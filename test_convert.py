import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path

from convert import ConversionError, Job, convert, find_jobs
from main import main

# Stand-in for hdrfix: copies the input to the output, fails on files containing "bad".
FAKE_HDRFIX = """import shutil, sys
src, dst = sys.argv[-2], sys.argv[-1]
if "bad" in src:
    sys.exit("decode error")
shutil.copyfile(src, dst)
"""


class ConvertTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.src = self.root / "NVIDIA"
        script = self.root / "fake_hdrfix.py"
        script.write_text(FAKE_HDRFIX)
        if os.name == "nt":
            self.hdrfix = self.root / "hdrfix.cmd"
            self.hdrfix.write_text(f'@"{sys.executable}" "{script}" %*\n')
        else:
            self.hdrfix = self.root / "hdrfix"
            self.hdrfix.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{script}" "$@"\n')
            self.hdrfix.chmod(self.hdrfix.stat().st_mode | stat.S_IEXEC)

    def tearDown(self):
        self._tmp.cleanup()

    def capture(self, game, name, content="data"):
        path = self.src / game / f"{game} Screenshot {name}.jxr"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path


class TestFindJobs(ConvertTestCase):
    def test_one_folder_per_game(self):
        self.capture("Cyberpunk 2077", "2026.08.30 - 01.20.38.07")
        self.capture("Stellar Blade", "2026.03.19 - 22.26.00.00")
        (self.src / "Desktop").mkdir()
        (self.src / "Stellar Blade" / "clip.mp4").write_text("")

        jobs, done = find_jobs(self.src)

        self.assertEqual(done, 0)
        self.assertEqual([job.game for job in jobs], ["Cyberpunk 2077", "Stellar Blade"])
        self.assertEqual(
            jobs[0].dst,
            self.src
            / "Cyberpunk 2077"
            / "PNG"
            / "Cyberpunk 2077 Screenshot 2026.08.30 - 01.20.38.07.png",
        )

    def test_skips_already_converted(self):
        src = self.capture("Cyberpunk 2077", "a")
        self.capture("Cyberpunk 2077", "b")
        (src.parent / "PNG").mkdir()
        (src.parent / "PNG" / (src.stem + ".png")).write_text("")

        jobs, done = find_jobs(self.src)
        self.assertEqual((len(jobs), done), (1, 1))

        jobs, done = find_jobs(self.src, overwrite=True)
        self.assertEqual((len(jobs), done), (2, 0))

    def test_dst_root(self):
        self.capture("Cyberpunk 2077", "a")
        dst = self.root / "out"

        jobs, _ = find_jobs(self.src, dst_root=dst)
        self.assertEqual(jobs[0].dst.parent, dst / "Cyberpunk 2077")

    def test_game_filters_are_case_insensitive(self):
        self.capture("Cyberpunk 2077", "a")
        self.capture("Desktop", "a")
        self.capture("Wingdk", "a")

        jobs, _ = find_jobs(self.src, games=["cyberpunk 2077"])
        self.assertEqual({job.game for job in jobs}, {"Cyberpunk 2077"})

        jobs, _ = find_jobs(self.src, exclude=["desktop", "WINGDK"])
        self.assertEqual({job.game for job in jobs}, {"Cyberpunk 2077"})

    def test_single_game_folder_as_root(self):
        self.capture("Cyberpunk 2077", "a")

        jobs, _ = find_jobs(self.src / "Cyberpunk 2077")
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].dst.parent, self.src / "Cyberpunk 2077" / "PNG")


class TestConvert(ConvertTestCase):
    def test_success_keeps_capture_date(self):
        src = self.capture("Cyberpunk 2077", "a")
        os.utime(src, (1_700_000_000, 1_700_000_000))
        job = Job("Cyberpunk 2077", src, src.parent / "PNG" / "a.png")

        convert(self.hdrfix, job)

        self.assertEqual(job.dst.read_text(), "data")
        self.assertEqual(job.dst.stat().st_mtime, 1_700_000_000)
        self.assertEqual(os.listdir(job.dst.parent), ["a.png"])

    def test_failure_leaves_nothing_behind(self):
        src = self.capture("Cyberpunk 2077", "bad")
        job = Job("Cyberpunk 2077", src, src.parent / "PNG" / "bad.png")

        with self.assertRaisesRegex(ConversionError, "decode error"):
            convert(self.hdrfix, job)
        self.assertEqual(os.listdir(job.dst.parent), [])


class TestCli(ConvertTestCase):
    def run_cli(self, *args):
        return main([str(self.src), "--hdrfix", str(self.hdrfix), *args])

    def test_full_run_then_resume(self):
        self.capture("Cyberpunk 2077", "a")
        self.capture("Forza Horizon 6", "a")

        self.assertEqual(self.run_cli("-j", "2"), 0)
        self.assertEqual(len(list(self.src.glob("*/PNG/*.png"))), 2)

        self.capture("Forza Horizon 6", "b")
        self.assertEqual(self.run_cli(), 0)
        self.assertEqual(len(list(self.src.glob("*/PNG/*.png"))), 3)

    def test_failures_set_exit_code(self):
        self.capture("Cyberpunk 2077", "a")
        self.capture("Cyberpunk 2077", "bad")

        self.assertEqual(self.run_cli(), 1)
        self.assertEqual(len(list(self.src.glob("*/PNG/*.png"))), 1)

    def test_dry_run_writes_nothing(self):
        self.capture("Cyberpunk 2077", "a")

        self.assertEqual(self.run_cli("--dry-run"), 0)
        self.assertEqual(list(self.src.glob("*/PNG")), [])

    def test_missing_source(self):
        self.assertEqual(main([str(self.root / "nope")]), 2)


if __name__ == "__main__":
    unittest.main()

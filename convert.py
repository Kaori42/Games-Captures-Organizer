import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

JXR_EXT = ".jxr"
PARTIAL_SUFFIX = ".partial.png"


@dataclass(frozen=True)
class Job:
    """A single JXR -> PNG conversion."""

    game: str
    src: Path
    dst: Path


class ConversionError(Exception):
    pass


def find_hdrfix(explicit=None):
    """
    Locates the hdrfix executable.

    Args:
        explicit (str, optional): Path given by the user, takes precedence.

    Returns:
        Path or None: The path of hdrfix, or None if it cannot be found.
    """
    if explicit:
        path = Path(explicit)
        return path if path.is_file() else None

    bundled = Path(__file__).resolve().parent / "hdrfix.exe"
    if bundled.is_file():
        return bundled

    found = shutil.which("hdrfix")
    return Path(found) if found else None


def _jxr_files(folder):
    return sorted(
        Path(entry.path)
        for entry in os.scandir(folder)
        if entry.is_file() and entry.name.lower().endswith(JXR_EXT)
    )


def _game_folders(src_root):
    """
    Yields (game_name, folder) pairs.

    NVIDIA stores captures as `<root>/<game>/<game> Screenshot <date>.jxr`.
    If the root itself contains JXR files (a single game folder was given),
    it is treated as one game.
    """
    if _jxr_files(src_root):
        yield src_root.name, src_root
    for entry in sorted(os.scandir(src_root), key=lambda e: e.name.lower()):
        if entry.is_dir() and not entry.name.startswith("."):
            yield entry.name, Path(entry.path)


def find_jobs(
    src_root,
    dst_root=None,
    subfolder="PNG",
    games=None,
    exclude=None,
    overwrite=False,
):
    """
    Lists the conversions to run.

    Args:
        src_root (str | Path): The NVIDIA captures folder (one sub-folder per game).
        dst_root (str | Path, optional): If set, PNGs go to `<dst_root>/<game>/`.
            Otherwise they go to `<game folder>/<subfolder>/`.
        subfolder (str): Name of the PNG sub-folder when `dst_root` is not set.
        games (list[str], optional): Only process these games (case-insensitive).
        exclude (list[str], optional): Skip these games (case-insensitive).
        overwrite (bool): Convert again even if the PNG already exists.

    Returns:
        tuple[list[Job], int]: The jobs to run and the number of already converted files.
    """
    src_root = Path(src_root)
    wanted = {g.lower() for g in games} if games else None
    excluded = {g.lower() for g in exclude} if exclude else set()

    jobs = []
    already_done = 0
    for game, folder in _game_folders(src_root):
        if wanted is not None and game.lower() not in wanted:
            continue
        if game.lower() in excluded:
            continue

        out_dir = Path(dst_root) / game if dst_root else folder / subfolder
        for src in _jxr_files(folder):
            dst = out_dir / (src.stem + ".png")
            if not overwrite and dst.exists():
                already_done += 1
                continue
            jobs.append(Job(game, src, dst))

    return jobs, already_done


def convert(hdrfix, job, extra_args=()):
    """
    Converts one JXR file to PNG with hdrfix.

    The PNG is written to a temporary file first and renamed once complete, so an
    interrupted run never leaves a truncated PNG that would be skipped next time.
    The PNG gets the same modification date as the JXR to keep date sorting right.

    Raises:
        ConversionError: If hdrfix fails.
    """
    job.dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = job.dst.with_name(job.dst.stem + PARTIAL_SUFFIX)

    try:
        proc = subprocess.run(
            [str(hdrfix), *extra_args, str(job.src), str(tmp)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
        )
        if proc.returncode != 0 or not tmp.is_file():
            lines = proc.stdout.strip().splitlines()
            reason = lines[-1] if lines else f"code de sortie {proc.returncode}"
            raise ConversionError(reason)

        os.replace(tmp, job.dst)
    finally:
        tmp.unlink(missing_ok=True)

    stat = job.src.stat()
    os.utime(job.dst, ns=(stat.st_atime_ns, stat.st_mtime_ns))

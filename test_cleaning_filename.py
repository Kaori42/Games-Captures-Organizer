from tests import RichTestRunner, unittest
from game_names import clean_filename

class TestCleanFilename(unittest.TestCase):
    def test_remove_dates(self):
        self.assertEqual(clean_filename("example_12_05_2020"), "example")

    def test_remove_version(self):
        self.assertEqual(clean_filename("example - 1.2.3.4 (beta)"), "example")

    def test_remove_underscores(self):
        self.assertEqual(clean_filename("example_file_name"), "example file name")

    def test_remove_extra_spaces(self):
        self.assertEqual(clean_filename("example   file"), "example file")

    def test_real_case1(self):
        self.assertEqual(
            clean_filename("STAR WARS Jedi_ Survivor™ 01_07_2023 23_45_37"),
            "STAR WARS Jedi Survivor™",
        )

    def test_only_number(self):
        self.assertEqual(clean_filename("1091500_20230927184252_1"), "1091500")

    def test_long_title(self):
        self.assertEqual(
            clean_filename(
                "Cyberpunk 2077 (C) 2020 by CD Projekt RED 18_12_2023 15_48_04"
            ),
            # I would really like it to only be "Cyberpunk 2077"
            "Cyberpunk 2077 (C) 2020 by CD Projekt RED",
        )


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner, verbosity=2)

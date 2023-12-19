from tests import RichTestRunner, unittest
from main import common_filename_part


class TestCommonFilenameParts(unittest.TestCase):
    def test_common_parts(self):
        self.assertEqual(
            common_filename_part(
                "C:/Users/proki/OneDrive/Dev/Games-Captures-Organizer/test_folder"
            ),
            [
                "Avatar Frontiers of Pandora™",
                "Cyberpunk 2077 (C) 2020 by CD Projekt RED",
                "Skull And Bones",
            ],
        )


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner, verbosity=2)
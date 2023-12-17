import unittest
from main import (
    clean_filename,
)
from rich.console import Console
from rich.traceback import install

install()  # Active les tracebacks riches


class RichTestResult(unittest.TextTestResult):
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.console = Console()
        self.success_count = 0

    def addSuccess(self, test):
        super().addSuccess(test)
        self.success_count += 1

    def addError(self, test, err):
        super().addError(test, err)
        self.console.print(f"❌ [red] ERROR[/red]: {test}")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.console.print(f"⚠️ [yellow] FAILURE[/yellow]: {test}")


class RichTestRunner(unittest.TextTestRunner):
    def _makeResult(self):
        return RichTestResult(self.stream, self.descriptions, self.verbosity)

    def run(self, test):
        result = self._makeResult()
        test(result)
        self.stream.flush()

        # Utilisation de l'objet result correctement initialisé
        total_tests = result.success_count + len(result.failures) + len(result.errors)
        if total_tests > 0:
            if result.success_count < total_tests:
                result.console.print(
                    f"❌ [red]{total_tests-result.success_count}/{total_tests} tests FAILED[/red]\n"
                    f"⚠️ [yellow] {result.success_count}/{total_tests} tests passed successfully[/yellow]"
                )
            else:
                result.console.print(
                    f"✅ [green]{result.success_count}/{total_tests} tests passed successfully[/green]"
                )

        # Afficher les détails des erreurs et des échecs
        for test, err in result.failures + result.errors:
            result.console.print(f"❌ Test Failed: {test}")
            result.console.print(err)

        return result


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
                "Cyberpunk 2077 (C) 2020 by CD Projekt RED 07_11_2023 22_19_28"
            ),
            # I would really like it to only be "Cyberpunk 2077"
            "Cyberpunk 2077 (C) 2020 by CD Projekt RED",
        )


# Ceci lance les tests lorsque le fichier est exécuté directement
if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner, verbosity=2)

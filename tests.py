import unittest
from rich.console import Console
from rich.traceback import install

install()  # Active les tracebacks riches


class RichTestResult(unittest.TextTestResult):
    """
    A subclass of `unittest.TextTestResult` that provides additional functionality for displaying test results with rich formatting.

    Attributes:
        console (Console): A console object from the `rich.console` module for rich formatting of test results.
        success_count (int): The number of successful tests.

    Args:
        stream (io.TextIOBase): The stream to write the test results to.
        descriptions (bool): Whether to include test descriptions in the output.
        verbosity (int): The verbosity level of the output.
    """

    def __init__(self, stream, descriptions, verbosity):
        """
        Initializes the `RichTestResult` instance.

        Args:
            stream (io.TextIOBase): The stream to write the test results to.
            descriptions (bool): Whether to include test descriptions in the output.
            verbosity (int): The verbosity level of the output.
        """
        super().__init__(stream, descriptions, verbosity)
        self.console = Console()
        self.success_count = 0

    def addSuccess(self, test):
        """
        Overrides the `addSuccess` method to increment the `success_count` field and call the parent method.

        Args:
            test (unittest.TestCase): The successful test case.
        """
        super().addSuccess(test)
        self.success_count += 1

    def addError(self, test, err):
        """
        Overrides the `addError` method to print an error message with rich formatting and call the parent method.

        Args:
            test (unittest.TestCase): The test case that encountered an error.
            err (tuple): The error information.
        """
        super().addError(test, err)
        self.console.print(f"❌ [red] ERROR[/red]: {test}")

    def addFailure(self, test, err):
        """
        Overrides the `addFailure` method to print a failure message with rich formatting and call the parent method.

        Args:
            test (unittest.TestCase): The test case that encountered a failure.
            err (tuple): The failure information.
        """
        super().addFailure(test, err)
        self.console.print(f"⚠️ [yellow] FAILURE[/yellow]: {test}")


class RichTestRunner(unittest.TextTestRunner):
    def _makeResult(self):
        return RichTestResult(self.stream, self.descriptions, self.verbosity)

    def run(self, test):
        """
        Execute the test cases and display the test results with rich formatting.

        Args:
            self (RichTestRunner): The instance of the RichTestRunner class.
            test (unittest.TestSuite): The test suite containing the test cases to be executed.

        Returns:
            RichTestResult: The object containing the test results, including the number of successful tests, failures, and errors.
        """
        result = self._makeResult()
        test(result)
        self.stream.flush()

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

        for test, err in result.failures + result.errors:
            result.console.print(f"❌ Test Failed: {test}")
            result.console.print(err)

        return result

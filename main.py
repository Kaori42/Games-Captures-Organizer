from gui import load_tk
from args import check_args, parse_args


def main():
    """
    Handles the command line arguments and starts the gui or the sorting operation.

    Calls the `check_args` function if the script is run with command line arguments.

    Calls the `build_gui` function if the script is run without command line arguments.
    """
    args = parse_args()

    if args:
        check_args(args)
    else:
        load_tk()


if __name__ == "__main__":
    main()

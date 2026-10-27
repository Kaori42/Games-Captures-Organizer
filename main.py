import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from colorama import Fore, Style, just_fix_windows_console
from tqdm import tqdm

from convert import ConversionError, convert, find_hdrfix, find_jobs

DEFAULT_SRC = Path.home() / "Videos" / "NVIDIA"
# hdrfix already spreads the tone mapping over all cores, but JXR decoding and PNG
# encoding are single-threaded, so a few files in parallel still pays off.
DEFAULT_JOBS = max(1, min(4, (os.cpu_count() or 2) // 2))


def color(text, fore):
    return fore + text + Style.RESET_ALL


def parse_args(argv):
    """
    Parses the command line. Everything after `--` is passed as-is to hdrfix.

    Returns:
        tuple[argparse.Namespace, list[str]]: The parsed arguments and the hdrfix options.
    """
    if "--" in argv:
        split = argv.index("--")
        argv, hdrfix_args = argv[:split], argv[split + 1 :]
    else:
        hdrfix_args = []

    parser = argparse.ArgumentParser(
        description="Convertit les captures NVIDIA HDR (.jxr) en PNG avec hdrfix.",
        epilog=(
            "Exemples :\n"
            "  python main.py\n"
            '  python main.py "D:\\Captures\\NVIDIA" --dst "D:\\Captures\\PNG"\n'
            '  python main.py --game "Cyberpunk 2077" -j 2 -- --tone-map hable'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "src",
        nargs="?",
        default=str(DEFAULT_SRC),
        help=f"Dossier des captures NVIDIA, un sous-dossier par jeu (défaut : {DEFAULT_SRC})",
    )
    parser.add_argument(
        "--dst",
        help="Dossier de sortie, les PNG vont dans <dst>/<jeu>/ "
        "(défaut : un sous-dossier dans chaque dossier de jeu)",
    )
    parser.add_argument(
        "--subfolder",
        default="PNG",
        help="Nom du sous-dossier de sortie quand --dst n'est pas fourni (défaut : PNG)",
    )
    parser.add_argument(
        "-g",
        "--game",
        action="append",
        help="Ne traiter que ce jeu (nom du dossier, répétable)",
    )
    parser.add_argument(
        "-x",
        "--exclude",
        action="append",
        help="Ignorer ce jeu (nom du dossier, répétable)",
    )
    parser.add_argument(
        "-j",
        "--jobs",
        type=int,
        default=DEFAULT_JOBS,
        help=f"Nombre de conversions en parallèle (défaut : {DEFAULT_JOBS})",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Reconvertir même si le PNG existe déjà",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Afficher ce qui serait converti sans rien faire",
    )
    parser.add_argument("--hdrfix", help="Chemin de hdrfix (défaut : hdrfix.exe du projet)")

    args = parser.parse_args(argv)
    if args.jobs < 1:
        parser.error("--jobs doit être >= 1")
    return args, hdrfix_args


def run(args, hdrfix_args):
    """
    Runs the conversions and returns the process exit code.
    """
    src = Path(args.src)
    if not src.is_dir():
        print(color(f"Erreur ❌ Le dossier source n'existe pas : {src}", Fore.RED))
        return 2

    hdrfix = find_hdrfix(args.hdrfix)
    if hdrfix is None and not args.dry_run:
        print(color("Erreur ❌ hdrfix introuvable, utilisez --hdrfix.", Fore.RED))
        return 2

    jobs, already_done = find_jobs(
        src,
        dst_root=args.dst,
        subfolder=args.subfolder,
        games=args.game,
        exclude=args.exclude,
        overwrite=args.overwrite,
    )

    if already_done:
        print(color(f"{already_done} capture(s) déjà convertie(s), ignorée(s).", Fore.CYAN))
    if not jobs:
        print(color("Rien à convertir ✅", Fore.GREEN))
        return 0

    if args.dry_run:
        for job in jobs:
            print(f"{job.src}\n  -> {job.dst}")
        print(color(f"{len(jobs)} capture(s) à convertir.", Fore.YELLOW))
        return 0

    print(
        color(
            f"Conversion de {len(jobs)} capture(s) "
            f"({len({job.game for job in jobs})} jeu(x), {args.jobs} en parallèle)...",
            Fore.YELLOW,
        )
    )

    failures = []
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        futures = {executor.submit(convert, hdrfix, job, hdrfix_args): job for job in jobs}
        try:
            with tqdm(total=len(jobs), unit="img", dynamic_ncols=True) as pbar:
                for future in as_completed(futures):
                    job = futures[future]
                    try:
                        future.result()
                    except (ConversionError, OSError) as error:
                        failures.append(job)
                        tqdm.write(color(f"❌ {job.src.name} : {error}", Fore.RED))
                    pbar.set_postfix_str(job.game, refresh=False)
                    pbar.update(1)
        except KeyboardInterrupt:
            executor.shutdown(wait=True, cancel_futures=True)
            print(color("\nInterrompu. Relancez la commande pour reprendre.", Fore.YELLOW))
            return 130

    converted = len(jobs) - len(failures)
    print(color(f"{converted} capture(s) convertie(s) ✅", Fore.GREEN))
    if failures:
        print(color(f"{len(failures)} échec(s) ❌", Fore.RED))
        return 1
    return 0


def main(argv=None):
    just_fix_windows_console()
    args, hdrfix_args = parse_args(sys.argv[1:] if argv is None else argv)
    return run(args, hdrfix_args)


if __name__ == "__main__":
    sys.exit(main())

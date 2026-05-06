import argparse
import os
from importlib.metadata import version
from pathlib import Path

from c2pie.signing import sign_file
from c2pie.utils.content_types import C2PA_ContentTypes

supported_extensions: list[str] = [_type.value for _type in C2PA_ContentTypes]


def parse_arguments() -> argparse.Namespace:
    global_parser = argparse.ArgumentParser(
        prog="c2pie",
        description=f"A program designed to embed C2PA Content Credentials"
        f"into files with supported extensions.\nCurrently, the "
        f"supported extensions are: {supported_extensions}.",
    )

    global_parser.add_argument("-V", "--version", action="version", version=f"c2pie {version('c2pie')}")

    subparsers = global_parser.add_subparsers(title="subcommands", help="commands")

    sign_parser = subparsers.add_parser("sign", help="embed c2pa signature into a file")

    sign_parser.add_argument(
        "--input_file",
        type=Path,
        help="path to the input file to sign.",
    )

    sign_parser.add_argument(
        "-o",
        "--output",
        dest="output_file",
        type=Path,
        default=None,
        help="optional path to save the signed file. If omitted, the program saves to 'signed_' + input_file.",
    )

    sign_parser.add_argument(
        "--tsa_url",
        type=str,
        default=None,
        help="RFC 3161 TSA URL for timestamping (e.g. http://timestamp.digicert.com). "
        "Falls back to C2PIE_TSA_URL env variable.",
    )

    sign_parser.add_argument(
        "--require_tsa",
        action="store_true",
        default=False,
        help="abort signing if no TSA URL is available.",
    )

    sign_parser.add_argument(
        "--tsa_log_dir",
        type=Path,
        default=None,
        help="directory to save TSA request/response DER files for debugging.",
    )

    sign_parser.set_defaults(func=sign)

    return global_parser.parse_args()


def sign(arguments: argparse.Namespace) -> None:
    input_file_path = arguments.input_file
    output_file_path = arguments.output_file
    tsa_url = arguments.tsa_url or os.getenv("C2PIE_TSA_URL")
    require_tsa = arguments.require_tsa or (os.getenv("C2PIE_TSA_REQUIRED", "").lower() == "true")
    tsa_log_dir = arguments.tsa_log_dir or os.getenv("C2PIE_TSA_LOG_DIR")

    sign_file(
        input_path=input_file_path,
        output_path=output_file_path,
        tsa_url=tsa_url,
        require_tsa=require_tsa,
        tsa_log_dir=tsa_log_dir,
    )


def main() -> None:
    arguments = parse_arguments()
    arguments.func(arguments)


if __name__ == "__main__":
    main()

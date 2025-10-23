import argparse
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
        "-m",
        "--manifest",
        dest="schema_filepath",
        type=Path,
        default=None,
        help="optional path to a the signature file. If omitted, the default signature is used.",
    )

    sign_parser.set_defaults(func=sign)
    return global_parser.parse_args()


def sign(arguments: argparse.Namespace) -> None:
    input_file_path = arguments.input_file
    output_file_path = arguments.output_file
    schema_file_path = arguments.schema_filepath

    # sign the provided file
    sign_file(
        input_path=input_file_path,
        output_path=output_file_path,
        schema_path=schema_file_path,
    )


def main() -> None:
    arguments = parse_arguments()
    arguments.func(arguments)


if __name__ == "__main__":
    main()

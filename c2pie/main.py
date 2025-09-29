import argparse
from pathlib import Path

from c2pie.signing import sign_file
from c2pie.utils.content_types import C2PA_ContentTypes

supported_extensions: list[str] = [_type.value for _type in C2PA_ContentTypes]


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="c2pie",
        description=f"A program designed to embed C2PA Content Credentials"
        f"into files with supported extensions.\nCurrently, the "
        f"supported extensions are: {supported_extensions}.",
    )
    parser.add_argument(
        "--input_file",
        type=Path,
        help="path to the input file to sign.",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_file",
        type=Path,
        default=None,
        help="optional path to save the signed file. If omitted, the program saves to 'signed_' + input_file.",
    )

    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    input_file_path = arguments.input_file
    output_file_path = arguments.output_file

    # sign the provided file
    sign_file(
        input_path=input_file_path,
        output_path=output_file_path,
    )


if __name__ == "__main__":
    main()

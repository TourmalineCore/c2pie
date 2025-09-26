import argparse
from enum import Enum
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


def ensure_path_correctness(file_path: Path) -> None:
    # check if input_file_path isn't a directory
    if file_path.is_dir():
        raise ValueError(f"The provided path is a directory, not a file: {file_path}.")

    # check if file has correct extension
    extension_of_input_file = file_path.suffix
    if extension_of_input_file not in supported_extensions:
        raise ValueError(
            f"The file has an incorrect extension: {extension_of_input_file}"
            f" Currently, only the following extensions are supported: {supported_extensions}.",
        )


def main() -> None:
    arguments = parse_arguments()
    input_file_path = arguments.input_file
    output_file_path = arguments.output_file

    # initial check if input_file_path exists
    if not input_file_path.exists():
        raise ValueError(f"Cannot find the provided path: {input_file_path}.")

    # check if arguments are correct
    ensure_path_correctness(input_file_path)
    if output_file_path:
        ensure_path_correctness(output_file_path)

    # fix output_file_path
    if not output_file_path:
        name_of_input_file = input_file_path.name
        output_file_path = input_file_path.with_name("signed_" + name_of_input_file)

    file_content_type: Enum = C2PA_ContentTypes(input_file_path.suffix)

    # sign the provided file
    sign_file(
        file_type=file_content_type,
        input_path=input_file_path,
        output_path=output_file_path,
    )


if __name__ == "__main__":
    main()

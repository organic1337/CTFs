#!/bin/python3
import argparse
from dataclasses import dataclass
from pathlib import Path

import pwn
from pwnlib.context import ContextType


@dataclass
class Arguments:
    shellcode_path: Path
    output_file: Path
    architecture: str
    endianness: str


def parse_args() -> Arguments:
    parser = argparse.ArgumentParser(description='Utility script for compiling assembly shellcodes')
    parser.add_argument('-a', '--arch', choices=ContextType.architectures, default='i386')
    parser.add_argument('-e', '--endianness', choices=ContextType.endiannesses, default='little')
    parser.add_argument('shellcode_path')
    parser.add_argument('-o', '--output_file')

    arguments = parser.parse_args()
    return Arguments(
        endianness=arguments.endianness,
        architecture=arguments.arch,
        shellcode_path=Path(arguments.shellcode_path),
        output_file=Path(arguments.output_file)
    )


def main() -> None:
    arguments = parse_args()
    with pwn.context.local(arch=arguments.architecture, endianness=arguments.endianness):
        assembled_shellcode = pwn.asm(arguments.shellcode_path.read_text())
        Path(arguments.output_file).write_bytes(assembled_shellcode)


if __name__ == '__main__':
    main()

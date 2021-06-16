#!/bin/python3
import argparse
from dataclasses import dataclass
from pathlib import Path

import pwn
import re
from pwnlib.context import ContextType


@dataclass
class Arguments:
    shellcode_path: Path
    output_file: Path
    architecture: str
    endianness: str
    bits: int


def parse_args() -> Arguments:
    parser = argparse.ArgumentParser(description='Utility script for compiling assembly shellcodes')
    parser.add_argument('-a', '--arch', choices=ContextType.architectures, default='i386')
    parser.add_argument('-e', '--endianness', choices=ContextType.endiannesses, default='little')
    parser.add_argument('shellcode_path')
    parser.add_argument('-o', '--output_file')
    parser.add_argument('-b', '--bits', type=int, default=32)

    arguments = parser.parse_args()
    return Arguments(
        bits=arguments.bits,
        endianness=arguments.endianness,
        architecture=arguments.arch,
        shellcode_path=Path(arguments.shellcode_path),
        output_file=Path(arguments.output_file),
    )


def get_assembly_code(source_file_path: Path) -> str:
    code = source_file_path.read_text()
    non_comment_lines = [line for line in code.splitlines() if not re.match(r'\s*;', line)]
    return '\n'.join(non_comment_lines)


def main() -> None:
    arguments = parse_args()
    with pwn.context.local(arch=arguments.architecture, endianness=arguments.endianness, bits=arguments.bits):
        assembly_code = get_assembly_code(arguments.shellcode_path)
        assembled_shellcode = pwn.asm(assembly_code)
        Path(arguments.output_file).write_bytes(assembled_shellcode)


if __name__ == '__main__':
    main()

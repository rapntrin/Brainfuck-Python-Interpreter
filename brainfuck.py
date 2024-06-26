# Brainfuck Interpreter
# Author: rapntrin
# Information on Brainfuck: https://wikipedia.org/wiki/Brainfuck

import math
import argparse
import os
import time

class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


getch = _Getch()

class BrainfuckError(Exception):
    def __init__(self, message):
        self.message = message

class Brainfuck:
    def __init__(self, *, code:str, memory:int = 30000, bits:int = 8, python:bool = False ,wrapping:bool = True, dynamic_memory:bool = True):
        self.code = code
        self.pointer = 0
        self.wrapping = wrapping
        self.python = python
        self.dynamic_memory = dynamic_memory
        self.memory = [0] * memory
        self.maxint = math.pow(2, bits) - 1
        self.output = ""
    
    def run(self):
        i = 0
        code = self.code
        time.sleep(1)
        # Repeat through the Code
        while i < len(code):
            i = self.execute(i)
        # Print the Output                                                                                                                                                                                          ", end="\r")
        print(self.output)
    def execute(self, codepointer):
        try:
            code = self.code
            # Check if codepointer is out of bounds
            if codepointer > len(code):
                return
            # > Increment Pointer
            if code[codepointer] == ">":
                self.pointer += 1
                if self.pointer > len(self.memory):
                    if self.dynamic_memory:
                        self.memory.append(0)
                    else:
                        self.pointer = len(self.memory)
            
            # < Decrement Pointer
            elif code[codepointer] == "<":
                self.pointer -= 1
                if self.pointer < 0:
                    self.pointer = 0
            
            # + Increment Value
            elif code[codepointer] == "+":
                self.memory[self.pointer] += 1
                if self.memory[self.pointer] > self.maxint:
                    if self.wrapping:
                        self.memory[self.pointer] = 0
                    else:
                        self.memory[self.pointer] = self.maxint
            
            # - Decrement Value
            elif code[codepointer] == "-":
                self.memory[self.pointer] -= 1
                if self.memory[self.pointer] < 0:
                    if self.wrapping:
                        self.memory[self.pointer] = self.maxint
                    else:
                        self.memory[self.pointer] = 0
            
            # . Print Value
            elif code[codepointer] == ".":
                # Print as ASCII
                if self.memory[self.pointer] == 127:
                    self.output = self.output[:-1]
                    print(self.output + " ", end="\r")
                elif self.memory[self.pointer] == 10:
                    self.output += "\n"
                    print(self.output, end="\r")
                else:
                    self.output += chr(self.memory[self.pointer])
                    print(self.output, end="\r")

            # , Read Value
            elif code[codepointer] == ",":
                self.memory[self.pointer] = ord(getch())
            
            # [ Execute Code until Value at Pointer is 0 ]
            elif code[codepointer] == "[":
                if self.memory[self.pointer] != 0:
                    codepointer += 1
                    start_loop = codepointer
                    while self.memory[self.pointer] > 0:
                        codepointer = start_loop
                        while code[codepointer] != "]":
                            if codepointer == len(code):
                                self.output = f"Syntax Error: Unmatched '[' found at position {codepointer}"
                                return len(code)
                            codepointer = self.execute(codepointer)
                else:
                    while code[codepointer] != "]":
                        codepointer += 1
                    codepointer += 1
                    print(f"{codepointer}/{len(code)}")
            
            # % Run Python Code
            elif code[codepointer] == "%":
                if self.python:
                    codepointer += 1
                    command = ""
                    while code[codepointer] != "%":
                        command += code[codepointer]
                        codepointer += 1
                    exec(command)

            return codepointer+1
        except:
            return codepointer+1
    
# Load code from file parameter
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str, help="Path to file containing Brainfuck code")
    parser.add_argument("--memory", type=int, default=30000, help="Memory size in bytes")
    parser.add_argument("--bits", type=int, default=8, help="Number of bits in memory")
    parser.add_argument("--allow-python", action="store_true", help="Allow Python code to be executed")
    args = parser.parse_args()
    
    # Check if file exists and ends with .bf
    if not os.path.exists(args.file): 
        raise BrainfuckError(f"File {args.file} does not exist")
    
    if not args.file.endswith(".bf"):
        raise BrainfuckError(f"File {args.file} is not a Brainfuck file")

    with open(args.file, "r") as f:
        code = f.read()

    # Run the Brainfuck code
    bf = Brainfuck(code=code, memory=30000, bits=8, python=args.allow_python)
    bf.run()
#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path
import argparse
import glob
from write_code import CodeWriter
from parser import *
from _constants import *

def main():
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument("path", type=str, help="vm file or folder")
    args = parser.parse_args()
    path = args.path

    if path.endswith(".vm"):    #file
        with CodeWriter(path[:-3] + ".asm") as cw:
            _translate_file(path, cw)

    elif path.endswith("/"):    #directory
        pass

def _translate_file(file_path, cw):
    filename= os.path.splitext(os.path.basename(file_path))
    cw.setFileName()            #cw.filename　書き込みファイル名
    print("書き込みファイル名：",cw.filename+".asm")
    with Parser(file_path) as ps:
        ps.advance()
        while ps.current_command != None:
            print(ps.current_command)
            if ps.commandType() == C_ARITHMETIC:
                cw.writeArithmetic(ps.arg1())
            elif ps.commandType() == C_PUSH:
                cw.writePushPop(ps.commandType(),ps.arg1() ,ps.arg2())
            elif ps.commandType() == C_POP:
                print("commandType()=", ps.commandType())
            ps.advance()

if __name__ == "__main__":
    main()

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
        if path.endswith("/"):
            path=path[:-1]
        with CodeWriter(path+"/"+os.path.basename(path)+".asm") as cw:
            files=glob.glob("%s/*" %path)
            print(files)
            for file in files:
                if file.endswith(".vm"):
                    _translate_file(file,cw)          

def _translate_file(file_path, cw):
    filename= os.path.splitext(os.path.basename(file_path))
    cw.setFileName()            #cw.filename　書き込みファイル名
    print("書き込みファイル名：",cw.filename+".asm")
    with Parser(file_path) as ps:
        ps.advance()
        while ps.current_command != None:
            print(ps.current_command,ps.commandType())
            if ps.commandType() == C_ARITHMETIC:
                cw.writeArithmetic(ps.arg1())
            elif ps.commandType() == C_PUSH:
                cw.writePushPop(ps.commandType(),ps.arg1(),ps.arg2())
            elif ps.commandType() == C_POP:
                cw.writePushPop(ps.commandType(),ps.arg1(),ps.arg2())
            elif ps.commandType() == C_LABEL:
                cw.writeLabel(ps.arg1())
            elif ps.commandType() == C_GOTO:
                cw.writeGoto(ps.arg1())
            elif ps.commandType() == C_IF:
                cw.writeIf(ps.arg1())
            elif ps.commandType() == C_FUNCTION:
                cw.writeFunction(ps.arg1(), ps.arg2())
            elif ps.commandType() == C_RETURN:
                cw.writeReturn()
            ps.advance()

if __name__ == "__main__":
    main()

import os.path
from _constants import *

class CodeWriter():
    def __init__(self, filepath):
        self.filepath = filepath
        self.label_num = 0

    def __enter__(self):
        self.f = open(self.filepath, "w")
        return self
    
    def __exit__(self, exception_type, exception_value, traceback):
        self.f.close()

    def setFileName(self):
        self.filename, _ = os.path.splitext(os.path.basename(self.filepath))

    def writeArithmetic(self, command):
        if command in ["add","sub", "and", "or"]:
            self._pop2M()
            self._writeCode("D=M")
            self._pop2M()
            if command == "add":
                self._writeCode("D=D+M")
            elif command == "sub":
                self._writeCode("D=M-D")
            elif command == "and":
                self._writeCode("D=D&M")
            elif command == "or":
                self._writeCode("D=D|M")
            self._pushD()

        elif command in ["neg", "not"]:
            self._writeCodes([
                "@SP",
                "A=M-1"
            ])
            if command == "neg":
                self._writeCode("M=-M")
            elif command == "not":
                self._writeCode("M=!M")

        elif command in ["eq", "gt", "lt"]:
            self._pop2M()
            self._writeCode("D=M")
            self._pop2M()
            l1 = self._getNewLabel()
            l2 = self._getNewLabel()
            if command == "eq":
                comp_type = "JEQ"
            elif command == "gt":
                comp_type = "JGT"
            elif command == "lt":
                comp_type = "JLT"
            self._writeCodes([
                "D=M-D",
                "@%s" %l1,
                "D;%s" %comp_type,
                "D=0",
                "@%s" %l2,
                "0;JMP",
                "(%s)" %l1,
                "D=-1",
                "(%s)" %l2
            ])
            self._pushD()
            

    def _pop2M(self):
        self._writeCodes([
            "@SP",
            "M=M-1",
            "A=M"
        ])

    def _pushD(self):
        self._writeCodes([
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1"
        ])

    def writePushPop(self, command, segment, index):
        index = int(index)
        if command == C_PUSH:
            if segment == "constant":
                self._writeCodes([
                    "@%d" % index,
                    "D=A",
                ])
                self._pushD()
                return
            elif segment in ["local", "argument", "this", "that"]:
                self._writePush2VirtualSegment(segment, index)
            elif segment in ["pointer", "temp"]:
                self._writePush2StaticSegment(segment, index)
            elif segment == "static":
                self._writeCodes([
                    "@%s.%d" %(self.filename, index),
                    "D=M"
                ])
                self._pushD()
        
        elif command == C_POP:
            if segment in ["local", "argument", "this", "that"]:
                self._writePopFromVirtualSegment(segment, index)
            elif segment in ["temp", "pointer"]:
                self._writePopFromStaticSegment(segment, index)
            elif segment == "static":
                self._pop2M()
                self._writeCodes([
                    "D=M",
                    "@%s.%d" %(self.filename, index)
                ])
                self._writeCode("M=D")
                    
    def _writePush2VirtualSegment(self, segment, index):
        if segment == "local":
            register_name = "LCL"
        elif segment == "argument":
            register_name = "ARG"
        elif segment == "this":
            register_name = "THIS"
        elif segment == "that":
            register_name = "THAT"
        self._writeCodes([
            "@%s" % register_name,
            "A=M"
        ])
        for i in range(index):
            self._writeCode("A=A+1")
        self._writeCode("D=M")
        self._pushD()
    
    def _writePush2StaticSegment(self, segment, index):
        if segment == "temp":
            base_address = TEMP_BASE_ADDRESS
        elif segment == "pointer":
            base_address = POINTER_BASE_ADDRESS
        self._writeCodes([
            "@%d" % base_address
        ])
        for i in range(index):
            self._writeCode("A=A+1")
        self._writeCode("D=M")
        self._pushD()
 
    def _writePopFromVirtualSegment(self, segment, index):
        if segment == "local":
            register_name = "LCL"
        elif segment == "argument":
            register_name = "ARG"
        elif segment == "this":
            register_name = "THIS"
        elif segment == "that":
            register_name = "THAT"
        self._pop2M()
        self._writeCodes([
            "D=M",
            "@%s" %register_name,
            "A=M"
        ])
        for i in range(index):
            self._writeCode("A=A+1")
        self._writeCode("M=D")
        return

    def _writePopFromStaticSegment(self, segment, index):
        if segment == "pointer":
            base_address = POINTER_BASE_ADDRESS
        elif segment == "temp":
            base_address = TEMP_BASE_ADDRESS
        self._pop2M()
        self._writeCodes([
            "D=M",
            "@%d" %base_address
        ])
        for i in range(index):
            self._writeCode("A=A+1")
        self._writeCode("M=D")
        return

    def _writeCode(self, code):
        self.f.write(code + "\n")

    def _writeCodes(self, codes):
        self._writeCode("\n".join(codes))

    def _getNewLabel(self):
        self.label_num += 1
        return "LABEL" + str(self.label_num)


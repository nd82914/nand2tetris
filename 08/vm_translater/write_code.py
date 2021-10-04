import os.path
from _constants import *

class CodeWriter():
    def __init__(self, filepath):
        self.filepath = filepath
        self.label_num = 0
        self.return_address_num = 0

    def __enter__(self):
        self.f = open(self.filepath, "w")
        self._writeInit()
        return self
    
    def __exit__(self, exception_type, exception_value, traceback):
        self.f.close()

    def setFileName(self):
        self.filename, _ = os.path.splitext(os.path.basename(self.filepath))

    def _writeInit(self):
        self._writeCodes([
            "@256",
            "D=A",
            "@SP",
            "M=D"
        ])
        self.writeCall("Sys.init",0)

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
            l1 = self._getIfLabel()
            l2 = self._getIfLabel()
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

    def writeLabel(self, label):
        self._writeCode("(%s)" %label)

    def writeGoto(self, label):
        self._writeCodes([
            "@%s" % label,
            "0;JMP"
        ])

    def writeIf(self, label):
        self._pop2M()
        self._writeCodes([
            "D=M",
            "@%s" % label,
            "D;JNE"
        ])

    def writeFunction(self, function_name, num_locals):
        num_locals = int(num_locals)
        self._writeCodes([
            "(%s)" % function_name,
            "D=0"
        ])
        for i in range(num_locals):
            self._pushD()
            
        self.current_function_name=function_name

    def writeCall(self, function_name, num_args):
        ra=self._getReturnAddressLabel()#push returnAddress
        self._writeCodes([
            "@%s" %ra,      #push return address
            "D=A"
        ])
        self._pushD()       
        self._writeCodes([  #push LCL
            "@LCL",
            "D=M"
        ])
        self._pushD()
        self._writeCodes([  #push ARG
            "@ARG",
            "D=M"
        ])
        self._pushD()
        self._writeCodes([  #push This
            "@THIS",
            "D=M"
        ])
        self._pushD()
        self._writeCodes([  #push That
            "@THAT",
            "D=M"
        ])
        self._pushD()
        self._writeCodes([  #ARG=SP-n-5
            "@SP",
            "D=M",
            "@5",
            "D=D-A",
            "@%d" % int(num_args),
            "D=D-A",
            "@ARG",
            "M=D"
        ])
        self._writeCodes([  #LCL=SP
            "@SP",
            "D=M",
            "@LCL",
            "M=D"
        ]) 
        self._writeCodes([   
            "@%s" % function_name ,  #gotof
            "0;JMP",
            "(%s)" % ra     #define label
        ])
        
    def writeReturn(self):
        self._writeCodes([
            "@LCL",
            "D=M",
            "@R13",
            "M=D",          #FRAME(R13)=@LCL
            "@5",
            "D=A",
            "@R13",
            "A=M-D",
            "D=M",
            "@R14",
            "M=D"           #RET(@R14)=FRAME-5
        ])
        self._pop2M()       #戻り値をpop
        self._writeCodes([
            "D=M",
            "@ARG",         #A=2
            "A=M",          #A=M[2](ARG)
            "M=D" ,          #M[M[2]](ARG*)=戻り値

            "@ARG",
            "D=M",
            "@SP",
            "M=D+1",        #SP=ARG+1

            "@R13",
            "AM=M-1",       #A=FRAME-1, R13=FRAME-1
            "D=M",
            "@THAT",
            "M=D",          #THAT=*(FRAME-1)
            
            "@R13",
            "AM=M-1",       #A=FRAME-2, R13=FRAME-2
            "D=M",
            "@THIS",
            "M=D",          #THIS=*(FRAME-2)

            "@R13",
            "AM=M-1",       #A=FRAME-3, R13=FRAME-3
            "D=M",
            "@ARG",
            "M=D",          #ARG=*(FRAME-3)
            
            "@R13",
            "AM=M-1",       #A=FRAME-4, R13=FRAME-4
            "D=M",
            "@LCL",
            "M=D",          #LCL=*(FRAME-4)

            "@R14",
            "A=M",
            "0;JMP"         #goto RET
        ])

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

    def _getIfLabel(self):
        self.label_num += 1
        return "IF_LABEL" + str(self.label_num)

    def _getReturnAddressLabel(self):
        self.return_address_num += 1
        return "RETURN_ADDRESS" + str(self.return_address_num)
import re
from _constants import *

A_cp = re.compile(r"@([0-9a-zA-Z_\.\$:]+)")
L_cp = re.compile(r"\(([0-9a-zA-Z_\.\$:]+)\)")
#(?:・・・)?→0回以上の（AorMorD)）,(()=)→("xx=","xx"), (?:()=)→("xx")
#[^;]+→コロン以外の1文字以上の文字列　xyz;yyy→xyz
C_cp = re.compile(r"(?:(A?M?D?)=)?([^;]+)(?:;(.+))?")
 

        

class Parser():
    
    def __init__(self,file_path):
        self.current_command = ""
        self.file_path=file_path
        self.rf=None

    def __enter__(self):
        #ここで返されるオブジェクトは、with HackParcer() as ** において変数**を参照することで使用できるHackParcerインスタンスとなる
        self.rf=open(self.file_path)
        return self #with HackParser() as hp のhpにselfが代入される

    def __exit__(self,exc_type, exc_value, traceback):
        self.rf.close()
        
    def hasMoreCommands(self):
        if (self.current_command) == None:
            return False
        else:
            return True
        #入力にまだコマンドが存在するかBool型で戻り値を返す。

    def advance(self):
        while True:
            line = self.rf.readline()
            if not line:
                self.current_command = None
                return self.current_command

            elif line:
                line = line.rstrip().lstrip()
                comment_i = line.find("//")
                if comment_i != -1:
                    line = line[:comment_i]
                else:
                    line = line

                if line != "":
                    self.current_command = line.split()
                    return self.current_command

    def commandType(self):
        if self.current_command[0] == "push":
            return C_PUSH
        if self.current_command[0] == "pop":
            return C_POP
        if self.current_command[0] == "label":
            return C_LABEL
        if self.current_command[0] == "goto":
            return C_GOTO
        if self.current_command[0] == "if-goto":
            return C_IF
        if self.current_command[0] == "function":
            return C_FUNCTION
        if self.current_command[0] == "return":
            return C_RETURN
        if self.current_command[0] == "call":
            return C_CALL
        if self.current_command[0] in ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]:
            return C_ARITHMETIC

    def arg1(self):
        if self.commandType() == C_ARITHMETIC:
            return self.current_command[0]
        else:
            return self.current_command[1]

    def arg2(self):
        if self.commandType() in [C_PUSH, C_POP, C_FUNCTION, C_CALL]:
            return self.current_command[2]



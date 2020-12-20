import re
A_cp = re.compile(r"@([0-9a-zA-Z_\.\$:]+)")
L_cp = re.compile(r"\(([0-9a-zA-Z_\.\$:]+)\)")
#(?:・・・)?→0回以上の（AorMorD)）,(()=)→("xx=","xx"), (?:()=)→("xx")
#[^;]+→コロン以外の1文字以上の文字列　xyz;yyy→xyz
C_cp = re.compile(r"(?:(A?M?D?)=)?([^;]+)(?:;(.+))?")
 

        

class HackParser():
    def __init__(self,asm_file_path):
        self.current_command = None
        self.asm_file_path=asm_file_path
        self.rf=None

    def __enter__(self):
        open(self.asm_file_path, "r")
        #ここで返されるオブジェクトは、with HackParcer() as ** において変数**を参照することで使用できるHackParcerインスタンスとなる
        self.rf=open(self.asm_file_path)
        return self #with HackParser() as hp のhpにselfが代入される

    def __exit__(self,exc_type, exc_value, traceback):
        self.rf.close()
        
    def hasMoreCommands(self):
        if (self.current_command) == "":
            return False
        else:
            return True
        #入力にまだコマンドが存在するかBool型で戻り値を返す。

    def advance(self):
        self.current_command = self.rf.readline().replace("\n"," ")
        return
        #if hasMoreCommand==TRUE then 入力から次のコマンドを読み、現在のコマンドにする。

    def commandType(self):
        command = self.current_command.replace(" ","")
        command = re.sub(r"//.*","",command)
        A_type = A_cp.match(command)
        L_type = L_cp.match(command)
        C_type = C_cp.match(command)
        #print(hp.current_command)
        #print(A_type)
        #print(A_type.group())
        if A_type:
            return "A", A_type, A_type.groups()
        elif L_type:
            return "L", L_type, L_type.groups()
        elif C_type:
            return "C", C_type, C_type.groups()
        else:
            return None

    
    def symbol(self):
        if self.commandType() != None:
            if self.commandType()[0] == "A" or self.commandType()[0] =="L":
                return(self.commandType()[2][0])
            else:
                return
        else:
            return

    def dest(self):
        if self.commandType() != None:
            if self.commandType()[0] == "C":
                return(self.commandType()[2][0])
            else:
                return
        else:
            return

    def comp(self):
        if self.commandType() != None:
            if self.commandType()[0] == "C":
                return(self.commandType()[2][1])
            else:
                return
        else:
            return

    def jump(self):
        if self.commandType() != None:
            if self.commandType()[0] == "C":
                return(self.commandType()[2][2])
            else:
                return
        else:
            return


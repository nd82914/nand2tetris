import argparse
import os.path
from hack_parser import *
from hack_code import *
from hack_symboltb import *

def main():
    #コマンドラインオプション　paser.pyとは無関係なので注意
    parser = argparse.ArgumentParser(description="assemble file to binary file")
    parser.add_argument("asm_file",metavar="filepath",type=str,help="assembly file path")
    args=parser.parse_args()
    asm_file = args.asm_file
    save_file = os.path.splitext(asm_file)[0]+".hack"
    print(os.path.splitext(asm_file))
    with open(save_file, "w") as wf:
    #with を用いてクラスを呼び出すと、クラスの__enter__(),__exit__()関数を前処理、後処理として実行する
        with HackParser(asm_file) as hp:
            st = SymbolTable()
            Nrom=0
            while hp.hasMoreCommands() == True:
                hp.advance()
                if hp.commandType() != None:
                    if hp.commandType()[0] == "L":
                        if not st.contains(hp.symbol()):
                            st.addEntry(hp.symbol(),Nrom)
                        else:
                            print("error")
                    else:
                        Nrom = Nrom+1
            print("SymbolTable=",st.symbols)

            #2回目読み込み
        with HackParser(asm_file) as hp:
            i=0
            while hp.hasMoreCommands() == True:
                hp.advance()
                print("current command:", hp.current_command)
                print(hp.commandType())
                #print(hp.symbol())
                if hp.commandType() != None:
                    if hp.commandType()[0] == "A": #Aコマンド
                        if re.fullmatch(r"[0-9]+",hp.symbol()):
                            #hp.symbol()が数値のみの場合Aコマンドは整数をあつかう
                            A=re.fullmatch(r"([0-9]+)",hp.symbol()).group()
                            #A=2 以下は0000000000000010を書き込む
                            wf.write((str(format(int(A),'b'))).zfill(16)+"\n")

                        elif st.contains(hp.symbol()):
                            A=st.symbols[hp.symbol()]
                            print(A)
                            wf.write((str(format(int(A),'b'))).zfill(16)+"\n")
                        elif not st.contains(hp.symbol()):
                            print("notcontains",hp.symbol())
                            st.addEntry(hp.symbol(),16+i) #RAMの16までは定義済みシンボル
                            A=st.symbols[hp.symbol()]
                            wf.write((str(format(int(A),'b'))).zfill(16)+"\n")
                            i=i+1

                            #hp.symbol()が数値のみでない場合、Aコマンドはシンボルを扱う
                            print(hp.symbol())
                    elif hp.commandType()[0] == "L":
                        pass
                    elif hp.commandType()[0] == "C":
                        print(hp.dest(),hp.comp(),hp.jump())
                        print(dest(hp.dest()),comp(hp.comp()),jump(hp.jump()))
                        wf.write("111"+comp(hp.comp())+dest(hp.dest())+jump(hp.jump())+"\n")
                    else:
                        pass
                else:
                    pass

            print(st.symbols)







if __name__ == "__main__":
    main()

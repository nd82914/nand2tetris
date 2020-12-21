import os.path

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
        if command in ["add","sub"]:
            pass


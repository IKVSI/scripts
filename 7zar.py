#!/usr/bin/python3

import sys
import os
import subprocess
from pathlib import Path
from PySide6.QtWidgets import (
    QLineEdit,
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QCheckBox,
    QPushButton
)
from pydantic import SecretStr
#from PySide6.QtGui import QFontMetricsF

def writeblock(title : str, text : str) -> str:
    textlist = text.split('\n')
    maxlen = max((max(len(i) for i in textlist), 76))
    newlist = (f"| {i}{' '*(maxlen-len(i))} |" for i in textlist)
    title = f"{' ' * ((maxlen-len(title))//2 - 1)}{title}"
    return "{}\n{}\n{}\n{}\n{}\n".format(
        '-'*(maxlen + 4),
        f"| {title}{' '*(maxlen-len(title))} |",
        '-'*(maxlen + 4),
        '\n'.join(newlist),
        '-'*(maxlen + 4)
    )

class Password(QWidget):
    def __init__(self, path):
        self.app = QApplication(sys.argv)
        self.password = SecretStr("")
        super().__init__()
        self.setWindowTitle("Password")
        self.setLayout(QVBoxLayout())
        #self.layout().setAlignment()
        self.label = QLabel(f"Do you need password for ({path})?")
        self.edit = QLineEdit()
        self.edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.checkbox = QCheckBox("show password")
        self.checkbox.stateChanged.connect(self.openPassword)
        self.button = QPushButton("Send")
        self.edit.returnPressed.connect(self.button.click)
        self.button.clicked.connect(self.savePassword)
        for widget in (
            self.label,
            self.edit,
            self.checkbox,
            self.button
        ):
            self.layout().addWidget(widget)

    def openPassword(self, state):
        if state:
            self.edit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.edit.setEchoMode(QLineEdit.EchoMode.Password)
    
    def savePassword(self):
        self.password = SecretStr(self.edit.text())
        self.close()

    def getPassword(self):
        self.show()
        self.app.exec()
        return self.password



def createarchive(archname: Path, files: tuple[Path], password: SecretStr):
    print(f"Archive name: ({archname})")
    print("Have password: {}".format("Yes" if password else "No"))
    print("Add paths:\n    {}".format("\n    ".join(str(i) for i in files)))
    if password:
        os.system(
            subprocess.list2cmdline(
                [
                    "7z",
                    "a",
                    "-t7z",
                    "-mx=9",
                    "-mhe=on",
                    "-snl",
                    "-v4g",
                    f"-p{password.get_secret_value()}",
                    str(archname),
                    *(str(i) for i in files)
                ]
            )
        )
    

def main(argv : list[str] = sys.argv):
    if len(argv) == 1:
        raise FileNotFoundError("No file to extract!!!")
    argv = tuple(Path(i).resolve() for i in argv[1:])
    for i in argv:
        if not i.exists():
            raise FileNotFoundError(f"File or folder ({i}) not found!")
    archname = argv[0].with_name("archive.7z") 
    if len(argv) == 1:
        folder = argv[0]
        if folder.exists():
            argv = tuple(i for i in folder.iterdir())
        archname = folder.with_suffix(".7z")
    password = Password(archname).getPassword()
    createarchive(archname, argv, password)

if __name__ == "__main__":
    main()
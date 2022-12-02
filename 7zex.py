#!/usr/bin/python3

import sys
import subprocess
import os
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

class Password(QWidget):
    def __init__(self, path):
        self.app = QApplication(sys.argv)
        self.password = SecretStr("")
        super().__init__()
        self.setWindowTitle("Password")
        self.setLayout(QVBoxLayout())
        #self.layout().setAlignment()
        self.label = QLabel(f"Need password for ({path}):")
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

def run(command: list[str], text=True) -> subprocess.Popen:
    return subprocess.Popen(
        command,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        stdin = subprocess.PIPE,
        text = text
    )

def checkPassword(archivepath: Path) -> SecretStr | None:
    password = None
    with run(
        [
            "7z",
            "l",
            f"{archivepath}"
        ],
        text = False
    ) as ex:
        out, err = ex.communicate(b"TEST\n")
        err = err.decode("utf-8")
        if "Cannot open encrypted archive. Wrong password?" in err:
            password = Password(archivepath).getPassword()
    return password

def extractzip(archivepath: Path, folderpath: Path, password: SecretStr):
    with run(
        [
            "unzip",
            "-d",
            str(folderpath),
            str(archivepath)
        ]
    ) as ex:
        out, err = ex.communicate("\n" if password is None else f"{password.get_secret_value()}\n")
        sys.stdout.write(writeblock("unzip STDOUT", out))
        if err:
            sys.stderr.write(writeblock("unzip STDERR", err))

def extract(archivepath: Path, password: SecretStr):
    folderpath = archivepath
    if folderpath.suffix:
        if folderpath.suffix[1:].isdigit():
            folderpath = folderpath.with_suffix('')
        folderpath  = folderpath.with_suffix('')
    else:
        folderpath = folderpath.with_suffix('.d')
    if archivepath.suffix == ".zip":
        return extractzip(
            archivepath,
            folderpath,
            password
        )
    if password:
        os.system(subprocess.list2cmdline(
            [
                "7z",
                "x",
                "-bsp1",
                f"-p{password.get_secret_value()}",
                f"-o{folderpath}",
                f"{archivepath}"
            ]
        ))
    else:
        os.system(subprocess.list2cmdline(
            [
                "7z",
                "x",
                "-bsp1",
                f"-o{folderpath}",
                f"{archivepath}"
            ]
        ))

def main(argv : list[str] = sys.argv):
    if len(argv) == 1:
        raise FileNotFoundError("No file to extract!!!")
    archivepath = Path(argv[1]).resolve()
    if archivepath.is_file():
        password = checkPassword(archivepath)
        extract(archivepath, password)
    else:
        raise FileNotFoundError(f"No file \"{archivepath}\" !!!")
        

if __name__ == "__main__":
    main()
## Evet / Hayır onay kutusu ##
from PySide6.QtWidgets import QApplication, QMessageBox


def onay(msj, parent=None):
    # Açık pencereye bağlı açılır: Mac'te ayrı bir masaüstü alanına geçip panelin kaybolmasını önler
    mesaj=QMessageBox(parent or QApplication.activeWindow())
    mesaj.setIcon(QMessageBox.Information)
    mesaj.setWindowTitle("Onay")
    mesaj.setText(msj)
    mesaj.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
    mesaj.setEscapeButton(QMessageBox.No)
    mesaj.button(QMessageBox.Yes).setText("Evet")
    mesaj.button(QMessageBox.No).setText("Hayır")
    return mesaj.exec()

## Klavye kısayolları ##
# Mac'te Ctrl yerine Cmd (⌘) kullanılır; Qt bunu kendisi çevirir.
#   Ctrl+1 ... Ctrl+9  menüdeki bölümler (yukarıdan aşağıya)
#   Ctrl+F             açık sayfadaki arama kutusu (yoksa Kitap Listesi araması)
#   Kitap Kayıt: Ctrl+N yeni kitap, Ctrl+S kaydet, Esc vazgeç

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QLineEdit
from PySide6.QtGui import QShortcut

ARAMA = "arama_kutusu"      # arama kutularına verilen özellik adı


def arama_kutusu_yap(alan):
    """Ctrl+F ile odaklanılacak arama kutusu olarak işaretler."""
    alan.setProperty(ARAMA, True)
    return alan


def kisayol(tus, hedef, islev):
    """Pencerenin her yerinde çalışır; hedef bileşen görünmüyorsa (ör. başka sekme açıkken) devre dışıdır."""
    return QShortcut(QKeySequence(tus), hedef, islev, context=Qt.WindowShortcut)


def metin(tus):
    """Araç ipuçlarında gösterilecek, sisteme uygun yazım (Mac'te ⌘S, Windows'ta Ctrl+S)."""
    return QKeySequence(tus).toString(QKeySequence.NativeText)


def panele_kur(panel, sekmeler, liste_sayfasi, liste_aramasi):
    """Menü ve arama kısayolları: panelin her yerinde çalışır."""
    for i in range(min(sekmeler.count(), 9)):
        kisayol(f"Ctrl+{i + 1}", panel, lambda i=i: sekmeler.setCurrentIndex(i))

    def ara():
        sayfa = sekmeler.currentWidget()
        for alan in sayfa.findChildren(QLineEdit):
            if alan.property(ARAMA) and alan.isVisible():
                break
        else:
            sekmeler.setCurrentWidget(liste_sayfasi)
            alan = liste_aramasi
        alan.setFocus(Qt.ShortcutFocusReason)
        alan.selectAll()

    kisayol(QKeySequence.Find, panel, ara)

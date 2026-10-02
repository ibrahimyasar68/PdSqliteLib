## .ui ve .qrc dosyalarını Python dosyalarına dönüştürme ##
# Kullanım: proje klasöründen  .venv/bin/python scripts/convertFiles.py
# pyuic5 / pyrcc5 bu betiği çalıştıran Python'un yanında (sanal ortamda) aranır; ortamı etkinleştirmek gerekmez.
import os
import shutil
import subprocess
import sys

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def arac(ad):
    yol = os.path.join(os.path.dirname(sys.executable), ad)
    return yol if os.path.exists(yol) or os.path.exists(yol + ".exe") else (shutil.which(ad) or ad)


## Resimler: pyrcc5 dosya yollarını .qrc dosyasının bulunduğu klasöre göre çözer
subprocess.run([arac("pyrcc5"), "media.qrc", "-o", os.path.join("..", "bforms", "media_rc.py")],
               check=True, cwd=os.path.join(KOK, "media"))
print("media/media.qrc başarıyla dönüştürüldü.")

## Arayüzler: --import-from ile kaynak dosyası "from bforms import media_rc" olarak içe aktarılır
for ad in ("library", "login", "guest"):
    subprocess.run([arac("pyuic5"), "--import-from=bforms", f"cuis/{ad}.ui", "-o", f"bforms/{ad}_py.py"],
                   check=True, cwd=KOK)
    print(f"cuis/{ad}.ui başarıyla dönüştürüldü.")

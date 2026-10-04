## .ui ve .qrc dosyalarını Python dosyalarına dönüştürme ##
# Kullanım: proje klasöründen  .venv/bin/python scripts/convertFiles.py
# pyside6-uic / pyside6-rcc bu betiği çalıştıran Python'un yanında (sanal ortamda) aranır; ortamı etkinleştirmek gerekmez.
import os
import shutil
import subprocess
import sys

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def arac(ad):
    yol = os.path.join(os.path.dirname(sys.executable), ad)
    return yol if os.path.exists(yol) or os.path.exists(yol + ".exe") else (shutil.which(ad) or ad)


## Resimler: pyside6-rcc dosya yollarını .qrc dosyasının bulunduğu klasöre göre çözer
subprocess.run([arac("pyside6-rcc"), "media.qrc", "-o", os.path.join("..", "bforms", "media_rc.py")],
               check=True, cwd=os.path.join(KOK, "media"))
print("media/media.qrc başarıyla dönüştürüldü.")

## Arayüzler: --absolute-imports ile kaynak dosyası proje köküne göre içe aktarılır
for ad in ("login",):        # paneller kodla kurulur (acodes/panel.py); yalnızca giriş ekranı .ui
    subprocess.run([arac("pyside6-uic"), "--absolute-imports", "--python-paths", KOK, f"cuis/{ad}.ui",
                    "-o", f"bforms/{ad}_py.py"],
                   check=True, cwd=KOK)
    # .qrc media/ klasöründe, üretilen kaynak dosyası ise bforms/ altında: içe aktarma satırı ona göre düzeltilir
    yol = os.path.join(KOK, "bforms", f"{ad}_py.py")
    with open(yol, encoding="utf-8") as f:
        kod = f.read()
    with open(yol, "w", encoding="utf-8") as f:
        f.write(kod.replace("import media.media_rc", "import bforms.media_rc  # noqa: F401  (Qt kaynakları)"))
    print(f"cuis/{ad}.ui başarıyla dönüştürüldü.")

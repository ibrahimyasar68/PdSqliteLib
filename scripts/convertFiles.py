## .ui ve .qrc dosyalarını Python dosyalarına dönüştürme ##
# Kullanım: sanal ortam etkinken proje klasöründen  python scripts/convertFiles.py
import subprocess

## Resim Dönüştürme

sfile="media/media.qrc"
tfile="bforms/media_rc.py"
# pyrcc5 dosya yollarını .qrc dosyasının bulunduğu klasöre göre çözer
command2 = ["pyrcc5", "media.qrc", "-o", "../"+tfile]
subprocess.run(command2, check=True, cwd="media")
print(f"{sfile} başarıyla dönüştürüldü.")


#  ui dosyalarını py dosyalarına dönüştürme  ###
ui_files = [
    "cuis/library.ui",
    "cuis/login.ui",
    "cuis/user.ui",
    "cuis/guest.ui",
]

for ui_file in ui_files:
    py_file = "bforms/{}.py".format(ui_file.split("/")[-1].replace('.ui','_py'))
    # --import-from: kaynak dosyası "from bforms import media_rc" olarak içe aktarılsın
    command = ["pyuic5", "--import-from=bforms", ui_file, "-o", py_file]
    try:
        subprocess.run(command, check=True)
        print(f"{ui_file} başarıyla dönüştürüldü.")
    except subprocess.CalledProcessError:
        print(f"{ui_file} dönüştürülürken bir hata oluştu.")

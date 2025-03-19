import subprocess



## Resim Dönüştürme

sfile="media/media.qrc"
tfile="bforms/media_rc.py"
command2 = ["pyrcc5", sfile, "-o", tfile]
subprocess.run(command2, check=True)
print(f"{sfile} başarıyla dönüştürüldü.")




#  ui dosyalarını py dosyalarına dönüştürme  ###
ui_files = [
    "cuis/library.ui",
    "cuis/login.ui",
    "cuis/user.ui",
    "cuis/user2.ui",
    "cuis/guest.ui",  
]

for ui_file in ui_files:
    py_file = "bforms/{}.py".format(ui_file.split("/")[-1].replace('.ui','_py'))
    command = ["pyuic5", ui_file, "-o", py_file]
    try:
        subprocess.run(command, check=True)
        print(f"{ui_file} başarıyla dönüştürüldü.")
    except subprocess.CalledProcessError:
        print(f"{ui_file} dönüştürülürken bir hata oluştu.")





# resim dönüştürme  = pyrcc5 -o ImageRestorant_rc.py ImageRestorant.qrc
# demoya donuştürme = pyinstaller --onefile --icon=restorant.ico frmGiris.py
# demoya donuştürme = pyinstaller --onefile --icon=restorant.ico --noconsole frmGiris.py
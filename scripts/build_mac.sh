#!/bin/zsh
## macOS için PdSqliteLib.app oluşturma ##
# Kullanım: ./scripts/build_mac.sh   (proje klasöründen)
# Çıktı: dist/PdSqliteLib.app
# Not: data/DBL_Kayit.db o anki haliyle pakete eklenir ve uygulamanın
#      ilk açılışında ~/Library/Application Support/PdSqliteLib/ altına kopyalanır.

set -e
cd "$(dirname "$0")/.."

if [ ! -x .venv/bin/python ]; then
    python3 -m venv .venv
fi
.venv/bin/pip install -q -r requirements.txt pyinstaller pillow

.venv/bin/pyinstaller main.py \
    --name PdSqliteLib \
    --windowed \
    --noconfirm \
    --clean \
    --icon "$PWD/media/family.ico" \
    --osx-bundle-identifier com.pdsqlitelib.app \
    --add-data "$PWD/data/DBL_Kayit.db:data" \
    --workpath build/pyinstaller \
    --specpath build/pyinstaller \
    --distpath dist

echo "Hazır: dist/PdSqliteLib.app"

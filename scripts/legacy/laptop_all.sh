#!/bin/bash
# laptop(WSL) 一体化: 准备环境 -> 生成 3 个 obf -> 拷到 Windows 家目录
# 注意: WSL 空闲会关停, 所以必须一次跑完
set -e
: "${WINUSER:?请先 export WINUSER=<你的 Windows 用户名>}"
TMP=/tmp/omc-poi-china
SRC=/mnt/c/Users/$WINUSER
rm -rf "$TMP"; mkdir -p "$TMP"; cd "$TMP"

echo "[1/5] 下载 Temurin JDK 21"
curl -sL -o jdk.tar.gz "https://api.adoptium.net/v3/binary/latest/21/ga/linux/x64/jdk/hotspot/normal/eclipse"
mkdir -p jdk && tar xzf jdk.tar.gz -C jdk --strip-components=1
export JAVA_HOME="$TMP/jdk"; export PATH="$JAVA_HOME/bin:$PATH"
java -version 2>&1 | head -1

echo "[2/5] 下载 + 解包 OsmAndMapCreator"
curl -sL -o omc.zip https://download.osmand.net/latest-night-build/OsmAndMapCreator-main.zip
python3 -c "import zipfile;zipfile.ZipFile('omc.zip').extractall('omc')"
chmod +x omc/*.sh

echo "[3/5] 取输入数据"
cd omc
for f in Xian China5A ChinaBrands; do cp "$SRC/$f.osm" "./$f.osm"; done
ls -l *.osm

echo "[4/5] 生成 obf"
export JAVA_OPTS="-Xms512M -Xmx8G"
for f in Xian China5A ChinaBrands; do
  t0=$(date +%s)
  echo "--- $f ---"
  bash utilities.sh generate-poi "$f.osm" --chars-build-poi-nameindex=3 2>&1 \
    | grep -E "POI INDEX SIZE|Exception|Error|Poi processing finished" | tail -3 || true
  echo "    $(( $(date +%s) - t0 )) 秒"
done
ls -lh *.obf

echo "[5/5] 拷回 Windows 家目录"
cp -f *.obf "$SRC/"
ls -l "$SRC"/*.obf
echo "ALL DONE"

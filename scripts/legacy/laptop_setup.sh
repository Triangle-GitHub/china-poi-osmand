#!/bin/bash
# 在 laptop(WSL) 上准备 OsmAndMapCreator 运行环境
# 全部塞在 /tmp/omc-poi-china 里, 不装系统包, 事后整体删除
set -e
TMP=/tmp/omc-poi-china
rm -rf "$TMP"
mkdir -p "$TMP"
cd "$TMP"

echo "=== 1) Temurin JDK 21 (linux x64) 官方直链 ==="
URL="https://api.adoptium.net/v3/binary/latest/21/ga/linux/x64/jdk/hotspot/normal/eclipse"
echo "URL=$URL"

echo "=== 2) 下载并解包 JDK ==="
curl -sL -o jdk.tar.gz "$URL"
mkdir -p jdk && tar xzf jdk.tar.gz -C jdk --strip-components=1
export JAVA_HOME="$TMP/jdk"
export PATH="$JAVA_HOME/bin:$PATH"
java -version 2>&1 | head -2

echo "=== 3) 下载 OsmAndMapCreator ==="
curl -sL -o omc.zip https://download.osmand.net/latest-night-build/OsmAndMapCreator-main.zip
ls -l omc.zip

echo "=== 4) 解包(用 python, 系统没有 unzip) ==="
python3 - <<'PY'
import zipfile
z = zipfile.ZipFile('omc.zip')
z.extractall('omc')
print('解压完成, %d 个文件' % len(z.namelist()))
PY
chmod +x omc/*.sh
ls omc | head -6
echo "=== 就绪: $TMP ==="
du -sh "$TMP"

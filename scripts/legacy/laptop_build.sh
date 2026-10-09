#!/bin/bash
# 在 laptop 上批量生成 .poi.obf
set -e
TMP=/tmp/omc-poi-china
export JAVA_HOME="$TMP/jdk"
export PATH="$JAVA_HOME/bin:$PATH"
export JAVA_OPTS="-Xms512M -Xmx8G"
cd "$TMP/omc"
for f in Xian China5A ChinaBrands; do
  echo "=== generate-poi $f ==="
  start=$(date +%s)
  bash utilities.sh generate-poi "$f.osm" --chars-build-poi-nameindex=3 2>&1 \
    | grep -E "POI INDEX SIZE|Exception|Error|Poi processing finished" | tail -3 || true
  echo "    耗时 $(( $(date +%s) - start )) 秒"
done
echo "=== 产物 ==="
ls -lh *.obf

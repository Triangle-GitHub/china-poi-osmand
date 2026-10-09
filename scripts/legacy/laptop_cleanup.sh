#!/bin/bash
# 清理我在 laptop 上留下的所有东西
echo "=== 1) 我起的进程 ==="
pgrep -af "laptop_all[.]sh|[n]et.osmand.MainUtilities|[u]tilities.sh" || echo "(无)"
for p in $(pgrep -f "laptop_all[.]sh"); do kill "$p" 2>/dev/null; done
for p in $(pgrep -f "[n]et.osmand.MainUtilities"); do kill "$p" 2>/dev/null; done
for p in $(pgrep -f "[u]tilities.sh"); do kill "$p" 2>/dev/null; done
sleep 2
echo "=== 2) 清理后残留 ==="
pgrep -af "laptop_all[.]sh|[n]et.osmand.MainUtilities|[u]tilities.sh" || echo "无残留"
echo "=== 3) 删临时目录 ==="
rm -rf /tmp/omc-poi-china /tmp/omc-run.log
ls -d /tmp/omc-poi-china 2>/dev/null || echo "/tmp/omc-poi-china 已删"
echo "=== 4) 删我在 Windows 家目录放的文件 ==="
cd /mnt/c/Users/$WINUSER
rm -f probe_poi.sh laptop_setup.sh laptop_where.sh laptop_diag.sh laptop_all.sh
rm -f Xian.osm China5A.osm ChinaBrands.osm
echo "--- 家目录现状(前 25 项) ---"
ls -l /mnt/c/Users/$WINUSER | head -25
echo "=== 5) 磁盘 ==="
df -h / | tail -1

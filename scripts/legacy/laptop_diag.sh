#!/bin/bash
echo "--- /tmp 现在有什么 ---"
ls /tmp | head -10
echo "--- 挂载 ---"
mount | grep -E " /tmp | /mnt/c " || true
echo "--- 空间 ---"
df -h /tmp / /mnt/c 2>/dev/null
echo "--- WSL 是否刚重启 ---"
uptime
echo "--- 找找 jdk/omc 还在不在 ---"
ls -d /tmp/omc-poi-china 2>/dev/null || echo "/tmp/omc-poi-china 不存在"
find / -maxdepth 3 -name "OsmAndMapCreator.jar" 2>/dev/null | head -3

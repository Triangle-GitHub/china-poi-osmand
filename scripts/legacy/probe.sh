#!/bin/bash
# 探测 laptop 环境: 是否有 bash/Java/Python/网络, 以及能否装 JDK
echo "=== uname ==="
uname -a
echo "=== os-release ==="
( cat /etc/os-release 2>/dev/null | head -3 ) || echo "(无 /etc/os-release -> 可能是 Git Bash on Windows)"
echo "=== 关键命令 ==="
for c in java javac python3 python curl unzip sudo apt-get; do printf "%-10s " "$c"; command -v "$c" || echo "(缺)"; done
echo "=== 常见 JDK 位置 ==="
ls -d /usr/lib/jvm/* 2>/dev/null || echo "(/usr/lib/jvm 不存在)"
ls -d "/c/Program Files/Java"/* 2>/dev/null || echo "(C:\\Program Files\\Java 不存在)"
ls -d "/c/Program Files/Eclipse Adoptium"/* 2>/dev/null || echo "(无 Adoptium)"
echo "=== 是否 WSL ==="
grep -qi microsoft /proc/version 2>/dev/null && echo "是 WSL" || echo "不是 WSL"
echo "=== 网络 (从 laptop 出发) ==="
for u in https://api.github.com https://download.osmand.net https://mirrors.tuna.tsinghua.edu.cn https://repo.huaweicloud.com; do
  printf "%-42s " "$u"
  curl -s -o /dev/null --max-time 10 -w "http=%{http_code}\n" "$u" 2>/dev/null || echo FAIL
done
echo "=== 磁盘/内存 ==="
df -h /tmp / 2>/dev/null | tail -3
free -g 2>/dev/null | head -2
nproc

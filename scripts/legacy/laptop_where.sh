#!/bin/bash
# 定位 scp 进来的文件在 WSL 里的真实路径
echo "HOME=$HOME"
echo "PWD=$(pwd)"
echo "--- /mnt/c/Users 下的用户 ---"
ls /mnt/c/Users 2>/dev/null
echo "--- 找 laptop_setup.sh / probe_poi.sh ---"
ls -l /mnt/c/Users/*/laptop_setup.sh /mnt/c/Users/*/probe_poi.sh 2>/dev/null || echo "(没找到)"
echo "--- WSL 里的 /tmp/omc-poi-china ---"
ls -ld /tmp/omc-poi-china /tmp/omc-poi-china/omc 2>/dev/null

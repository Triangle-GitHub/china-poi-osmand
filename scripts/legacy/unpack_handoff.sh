#!/bin/bash
# 在 laptop(WSL) 上解包交接包到 Windows 家目录
set -e
: "${WINUSER:?请先 export WINUSER=<你的 Windows 用户名>}"
SRC=/mnt/c/Users/$WINUSER
cd "$SRC"
python3 - <<'PY'
import tarfile, os, shutil
base = '/mnt/c/Users/' + os.environ['WINUSER']
tf = os.path.join(base, 'handoff.tgz')
dest = os.path.join(base, 'poi-handoff')
if os.path.exists(dest):
    shutil.rmtree(dest)
with tarfile.open(tf) as t:
    t.extractall(base)
src = os.path.join(base, 'handoff')
if os.path.exists(src):
    os.rename(src, dest)
print('解包完成 ->', dest)
PY
rm -f handoff.tgz unpack_handoff.sh
echo "=== 目录树 ==="
ls -lR "$SRC/poi-handoff"
echo "=== 大小 ==="
du -sh "$SRC/poi-handoff"

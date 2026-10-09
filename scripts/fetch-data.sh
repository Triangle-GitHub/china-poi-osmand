#!/usr/bin/env bash
# 按 scripts/sources.tsv 拉取上游 POI 数据到本仓库对应目录。
# 数据不进 git（见 .gitignore），只在你本机落地。
#
# 用法:
#   bash scripts/fetch-data.sh            # 全部
#   bash scripts/fetch-data.sh brand a5a  # 只拉指定的几个
#
# ⚠️ #1/#3/#4 上游没有 LICENSE（默认版权保留），仅限个人自用，**不要再分发**。
#    详见 ../THIRD-PARTY-DATA.md
set -euo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/.." && pwd)
TSV="$HERE/sources.tsv"
TMP=$(mktemp -d "$ROOT/.fetch.XXXXXX")
trap 'rm -rf "$TMP"' EXIT

wanted=("$@")
is_wanted() { [ ${#wanted[@]} -eq 0 ] && return 0; for w in "${wanted[@]}"; do [ "$w" = "$1" ] && return 0; done; return 1; }

fetch_zip() { # owner/repo → 解包目录（回显路径）
  local repo="$1" br
  for br in main master; do
    if curl -fsSL "https://github.com/$repo/archive/refs/heads/$br.zip" -o "$TMP/x.zip"; then
      unzip -q -o "$TMP/x.zip" -d "$TMP" >/dev/null
      ls -d "$TMP"/*/ | head -1
      return 0
    fi
  done
  echo "✗ 下载失败：$repo（main/master 都试过了）" >&2
  return 1
}

while IFS=$'\t' read -r name upstream dest content license redist note; do
  [ "$name" = "name" ] && continue          # 表头
  is_wanted "$name" || continue
  printf '=== %-8s ← %s\n' "$name" "$upstream"
  src=$(fetch_zip "$upstream") || continue
  case "$name" in
    brand)
      # 上游布局 data/poi_data/*.json ；build.py 读 brand/*.json ⇒ 拉平
      mkdir -p "$ROOT/brand"
      n=0
      while IFS= read -r json; do cp -a "$json" "$ROOT/brand/"; n=$((n+1)); done \
        < <(find "$src" -path '*poi_data*' -name '*.json' | sort)
      echo "    → brand/  $n 个 json" ;;
    a5a)
      mkdir -p "$ROOT/a5a"; cp -a "$src" "$ROOT/a5a/$(basename "$src")"
      echo "    → a5a/$(basename "$src")" ;;
    pyjacc)
      # 保持原始布局 pyjacc/data-poi-main/…
      mkdir -p "$ROOT/pyjacc"; cp -a "$src" "$ROOT/pyjacc/$(basename "$src")"
      echo "    → pyjacc/$(basename "$src")" ;;
    baidu)
      # 原始布局是 baidu/src/POI-data-of-China-main/…
      mkdir -p "$ROOT/baidu/src"; cp -a "$src" "$ROOT/baidu/src/$(basename "$src")"
      echo "    → baidu/src/$(basename "$src")" ;;
    *)
      mkdir -p "$ROOT/$dest"; cp -a "$src" "$ROOT/$dest/$(basename "$src")"
      echo "    → $dest/$(basename "$src")" ;;
  esac
done < "$TSV"

echo
echo "完成。下一步： python3 build.py   （或 python3 build.py --xian）"
echo "注：如果某个上游改了仓库布局，脚本会打印警告或复制到意料之外的层级，请按需调整本脚本的 case 分支。"

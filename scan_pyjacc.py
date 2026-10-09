#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全量扫描 Pyjacc 的 1,098 个 xlsx: 统计省/市/区的 POI 数量, 并缓存到 json。"""
import collections
import glob
import json
import os
import sys
import time
from geoio import xlsx_rows

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pyjacc", "data-poi-main")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pyjacc_counts.json")


def main():
    files = sorted(glob.glob(os.path.join(ROOT, "part*", "*", "**", "*.xlsx"), recursive=True))
    print("xlsx 文件数:", len(files))
    per_prov = collections.Counter()
    per_city = collections.Counter()
    provinces = collections.OrderedDict()
    t0 = time.time()
    total = 0
    bad = 0
    for i, p in enumerate(files, 1):
        rel = os.path.relpath(p, ROOT).split(os.sep)
        prov = rel[1]
        city = rel[2] if len(rel) > 3 else prov
        n = 0
        try:
            it = xlsx_rows(p)
            next(it, None)  # 表头
            for row in it:
                if row and (row[3] is not None or row[17] is not None):  # 有内容
                    n += 1
        except Exception as e:
            bad += 1
            print("  !! %s: %s" % (rel, e))
        per_prov[prov] += n
        per_city[(prov, city)] += n
        provinces.setdefault(prov, []).append(city)
        total += n
        if i % 100 == 0:
            print("  %4d/%d 文件, 累计 %d 条, %.0fs" % (i, len(files), total, time.time() - t0))
            sys.stdout.flush()
    print("\n总 POI: %d 条 (解析失败 %d 个文件), 用时 %.0fs" % (total, bad, time.time() - t0))
    print("\n按省级区划:")
    for k, v in per_prov.most_common():
        cities = len(set(provinces[k]))
        print("  %-12s %9d 条  (%d 个市)" % (k, v, cities))
    json.dump(
        {"total": total, "per_prov": dict(per_prov), "per_city": {"%s|%s" % k: v for k, v in per_city.items()}},
        open(OUT, "w", encoding="utf-8"),
        ensure_ascii=False,
        indent=1,
    )
    print("\n缓存 -> %s" % OUT)


if __name__ == "__main__":
    main()

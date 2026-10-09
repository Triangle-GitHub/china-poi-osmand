#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""独立校验 .obf 是否真的装进了源数据。
方法: 从源 OSM XML 取全部 name, 再在 obf 二进制里找这些 UTF-8 字符串;
      OBF 的名称索引/文本索引是明文 UTF-8, 所以能直接命中。
"""
import html
import re
import sys


def names_from_osm(path):
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = re.search(r'<tag k="name" v="([^"]*)"', line)
            if m:
                out.append(html.unescape(m.group(1)))
    return out


def check(obf, names, label=""):
    data = open(obf, "rb").read()
    hits = sum(1 for n in names if n and n.encode("utf-8") in data)
    pct = 100.0 * hits / len(names) if names else 0
    print("%-28s %8.2f MB | 源名称 %6d | obf 内命中 %6d (%.1f%%)" % (label or obf, len(data) / 1e6, len(names), hits, pct))
    present = [m.decode() for m in (b"MapIndex", b"PoiIndex", b"AddressIndex", b"TransportIndex", b"RouteIndex", b"BasemapIndex") if m in data]
    print("     段: %s" % (", ".join(present) if present else "(未找到任何已知段标记)"))
    for probe in ("shop", "conv", "cafe", "restaurant", "supermarket", "hotel", "pharmacy"):
        if probe.encode() in data:
            print("     含类目标记: %s" % probe, end="")
    print()
    return hits, len(names)


if __name__ == "__main__":
    obf = sys.argv[1]
    osm = sys.argv[2]
    label = sys.argv[3] if len(sys.argv) > 3 else ""
    ns = names_from_osm(osm)
    check(obf, ns, label)

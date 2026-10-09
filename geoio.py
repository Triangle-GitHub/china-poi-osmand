#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""纯标准库读取 xlsx (只取单元格值), 以及 ESRI Shapefile 的属性表(dbf)。

只实现本项目用得到的部分:
  xlsx:  sharedStrings + 每个 worksheet 的行/列值
  dbf:   dBASE III 表头 + 记录, 按字段类型解码(字符/数值/日期)
"""
import re
import struct
import zipfile
from xml.etree import ElementTree as ET

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


# ------------------------------------------------------------------ xlsx
def _shared_strings(z):
    try:
        raw = z.read("xl/sharedStrings.xml")
    except KeyError:
        return []
    root = ET.fromstring(raw)
    return ["".join(t.text or "" for t in si.iter(NS + "t")) for si in root]


def _col_of(ref):
    m = re.match(r"([A-Z]+)", ref or "A")
    return m.group(1) if m else "A"


def _col_index(col):
    n = 0
    for ch in col:
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def xlsx_rows(path):
    """yield list[str|None] —— 每行按列序展开(已按列字母定位, 缺列补 None)"""
    with zipfile.ZipFile(path) as z:
        shared = _shared_strings(z)
        sheets = sorted(n for n in z.namelist() if re.match(r"xl/worksheets/sheet\d+\.xml$", n))
        for sheet in sheets:
            root = ET.fromstring(z.read(sheet))
            for row in root.iter(NS + "row"):
                cells = {}
                width = 0
                for c in row.iter(NS + "c"):
                    ci = _col_index(_col_of(c.get("r")))
                    width = max(width, ci + 1)
                    t = c.get("t")
                    v = c.find(NS + "v")
                    if t == "s" and v is not None:
                        i = int(v.text)
                        val = shared[i] if i < len(shared) else None
                    elif t == "inlineStr":
                        val = "".join(x.text or "" for x in c.iter(NS + "t"))
                    else:
                        val = v.text if v is not None else None
                    cells[ci] = val
                yield [cells.get(i) for i in range(width)]


# ------------------------------------------------------------------ dbf
def dbf_rows(path):
    """读取 dBase III 属性表: 返回 (字段名列表, 行迭代器)"""
    with open(path, "rb") as fh:
        head = fh.read(32)
        if len(head) < 32:
            raise ValueError("dbf 太短")
        nrec, hlen, rlen = struct.unpack("<IHH", head[4:12])
        fields = []
        while True:
            fd = fh.read(32)
            if not fd or fd[0] in (0x0D, 0x00):
                break
            name = fd[:11].split(b"\x00")[0].decode("ascii", "ignore")
            ftype = chr(fd[11])
            flen = fd[16]
            fields.append((name, ftype, flen))
        fh.seek(hlen)

        recs = []
        for _ in range(nrec):
            rec = fh.read(rlen)
            if not rec or rec[:1] == b"*":  # 删除标记
                continue
            out, off = [], 1
            for name, ftype, flen in fields:
                raw = rec[off:off + flen]
                off += flen
                txt = raw.decode("gbk", "ignore").strip()
                if ftype == "N":
                    try:
                        out.append(float(txt) if "." in txt else int(txt))
                    except ValueError:
                        out.append(None)
                else:
                    out.append(txt)
            recs.append(out)
        return [f[0] for f in fields], recs


def shp_points(path):
    """读取 shp 里的点几何: yield (x, y) —— 只处理 Point(1)/PointZ(11)/PointM(21)"""
    with open(path, "rb") as fh:
        fh.seek(32)
        while True:
            hdr = fh.read(8)
            if len(hdr) < 8:
                return
            _, clen = struct.unpack(">ii", hdr)
            body = fh.read(clen * 2)
            if len(body) < 4:
                return
            stype = struct.unpack("<i", body[:4])[0]
            if stype in (1, 11, 21):
                x, y = struct.unpack("<dd", body[4:20])
                yield x, y
            # 其余几何类型(线/面)跳过: 本项目只用点层

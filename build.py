#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把中国大陆 POI 数据转成 OsmAnd / CoMaps 能吃的格式。

输入:
  brand/*.json        china-brand-poi-maps,  [{id,name,address,category,lat,lng,city}]  坐标 GCJ-02
  a5a/.../*.csv       china-5a-scenic-areas,  坐标已是 WGS-84

输出:
  out/<name>.kml      CoMaps / OsmAnd 书签(图层/分组)
  out/<name>.gpx      OsmAnd 收藏(My Places)
  out/<name>.osm      OSM XML, 交给 OsmAndMapCreator 生成 .poi.obf

用法: python3 build.py            # 全部
      python3 build.py --xian     # 只出西安品牌
"""
import csv
import glob
import json
import math
import os
import sys
from xml.sax.saxutils import escape as esc


def esc_a(s):
    """XML 属性值转义 (地址里出现双引号会截断属性, 必须转)"""
    return esc(s, {'"': "&quot;", "'": "&apos;"})

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

# ---------------------------------------------------------------- 坐标转换
# GCJ-02 (高德/腾讯 火星坐标) -> WGS-84 (OSM/OsmAnd 底图坐标)
# 标准实现, 城内精度约 1~2 m
A = 6378245.0
EE = 0.00669342162296594323


def _out_of_china(lng, lat):
    return not (72.004 <= lng <= 137.8347 and 0.8293 <= lat <= 55.8271)


def _t_lat(x, y):
    r = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x))
    r += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
    r += (20.0 * math.sin(y * math.pi) + 40.0 * math.sin(y / 3.0 * math.pi)) * 2.0 / 3.0
    r += (160.0 * math.sin(y / 12.0 * math.pi) + 320 * math.sin(y * math.pi / 30.0)) * 2.0 / 3.0
    return r


def _t_lng(x, y):
    r = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))
    r += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
    r += (20.0 * math.sin(x * math.pi) + 40.0 * math.sin(x / 3.0 * math.pi)) * 2.0 / 3.0
    r += (150.0 * math.sin(x / 12.0 * math.pi) + 300.0 * math.sin(x / 30.0 * math.pi)) * 2.0 / 3.0
    return r


def gcj2wgs(lng, lat):
    if _out_of_china(lng, lat):
        return lng, lat
    dlat = _t_lat(lng - 105.0, lat - 35.0)
    dlng = _t_lng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * math.pi
    magic = math.sin(radlat)
    magic = 1 - EE * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((A * (1 - EE)) / (magic * sqrtmagic) * math.pi)
    dlng = (dlng * 180.0) / (A / sqrtmagic * math.cos(radlat) * math.pi)
    return lng - dlng, lat - dlat


# ---------------------------------------------------------------- 分类映射
# 高德 category (形如 "餐饮服务:咖啡厅") -> (OSM 标签, KML 颜色, GPX sym, 中文组名)
CAT_MAP = [
    ("咖啡", ["amenity=cafe"], "ff4db8ff", "Cafe", "咖啡"),
    ("茶饮", ["amenity=cafe"], "ff4db8ff", "Cafe", "茶饮"),
    ("饮品", ["amenity=cafe"], "ff4db8ff", "Cafe", "饮品"),
    ("甜品", ["amenity=ice_cream"], "ffb0e0e6", "Ice Cream", "甜品"),
    ("蛋糕", ["shop=bakery"], "ffb0e0e6", "Bakery", "烘焙"),
    ("快餐", ["amenity=fast_food"], "ff0080ff", "Fast Food", "快餐"),
    ("火锅", ["amenity=restaurant"], "ff2020ff", "Restaurant", "火锅"),
    ("餐厅", ["amenity=restaurant"], "ff2020ff", "Restaurant", "餐饮"),
    ("餐饮", ["amenity=restaurant"], "ff2020ff", "Restaurant", "餐饮"),
    ("便利店", ["shop=convenience"], "ff00cc00", "Convenience Store", "便利店"),
    ("超市", ["shop=supermarket"], "ff00cc00", "Supermarket", "超市"),
    ("购物", ["shop=yes"], "ff00cc00", "Shop", "购物"),
    ("商场", ["shop=mall"], "ff00cc00", "Shop", "商场"),
    ("酒店", ["tourism=hotel"], "ffff00ff", "Hotel", "酒店"),
    ("宾馆", ["tourism=hotel"], "ffff00ff", "Hotel", "酒店"),
    ("快递", ["amenity=parcel_locker"], "ffff8800", "Post Office", "快递"),
    ("物流", ["amenity=parcel_locker"], "ffff8800", "Post Office", "快递"),
    ("药店", ["amenity=pharmacy"], "ff00ff00", "Pharmacy", "药店"),
    ("医院", ["amenity=hospital"], "ff0000ff", "Hospital", "医院"),
    ("银行", ["amenity=bank"], "ff808080", "Bank", "银行"),
    ("加油站", ["amenity=fuel"], "ff808080", "Gas Station", "加油"),
]
DEFAULT = (["shop=yes"], "ffa0a0a0", "Flag, Blue", "其他")


def classify(cat_text):
    for key, tags, color, sym, grp in CAT_MAP:
        if key in cat_text:
            return tags, color, sym, grp
    return DEFAULT


# ---------------------------------------------------------------- 数据装载
SKIPPED = []  # 采集时缺坐标被跳过的记录
def load_brands(city=None):
    """返回 [{name, lat, lng, brand, address, category, tags, color, sym, grp}]"""
    rows = []
    for p in sorted(glob.glob(os.path.join(HERE, "brand", "*.json"))):
        brand = os.path.splitext(os.path.basename(p))[0]
        for r in json.load(open(p, encoding="utf-8")):
            if city and r.get("city") != city:
                continue
            if r.get("lng") is None or r.get("lat") is None:
                # 采集时未返回坐标的记录(菜鸟驿站/古茗/罗森 共约 3 万条), 跳过
                SKIPPED.append(r.get("name") or "")
                continue
            lng, lat = gcj2wgs(float(r["lng"]), float(r["lat"]))
            tags, color, sym, grp = classify(r.get("category") or "")
            rows.append(
                dict(
                    name=r.get("name") or brand,
                    lat=lat,
                    lng=lng,
                    brand=brand,
                    address=r.get("address") or "",
                    category=r.get("category") or "",
                    id=r.get("id") or "",
                    city=r.get("city") or "",
                    tags=tags,
                    color=color,
                    sym=sym,
                    grp=grp,
                )
            )
    return rows


def load_5a():
    csvs = glob.glob(os.path.join(HERE, "a5a", "**", "china-5a-scenic-areas.csv"), recursive=True)
    rows = []
    with open(csvs[0], encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            try:
                lat, lng = float(r["latitude"]), float(r["longitude"])
            except (KeyError, ValueError):
                continue
            rows.append(
                dict(
                    name=r["name_zh"],
                    lat=lat,
                    lng=lng,
                    brand="5A景区",
                    address="%s %s" % (r.get("province_zh", ""), r.get("city_zh", "")),
                    category=r.get("grade", "5A"),
                    id=r.get("slug", ""),
                    city=r.get("city_zh", ""),
                    tags=["tourism=attraction"],
                    color="ffd4af37",
                    sym="Scenic Area",
                    grp="5A景区",
                )
            )
    return rows


# ---------------------------------------------------------------- 输出: KML
KML_HEAD = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document><name>{title}</name>
{styles}
{folders}
</Document></kml>
"""


def write_kml(path, rows, title):
    groups = {}
    for r in rows:
        groups.setdefault(r["brand"] if title.startswith("品牌") else r["grp"], []).append(r)
    styles = "\n".join(
        '<Style id="s%s"><IconStyle><color>%s</color>'
        '<scale>1.0</scale></IconStyle></Style>' % (r["grp"], r["color"])
        for r in {g: r for g, r in ((x["grp"], x) for x in rows)}.values()
    )
    folders = []
    for gname in sorted(groups):
        items = groups[gname]
        pm = []
        for r in items:
            desc = "%s<br/>%s<br/>%s" % (
                esc(r["brand"]),
                esc(r["category"]),
                esc(r["address"]),
            )
            pm.append(
                '<Placemark><name>%s</name><description><![CDATA[%s]]></description>'
                '<styleUrl>#s%s</styleUrl>'
                "<Point><coordinates>%.6f,%.6f,0</coordinates></Point></Placemark>"
                % (esc(r["name"]), desc, r["grp"], r["lng"], r["lat"])
            )
        folders.append(
            '<Folder><name>%s (%d)</name>%s</Folder>' % (esc(gname), len(items), "".join(pm))
        )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(KML_HEAD.format(title=esc(title), styles=styles, folders="".join(folders)))


# ---------------------------------------------------------------- 输出: GPX
def write_gpx(path, rows, title):
    out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<gpx version="1.1" creator="poi-work" xmlns="http://www.topografix.com/GPX/1/1">',
        "<metadata><name>%s</name></metadata>" % esc(title),
    ]
    for r in rows:
        out.append(
            '<wpt lat="%.6f" lon="%.6f"><name>%s</name><desc>%s</desc>'
            "<sym>%s</sym><type>%s</type></wpt>"
            % (
                r["lat"],
                r["lng"],
                esc(r["name"]),
                esc("%s | %s | %s" % (r["brand"], r["category"], r["address"])),
                esc(r["sym"]),
                esc(r["grp"]),
            )
        )
    out.append("</gpx>")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))


# ---------------------------------------------------------------- 输出: OSM XML
def write_osm(path, rows):
    """给 OsmAndMapCreator 用. 必须有 OSM POI 标签, 否则生成空 obf."""
    out = ['<?xml version="1.0" encoding="UTF-8"?>', '<osm version="0.6" generator="poi-work">']
    for i, r in enumerate(rows, 1):
        out.append('<node id="%d" action="modify" visible="true" lat="%.7f" lon="%.7f">' % (i, r["lat"], r["lng"]))
        out.append('<tag k="name" v="%s"/>' % esc_a(r["name"]))
        if r.get("brand"):
            out.append('<tag k="brand" v="%s"/>' % esc_a(r["brand"]))
        for t in r["tags"]:
            k, v = t.split("=", 1)
            out.append('<tag k="%s" v="%s"/>' % (k, esc_a(v)))
        if r.get("grp"):
            out.append('<tag k="poi_group" v="%s"/>' % esc_a(r["grp"]))
        if r.get("address"):
            out.append('<tag k="addr:full" v="%s"/>' % esc_a(r["address"]))
        if r.get("city"):
            out.append('<tag k="addr:city" v="%s"/>' % esc_a(r["city"]))
        out.append("</node>")
    out.append("</osm>")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))


# ---------------------------------------------------------------- main
def main():
    os.makedirs(OUT, exist_ok=True)
    xian_only = "--xian" in sys.argv

    print("[1/3] 读 5A 景区 (WGS-84, 免转换) ...")
    a5 = load_5a()
    print("      %d 条" % len(a5))
    write_kml(os.path.join(OUT, "china-5a.kml"), a5, "中国5A景区")
    write_gpx(os.path.join(OUT, "china-5a.gpx"), a5, "中国5A景区")
    write_osm(os.path.join(OUT, "china-5a.osm"), a5)

    print("[2/3] 读品牌门店 (GCJ-02 -> WGS-84) ...")
    if xian_only:
        rows = load_brands(city="西安")
        tag = "xian"
        title = "西安品牌门店"
    else:
        rows = load_brands()
        tag = "brands-all"
        title = "中国品牌门店"
    print("      %d 条" % len(rows))
    print("      (跳过缺坐标 %d 条)" % len(SKIPPED))
    write_kml(os.path.join(OUT, "%s.kml" % tag), rows, title)
    write_gpx(os.path.join(OUT, "%s.gpx" % tag), rows, title)
    write_osm(os.path.join(OUT, "%s.osm" % tag), rows)

    print("[3/3] 抽样核对坐标转换 (GCJ-02 -> WGS-84 位移):")
    raw = load_brands(city="西安")[:3]
    for r in raw:
        print("      %-28s wgs=%.6f,%.6f" % (r["name"][:26], r["lng"], r["lat"]))

    for f in sorted(os.listdir(OUT)):
        p = os.path.join(OUT, f)
        print("  产出 %-24s %8.2f MB" % (f, os.path.getsize(p) / 1e6))


if __name__ == "__main__":
    main()

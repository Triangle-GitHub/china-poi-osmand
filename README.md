# china-poi-osmand

把**中国大陆的 POI 数据**转换成 **OsmAnd / CoMaps** 能用的格式，并进一步生成 `.poi.obf` 离线 POI 索引。

> 一句话：`POI 原始数据 → 坐标纠偏(GCJ-02→WGS-84) → 标签映射 → KML/GPX/OSM XML → (OsmAndMapCreator) → .poi.obf`

## 为什么需要这个

国内 POI 数据（高德/腾讯系）用的是 **GCJ-02**「火星坐标」，而 OSM/OsmAnd 底图是 **WGS-84**。
不转换直接导入，整份数据会**整体偏移 300–500 m**（在手机上表现为"店铺飘到马路对面/隔壁街区"）。
本项目的 `build.py` 只做该做的三件事：坐标纠偏、中文分类 → OSM 标签、输出三种格式；**纯标准库，无第三方依赖**。

## 快速开始

```bash
# 0) 取数据（见 THIRD-PARTY-DATA.md；数据本身不入库）
bash scripts/fetch-data.sh

# 1) 生成 KML / GPX / OSM XML（输出到 out/）
python3 build.py            # 全国品牌门店 + 全国 5A 景区
python3 build.py --xian     # 只要西安市的品牌门店

# 2) 手机直接可用：把 out/*.kml 或 out/*.gpx 传进手机
#    CoMaps/OsmAnd → 我的位置 → 收藏/书签 → 导入

# 3) 想要「在原生搜索里按名字搜到」→ 生成 .poi.obf（需要 Java 17+）
#    见下方「生成 .poi.obf」
```

### 生成 `.poi.obf`

`.kml/.gpx` 只能当书签浏览；要进 OsmAnd 的**原生搜索**，得用官方工具把 `.osm` 编成 `.obf`：

```bash
# 下载 OsmAndMapCreator（约 150 MB，nightly）
curl -LO https://download.osmand.net/latest-night-build/OsmAndMapCreator-main.zip

export JAVA_OPTS="-Xms512M -Xmx8G"          # 17.5 万点建议给 4~8 GB，默认值会 OOM
bash utilities.sh generate-poi Xian.osm --chars-build-poi-nameindex=3
```

- 输入文件名即地图区域名（所以先把 `out/xian.osm` 复制成 `Xian.osm`）
- `--chars-build-poi-nameindex=3` 建名字索引 ⇒ 手机上才能**按名字搜到**这些 POI
- 产物落在当前目录：`Xian.obf` 等，拷进手机
  `/storage/emulated/0/Android/data/net.osmand.plus/files/`，在 OsmAnd 里启用后重启

**实测耗时/体积**（175,181 点的全国品牌那份）：

| 输入 | 点数 | 耗时 | 产物 | POI INDEX SIZE |
|---|---|---|---|---|
| `Xian.osm` | 3,234 | ~1 s | `Xian.obf` 1,973,126 B | 1,973,108 |
| `China5A.osm` | 373 | ~1 s | `China5a.obf` 280,034 B | 280,016 |
| `ChinaBrands.osm` | 175,181 | ~2 min | `Chinabrands.obf` 115,406,700 B | 115,406,682 |

三份都通过 `inspector` 校验（名字索引已建立，例如 373 个 5A 景区全部入库、
`POI Name index stats (839 prefixes, 10,632 tokens, 3,841 refs/atoms)`）。
`verify_obf.py` 是另一个独立校验器：直接从源 OSM XML 抽 `name`，去 obf 二进制里找明文 UTF-8 命中，
用来验证"数据真的装进去了"（抽样实测：Xian 3,234/3,234、5A 373/373、全国品牌 500/500）。

## 目录结构

```
build.py             主转换器（GCJ-02→WGS-84、分类映射、三种输出）
geoio.py             纯标准库读 xlsx / dbf（给 Pyjacc、百度那两份数据用的）
scan_pyjacc.py       扫描 Pyjacc 的 1,098 个 xlsx，统计省/市/区 POI 数量
verify_obf.py        校验 .obf 是否真的装了源数据（明文 UTF-8 命中法）
HANDOFF.md           一次真实交接的完整记录（把 .osm 交给人跑到 .obf）
BUILD-NOTES.md       那次交接的**执行结果**记录（含 MD5、耗时、踩坑）
THIRD-PARTY-DATA.md  数据来源 / 许可矩阵 / 拉取方式
SCRUB-NOTES.md       本仓库做过的脱敏替换（说明"哪些信息被替换掉了"）
scripts/fetch-data.sh  按 sources.tsv 拉取上游数据
scripts/sources.tsv    上游仓库 → 用途 → 许可 → 目标路径
scripts/legacy/        当年在笔记本(WSL)上用过的一次性脚本（留作过程记录）
samples/               小样本：西安品牌(3,234)、全国 5A(373) 的 KML/GPX/OSM + 5A 原始 CSV
data/ brand/ a5a/ out/ 运行期目录，不入库（见 .gitignore）
```

## 数据来源与许可（**重要**）

| 用途 | 上游 | 许可 | 可否再分发 |
|---|---|---|---|
| 品牌门店 56 品牌 / 66 城 / 205,228 条（2026-05 采集，GCJ-02） | `Wadesha/china-brand-poi-maps` | **无** | ❌ 仅个人自用 |
| 全国 5A 景区 373 条（WGS-84） | `tuansuwu/china-5a-scenic-areas` | **CC BY-SA 4.0** | ✅ 需署名 + 同许可 |
| 省会城市 POI（高德，2022-09） | `Pyjacc/data-poi` | **无** | ❌ |
| 百度 POI（2020，按城市×6 大类） | `wangunji/POI-data-of-China` | **无** | ❌ |

⇒ 本仓库**只放代码、文档和小样本**；上面"无许可"的数据一律由 `scripts/fetch-data.sh`
在你本机拉取、留在 `.gitignore` 覆盖的目录里，**请勿再分发**。细则见 `THIRD-PARTY-DATA.md`。

## 边界与注意

- 本项目只做「本地文件 → 本地文件」，**不联网抓取**、不调用任何地图服务 API。
- 生成的 `.osm` 里如果出现**未转义的双引号**，OsmAndMapCreator 会抛
  `XmlPullParserException: Attr.value missing`；`build.py` 已用 `esc_a()` 处理过，
  **不要手工改这些 XML**，要改内容请改脚本重新生成。
- 只有 `name` 而没有 POI 标签（`amenity=`/`shop=`/`tourism=`）的 node 会被 OsmAndMapCreator 忽略。
- 5A 景区那份数据是 CC BY-SA 4.0，`samples/` 里附了它的 LICENSE 与原始 CSV。

## 背景

这套东西最初是为「把连锁品牌门店和 5A 景区灌进手机 OsmAnd」做的，`
HANDOFF.md` / `BUILD-NOTES.md` 是当时一次真实交接（一台机器准备数据、另一台机器跑 OMC）的原文，
保留了原始的命令、耗时、MD5 与踩坑，便于复现或接手。已按 `SCRUB-NOTES.md` 做过去标识化处理。

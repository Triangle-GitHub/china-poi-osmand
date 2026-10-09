# 交接文档：把准备好的 OSM XML 转成 OsmAnd 可用的 `.poi.obf`

> 生成时间：2026-09-16 · 生成方：手机 Termux 上的 pi agent（本机 <android-device>）
> 接收方：**laptop（Windows，<laptop-host>，WSL2 Ubuntu 24.04 可用）** 上的 AI
> 本目录在 Windows 侧：`%USERPROFILE%\poi-handoff\`（WSL 里即 `/mnt/c/Users/$WINUSER/poi-handoff/`）

---

## 0. 一句话任务

用 **OsmAndMapCreator** 把本目录 `inputs/` 里已经准备好的 3 个 `.osm` 文件，各自生成一个 `.poi.obf`
（OsmAnd 的离线 POI 索引文件），产出物会被拷回手机装进 OsmAnd。

前置工作（数据获取、坐标系转换、分类映射、XML 转义、OsmAndMapCreator 下载）都已经做完，
**剩下的只有「运行 OsmAndMapCreator」这一步**，在 Windows 上大约 10 分钟。

---

## 1. 当前进度

| 项 | 状态 |
|---|---|
| 原始数据下载 | ✅ 已下载 4 份数据包（在手机 `/storage/emulated/0/Download/pois/`） |
| 坐标转换 GCJ-02 → WGS-84 | ✅ 已做（用天安门基准点校验，经度误差 ~5 m） |
| 分类 → OSM 标签映射 | ✅ 已做（amenity/shop/tourism…） |
| 转成 OSM XML + XML 转义 | ✅ 已做（3 个文件在 `inputs/`） |
| **生成 `.poi.obf`** | ⬜ **未完成 —— 这是要你做的事** |
| 装进手机 OsmAnd | ⬜ 待产出 obf 后进行 |

> 其中 `inputs/Xian.osm` **曾经成功生成过 obf**（在另一台 Linux 机器上，Java 25 环境），
> 产物样例在 `sample/Xian.obf`（1.9 MB）。所以工具链是验证过的，只是那台机器 CPU 太慢、且中途断连。

---

## 2. 输入文件（`inputs/`）

| 文件 | 内容 | POI 点数 | 坐标系 | 备注 |
|---|---|---|---|---|
| `Xian.osm` | 西安市连锁品牌门店 | 3,234 | WGS-84 | 区域名建议 `Xian` |
| `China5A.osm` | 全国 5A 级景区 | 373 | WGS-84 | 原始数据本就是 WGS-84 |
| `ChinaBrands.osm` | 全国 56 个连锁品牌门店 | 175,181 | WGS-84 | 最大的一份，也最慢 |

三个文件都是标准 **OSM XML**（`<osm><node lat lon><tag k v/>…</node></osm>`），
每个 node 至少带 `name` + 一个 POI 标签（`amenity=` / `shop=` / `tourism=`），
另外带 `brand`、`addr:full`、`addr:city`、`poi_group`。

⚠️ 已踩过的坑：标签值里出现 **未转义的双引号**会让 OsmAndMapCreator 抛
`XmlPullParserException: Attr.value missing`。本目录的输入已经修好，**不要手工改这些 XML**。

---

## 3. 需要的东西

1. **Java 17+**（实测 OsmAndMapCreator 的 class 字节码 major=61，即 Java 17 起）。
   - 这台机器 WSL 里没有 java。Windows 侧建议装 **Temurin 21**：<https://adoptium.net/>（装完 `java -version` 能跑即可）。
2. **OsmAndMapCreator**（151 MB，2026-09-16 night-build）：
   <https://download.osmand.net/latest-night-build/OsmAndMapCreator-main.zip>
   - 解包后共 242 个文件，约 195 MB；`utilities.bat`(Windows) / `utilities.sh`(类 Unix) 都在根目录。
3. **磁盘**：这台机器 `C:` 只剩 **约 6 GB**。解包 OMC 约 195 MB、JDK 约 190 MB，
   建议**工作目录放 WSL 的 ext4**（`/` 有 953 GB 空闲），例如 `/tmp/omc-work` 或 `~/omc-work`。
   ⚠️ **WSL 空闲会自动关停，`/tmp` 会被清空** —— 所以请在**同一次会话里**跑完，或把工作目录放到 `~/`（ext4，持久）。

---

## 4. 怎么做（Windows 侧，PowerShell / cmd）

```bat
:: 1) 解包
mkdir D:\omc-work
cd /d D:\omc-work
:: 把 OsmAndMapCreator-main.zip 解包到这里

:: 2) 设置内存（脚本里默认值偏小，175k 点建议给 4~8 GB）
set JAVA_OPTS=-Xms512M -Xmx8G

:: 3) 逐份生成（输入文件名 = 地图区域名，所以先复制成想要的短名字）
copy /Y %USERPROFILE%\poi-handoff\inputs\Xian.osm        Xian.osm
copy /Y %USERPROFILE%\poi-handoff\inputs\China5A.osm     China5A.osm
copy /Y %USERPROFILE%\poi-handoff\inputs\ChinaBrands.osm ChinaBrands.osm

utilities.bat generate-poi Xian.osm        --chars-build-poi-nameindex=3
utilities.bat generate-poi China5A.osm     --chars-build-poi-nameindex=3
utilities.bat generate-poi ChinaBrands.osm --chars-build-poi-nameindex=3
```

- `.obf` 会生成在**当前工作目录**，名字是 `Xian.obf` / `China5a.obf` / `Chinabrands.obf` 这种由文件名派生的形式。
- `--chars-build-poi-nameindex=3` 会建立名字索引 → 手机上才能**按名字搜到**这些 POI。
- 也可以用图形界面：跑 `OsmAndMapCreator.bat` → 勾选 **Build POI index** → 菜单 **File → Create .obf from file**。

### 如果要用 WSL 跑（可选，Linux 路径更快）

```bash
cd ~/omc-work                       # 解包 OMC 到这里
export JAVA_OPTS="-Xms512M -Xmx8G"
bash utilities.sh generate-poi "$HOME/omc-work/Xian.osm" --chars-build-poi-nameindex=3
```
注意：WSL 里读 Windows 文件是 `/mnt/c/Users/$WINUSER/poi-handoff/inputs/`。

---

## 5. 怎么确认成功

```bat
inspector.bat Xian.obf
:: 或者： java -cp "OsmAndMapCreator.jar;lib\*" net.osmand.obf.BinaryInspector Xian.obf
```

期望看到 POI 段（POI index）有条目。参考量级：

| 输入 | 成功时的 log 特征 | 预期输出大小 |
|---|---|---|
| `Xian.osm`（3,234 点） | `POI INDEX SIZE : 1973108` | ~1.9 MB |
| `China5A.osm`（373 点） | `POI INDEX SIZE : ~280016` | ~274 KB |
| `ChinaBrands.osm`（175,181 点） | `Poi processing finished` + `Finish writing binary file` | 十 MB 级 |

失败特征与对策：
- `XmlPullParserException: Attr.value missing` → 输入 XML 属性里有未转义引号（当前输入已修，勿改）。
- `OutOfMemoryError` → 调大 `JAVA_OPTS=-Xmx8G`。
- 生成出来的 obf 特别小（几 KB）且手机上搜不到 → 检查是否**没带 POI 标签**（只有 name 的 node 会被忽略，本次已保证带了 amenity/shop/tourism）。

---

## 6. 产出物怎么交付

把生成好的 `.obf` 放到这个目录（方便手机取回）：

```
%USERPROFILE%\poi-handoff\output\
```

然后告诉手机侧（Termux 上的 pi agent）：`poi-handoff/output/` 下有 obf。
手机侧会用 `scp laptop:..."` 取回，并放进 OsmAnd 数据目录
`/storage/emulated/0/Android/data/net.osmand.plus/files/`（或通过 OsmAnd「地图与资源 → 离线地图」导入），
然后在 OsmAnd 里启用这几张 POI 地图、重启，就能在原生搜索里搜到（例如搜「瑞幸」）。

---

## 7. 数据来路（便于后续扩量/复现）

原始数据（手机 Termux，`~/poi-work/`）：

| 源 | 位置 | 内容 | 许可 |
|---|---|---|---|
| `Wadesha/china-brand-poi-maps` | `china-brand-poi-maps-main.zip` → `data/poi_data/*.json` | 56 品牌 / 66 城 / 205,228 条，采集 **2026-05**，坐标 **GCJ-02**；其中 **30,047 条无坐标被跳过** | 无（腾讯/高德接口采集）→ 仅个人自用 |
| `tuansuwu/china-5a-scenic-areas` | `china-5a-scenic-areas-main.zip` → `data/*.csv` | 373 个国家 5A 景区，坐标 **WGS-84** | **CC BY-SA 4.0** |
| `Pyjacc/data-poi` | `data-poi-main.zip` | 全国省会城市 POI（高德，2022-09），按城市/区县 xlsx | 无 |
| `wangunji/POI-data-of-China` | `POI-data-of-China-main.zip` | 百度 2020，按城市×6 大类 | 无 |

转换脚本：`tools/build.py`（纯标准库 Python 3，本目录已附）

```bash
python3 build.py          # 全国品牌 + 5A
python3 build.py --xian   # 只要西安
```

脚本做了三件事：
1. **GCJ-02 → WGS-84**（标准算法，`gcj2wgs()`，已用天安门基准点校验误差 ~5 m）；
2. 高德中文分类 → OSM 标签（`amenity=cafe/restaurant/fast_food`、`shop=convenience/supermarket`、`tourism=hotel` 等），
   映射表在 `CAT_MAP`，要加类目改这里；
3. 输出 `.kml` / `.gpx`（给 CoMaps / OsmAnd 当书签用，已验证可直接导入）+ `.osm`（给 OMC 生成 obf）。

**要点**：所有进 OsmAnd 的坐标都必须先转成 **WGS-84**，否则在 OSM 底图上会整体偏移 300–500 m。

---

## 8. 边界与注意事项

- 本任务只做「本地文件 → obf」，**不联网抓取**、不碰任何地图服务 API。
- `inputs/` 的 XML 不要手工编辑（转义很脆）；要改内容请改 `tools/build.py` 重新生成。
- 生成的 obf 仅供本人设备使用；品牌类数据无授权，**不要再分发**。
- 做完请把这台机器上的临时文件清掉（若你自己建了工作目录）。

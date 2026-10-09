# 构建记录：poi-handoff → .poi.obf（已完成）

> 执行方：laptop（Windows，<laptop-host>）· 执行时间：2026-09-16 11:47–12:00 CST
> 依据：`HANDOFF.md`

## 结果

3 个 `.poi.obf` 已生成并放在 `output/`：

| 文件 | 大小 (bytes) | MD5 | POI INDEX SIZE (log) | 匹配 handoff 预期 |
|---|---|---|---|---|
| `Xian.obf` | 1,973,126 | `0f7da5bf834e5c83d525a89944598999` | 1,973,108 | ✅ 与 `sample/Xian.obf` 大小完全一致 |
| `China5a.obf` | 280,034 | `a57d9f7f8af9c8f8bdea8a735b0ab83e` | 280,016 | ✅ ~274 KB |
| `Chinabrands.obf` | 115,406,700 | `190a3ce9bebfbe7dc98058335b7372b3` | 115,406,682 | ✅ 十 MB 级 |

三份都跑出 `Poi processing finished` + `Finish writing binary file`，无 `OutOfMemoryError`、无 `XmlPullParserException`。

## 实际执行方式（与 handoff 第 4 节的差异）

- **Java**：不需要下载 Temurin。本机已有 **Microsoft OpenJDK 21.0.12**
  （`C:\Program Files\Microsoft\jdk-21.0.12.8-hotspot`）。
  注意：PATH 里默认的 `java` 是 **1.8.0_501**，直接用 `utilities.bat` 会因 class 版本 61 报错，
  所以用了一层 wrapper 把 JDK 21 放到 PATH 最前面再调 `utilities.bat`。
- **工作目录**：`D:\omc-work`（D: 有 120 GB 空闲；C: 当时仅剩 5.9 GB），未用 WSL。
- **OsmAndMapCreator**：`OsmAndMapCreator-main.zip`，151,362,722 bytes，
  `Last-Modified: 2026-09-16 01:27:46 GMT`（即 handoff 说的 night-build），解包 244 个文件 / 394 MB。
- **命令**（3 份相同参数）：
  ```
  JAVA_OPTS=-Xms512M -Xmx8G
  utilities.bat generate-poi <Xian|China5A|ChinaBrands>.osm --chars-build-poi-nameindex=3
  ```
- 输入文件先复制成短名（`Xian.osm` / `China5A.osm` / `ChinaBrands.osm`），
  输出名由文件名派生：`Xian.obf` / `China5a.obf` / `Chinabrands.obf`。
- 耗时：China5A ≈ 1 s，Xian ≈ 1 s，ChinaBrands ≈ 2 min。

## 验证

`inspector.bat` 对三份都通过：

```
Binary index Xian.obf version = 2 edition = Wed Sep 16 11:48:58 CST 2026
1 POI data Xian - 1,973,108 bytes
Binary index China5a.obf  ... 1 POI data China5a  -   280,016 bytes
Binary index Chinabrands.obf ... 1 POI data Chinabrands - 115,406,682 bytes
```

名字索引（手机上按名搜索的前提）已建立，以 `China5a.obf` 为例（`inspector -vpoi`）：

- `tourism (1, 373): [attraction (373)]` —— 373 个 5A 景区全部入库
- `POI Additionals: Text based (3, 1,119): [brand (373), name (373), name:en (373)]`
- `POI Name index stats (839 prefixes, 10,632 tokens, 3,841 refs/atoms)`

## 收尾

临时工作目录 `D:\omc-work`（含 zip、解包文件、日志、wrapper bat）**已删除**。
输入 `inputs/*.osm` 未做任何修改。

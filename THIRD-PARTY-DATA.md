# 第三方数据来源与许可

本仓库**不包含**下列数据本体（体积大、且多数无授权），只提供拉取脚本与转换代码。
`scripts/fetch-data.sh` 会把它们下载到 `.gitignore` 覆盖的目录里。

| # | 上游仓库 | 拉取到 | 内容 | 采集时间 | 坐标系 | 许可 | 可否再分发 |
|---|---|---|---|---|---|---|---|
| 1 | `Wadesha/china-brand-poi-maps` | `brand/` | 56 个连锁品牌 / 66 城 / 205,228 条（其中 30,047 条无坐标被跳过） | 2026-05 | GCJ-02 | **无** | ❌ 仅个人自用 |
| 2 | `tuansuwu/china-5a-scenic-areas` | `a5a/` | 全国 373 个 5A 级景区 | — | WGS-84 | **CC BY-SA 4.0** | ✅ 署名 + 同许可 |
| 3 | `Pyjacc/data-poi` | `pyjacc/` | 全国省会城市 POI（高德），按城市/区县 xlsx，共 1,098 个文件 | 2022-09 | GCJ-02 | **无** | ❌ |
| 4 | `wangunji/POI-data-of-China` | `baidu/` | 百度 POI，按城市 × 6 大类 | 2020 | GCJ-02 | **无** | ❌ |

## 怎么拉

```bash
bash scripts/fetch-data.sh          # 全部
bash scripts/fetch-data.sh brand    # 只拉某一份（参数 = sources.tsv 第一列）
```

`scripts/sources.tsv` 是这张表的机器可读版本（上游 → 目标目录 → 许可 → 说明），
加新数据源只需要在那张表里加一行，脚本本身不用改。

## 为什么不让它们进仓库

1. **许可**：#1/#3/#4 上游**没有 LICENSE**（默认版权保留），而且这类数据多来自高德/百度接口，
   本身还叠加了地图服务的使用条款 ⇒ 公开仓库里再分发不合适。
2. **体积**：#3 解包后约 678 MB、#4 约 230 MB、#1 约 59 MB；GitHub 单文件上限 100 MB。

## 仅有的例外

`samples/china-5a-scenic-areas.csv`（101 KB）是 #2 的原始 CSV，随仓库一起分发，
因为它的许可是 **CC BY-SA 4.0**：可以再分发，条件是**署名 + 相同许可**。
该文件旁的 `samples/LICENSE.china-5a-scenic-areas` 就是上游的 LICENSE 原文，请一并保留。

`samples/` 里的 `xian.*` / `china-5a.*`（KML/GPX/OSM）是转换产物：
其中西安/品牌部分由 #1 生成 ⇒ 同样**不要再分发**；5A 部分由 #2 生成 ⇒ 继承 CC BY-SA 4.0。
之所以还是放进仓库，是因为它们只有几百 KB、且是验证格式正确性的最小样本。

## 转换后坐标系的说明

- GCJ-02 → WGS-84 用标准算法（`build.py` 里的 `gcj2wgs()`），
  以天安门为基准点校验，**经度误差约 5 m**（城内约 1–2 m）。
- 5A 景区数据**本来就是 WGS-84**，脚本对它不做转换。

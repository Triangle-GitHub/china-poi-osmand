# scripts/legacy —— 当年的笔记本(WSL)一次性脚本

这些脚本是 2026-09 那次真实交接里，**在笔记本(Windows + WSL2 Ubuntu)上**用过的临时脚本，
一次任务结束后就不再需要了。它们留在这里只有一个目的：**把过程完整记录下来**，
方便别人（或未来的自己）复现「在 Windows/WSL 上跑 OsmAndMapCreator」这条路。

| 脚本 | 当时的作用 |
|---|---|
| `probe.sh` | 探测环境：有没有 bash/Java/Python/网络、能否装 JDK |
| `laptop_setup.sh` | 在 `/tmp/omc-poi-china` 里装 Temurin JDK 21 + 解包 OsmAndMapCreator |
| `laptop_build.sh` | 批量 `generate-poi` 生成 3 个 `.obf` |
| `laptop_all.sh` | 上面三步一体化（WSL 空闲会关停，必须一次跑完） |
| `laptop_where.sh` | 定位 scp 进来的文件在 WSL 里的真实路径 |
| `laptop_diag.sh` | 出问题时的诊断（挂载点/空间/是否刚重启） |
| `laptop_cleanup.sh` | 收尾：杀掉自己起的进程、删临时目录 |
| `unpack_handoff.sh` | 在 WSL 里解包交接包到 Windows 家目录 |

⚠️ 注意：

- 这些脚本里写死了当时的用户名与临时目录，已按 `SCRUB-NOTES.md` 用 `<user>` 之类的占位符替换，
  **不能直接原样运行**，请按自己的环境改路径。
- 真正还值得复用的逻辑（下载 JDK / 解包 OMC / 调 `utilities.sh generate-poi --chars-build-poi-nameindex=3`）
  已经写进仓库根目录的 `README.md`，优先看那里。

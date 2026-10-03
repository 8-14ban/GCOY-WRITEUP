# GCOY-WRITEUP

CTF writeup 沉淀工具。零依赖，单文件，Python 3.10+。

从比赛中的临时记录，到可复盘、可统计、可导出战报的完整链路。

## 安装

```bash
git clone https://github.com/8-14ban/GCOY-WRITEUP.git
```

无第三方依赖，直接运行。

## 快速开始

```bash
# 比赛中随手开一张记录卡
python3 gcoy_writeup.py new "ezywaf-bypass" --cat web --pts 200 --event "TestCTF"

# 解出后落 flag，自动标记 solved
python3 gcoy_writeup.py done 0001 --flag "flag{...}"

# 看板与统计
python3 gcoy_writeup.py list
python3 gcoy_writeup.py stats

# 导出单文件 HTML 战报（可挂 GitHub Pages）
python3 gcoy_writeup.py export --out report.html
```

## 子命令

| 命令 | 说明 |
| --- | --- |
| `new <标题> --cat web --pts 200 --event 赛事名` | 生成 Markdown 模板（题目描述/思路/步骤/FLAG/复盘） |
| `done <ID> --flag flag{...}` | 写入 flag，状态置 solved，同步 index 与正文 |
| `edit <ID> --title ... --cat ... --pts ... --event ...` | 修改元数据，同步 index 与 Markdown 正文 |
| `list` | 全部题目一览表 |
| `stats` | 按分类统计 solved 率与得分，给出薄弱分类建议 |
| `export --out report.html` | 单文件 HTML 战报，折叠式阅读 |
| `selftest` | 全流程自检 |

分类支持：`web / pwn / reverse / crypto / misc / forensics / osint`。

## 数据结构

```
writeups/
  index.json          # 序号与元数据汇总
  0001-ezywaf-bypass.md
  0002-rot-riddle.md
```

每篇 writeup 是纯 Markdown，头部为元数据表，可直接被任何 Markdown 工具读取。

## 设计原则

- 纯本地离线，数据完全自持（Markdown + JSON）
- 零第三方依赖，单文件可随身携带
- `stats` 输出薄弱分类，用于决定赛后主攻方向

## 自检

```bash
python3 gcoy_writeup.py selftest
```

# 星露谷物语存档管理工具

[English](README.md) | [Português](README.pt.md) | [Español](README.es.md) | [日本語](README.jp.md)

这是一个用于查看和安全编辑《Stardew Valley》存档信息的 Windows 桌面工具。它使用 Windows 标准存档位置；使用 Release 中的程序时无需安装 Python。

## 下载

请从最新的 [GitHub Release](https://github.com/fyihang/StardewValleyTool/releases) 下载 `StardewValleySaveManager.exe`。Release 中的可执行文件无需安装 Python。

## 可编辑内容

- 角色名称
- 农场名称
- 最喜爱的事物
- 已有动物的名称，包括存在时的马名称
- 通过下拉框编辑已有农场工人的角色名称和最喜爱的事物（农场名称仅由房主设置）

界面支持英文、简体中文、葡萄牙语、西班牙语和日语切换。界面会翻译动物种类；未知的模组动物种类则保留其游戏内原始名称。

## 存档保护机制

程序启动时会搜索 Windows 标准存档目录：

```text
%appdata%\StardewValley\Saves
```

如需使用其他位置，请点击“选择存档目录”。该选择只在本次运行期间有效，不会写入配置；下次启动仍从标准目录开始。

只有同时包含 `SaveGameInfo` 和“与文件夹同名主存档文件”的目录才会被识别为有效存档。房主在两个文件中共有的信息会同步写入两个文件；农场工人与动物仅修改保存这些记录的主存档。

写入前，程序会将两个文件备份到该存档文件夹中的 `.svt-backups/<UTC 时间戳>/`。它先校验临时 XML，再替换原文件，并在写后重新读取核验。写入过程中发生错误时，程序会从备份恢复两个原始文件。

## 使用方法

1. 完全关闭《Stardew Valley》。
2. 启动 `StardewValleySaveManager.exe`。
3. 在左侧列表选择存档。
4. 编辑房主字段；存在农场工人时可从下拉框选择其角色；双击动物名称可以重命名。
5. 点击“保存修改”，并确认游戏已经关闭。

首次使用时，建议先复制一个存档文件夹并在副本上测试。确认游戏内存档正常前，请保留程序生成的 `.svt-backups` 备份目录。

## 从源代码运行

安装 Python 3.11 或更高版本后，在仓库根目录运行：

```powershell
$env:PYTHONPATH = "src"
python src\__main__.py
```

## 许可证

本项目采用 [MIT License](LICENSE)。

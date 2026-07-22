# 星露谷物语存档管理工具

[English](README.md)

这是一个用于安全读取和编辑《Stardew Valley》指定存档信息的 Windows 桌面工具。

## 安全机制

- 程序使用 `%appdata%\StardewValley\Saves` 定位存档，不写入任何用户名或本机专用路径。
- 只有同时包含 `SaveGameInfo` 与“目录同名主存档文件”的子目录才会被识别为有效存档。
- 角色名、农场名、最喜爱的事物和已存在的马名称会同步修改两个 XML 文件。
- 动物名称仅修改主存档中既有 `FarmAnimal` 记录的名称。
- 每次保存前，两个文件都会备份至所选存档目录中的 `.svt-backups/<UTC 时间戳>/`。
- 程序先校验临时 XML，再覆盖原文件；写后重新读取核验。发生错误时，两个原始文件都会恢复。

编辑前必须关闭游戏，并应先在复制的存档上测试。

## 从源代码启动

需要 Python 3.11 或更高版本。在仓库根目录运行：

```powershell
$env:PYTHONPATH = "src"
python -m stardew_save_manager
```

可通过界面语言选择器在英文与简体中文间切换。

## 发布策略

自动化测试、PyInstaller 打包脚本、构建目录和 `.exe` 在开发期间仅保留本地。只有在用户完成实际测试并确认通过后，才会发布 Release 产物。

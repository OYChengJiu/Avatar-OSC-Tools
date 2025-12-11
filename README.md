# VRC OSC 快捷键面板

## 功能
- OSC 目标快捷配置（IP/端口/地址前缀）。
- 12 个按键 (1-9,0,-,+) 映射到 Emote1-12，状态可视化。
- 两种模式：
  - 长按模式：按下=开启，松开=关闭。
  - 切换模式：单击切换开启/关闭。
- 表情叠加：允许/禁用多个按键同时开启。
- 后台捕捉：是否在窗口非激活时捕捉全局按键。

## 运行
```bash
python main.py
```

## 打包（示例使用 PyInstaller）
已提供 `VRCBoolHotkeys.spec` 和 `file_version_info.txt`（含作者 OY橙子 的版本资源），可直接用 spec 打包：
```bash
pyinstaller VRCBoolHotkeys.spec
```
或直接打包主程序（不含版本资源示例）：
```bash
pyinstaller -F -w -n VRCBoolHotkeys main.py
```
生成文件位于 `dist/` 目录。

## 快捷键对应
- 1-9, 0, -, + 分别对应 Emote1-Emote12。
- 按键动作会通过 OSC 发送 True/False 到 `/avatar/parameters/<参数名>`。

## 注意
- 关闭“后台捕捉”后，仅窗口聚焦时生效。
- 关闭“表情叠加”时，开启新键会自动关闭已开启的其他键。
- 切换回“长按模式”时，会立刻同步物理按键，避免卡住在开启状态。

# 证书同步记录（2026-10-09）

## 来源和适用范围

- ChatSubmod `f1f2315`（2026-10-08）：附带 `cacert.pem`。MTTS 独立安装也通过 Requests 使用 MAS 的 certifi，因此同步同一份 CA bundle；不覆盖 MAS 的 Python 模块。
- ChatSubmod `5155962`（2026-10-09）：声明 CertifiFixer 依赖，在发布时下载最新 Release 并打包。MTTS 同步这部分，让独立安装也包含修复器。依赖源码不放进本仓库。
- ChatSubmod `ce0febf`（2026-10-09）：清理旧证书下载器的重启状态和对话。MTTS 没有对应下载器、状态或对话，无需移植删除操作。

MTTS 的网络库初始化由 `init -100` 调整为 `init -99`，保证在 CertifiFixer 的 `init -100` 修复之后、MTTS UI 的 `init -1` 之前运行。保留已有节点选择与 TLS 校验，不移植 Chat 专用的 provider 2 回退逻辑。

## 核对依据

- 随包 CA 来源：ChatSubmod `f1f2315` 的 `game/python-packages/certifi/cacert.pem`，共 131 张可加载 CA；复制时的文件 SHA256 为 `54913c500d5d0da7b2e97fdd185c0cec93dabf9a4d2cecf16102626288f2871b`（工作区 CRLF 字节）。
- CertifiFixer：核对了 2026-10-09 发布的 `1.0.1` Release 压缩包，其修复脚本在 MAS 的 certifi 导入状态为失败时，从随包文件复制到 `renpy.config.gamedir/python-packages/certifi/`。
- MAS 默认分支 `6318b0013924d06d1a30a5784b68b7eed5f4b32d`：复用本地上游仓库，核对 `0imports.rpy` 和 `zz_submods.rpy`。
- 中文 MAS 默认分支 `d384fd42ba7a65bbe81598dc7a1f52f6dbef9940`：本地缺少该提交，按提交读取 `0imports.rpy`。
- 移动版 `mobile-dev` 的 `0dcaeb84527c5457bb2280d3d33826884305c0a5`：复用本地仓库，核对 `0imports.rpy`。

## 边界

MAS 的 `mas_can_import.certifi()` 只返回已缓存的导入状态，并不会重新导入模块。CertifiFixer 复制文件后也不重载已导入的模块，因此修复后仍可能需要重启；MTTS 不新增运行时证书下载或模块重载。仅缺少 CA 文件时，修复器未必触发，所以仍需直接随包提供 `cacert.pem`。

CertifiFixer `1.0.1` 自带的 `core.py` 在原生更新路径使用 Python 3 的 `http.client` 和 `ssl.SSLCertVerificationError`；旧 Python 环境下该更新路径的兼容性不由本次同步保证。修复器的复制操作也没有回滚或完整异常隔离。发布流程与 Chat 一致获取最新 Release，后续依赖版本的兼容性仍需验证。

源码安装需要另外安装 CertifiFixer；正式发布工作流会自动下载并检查四个必需文件后打包。测试覆盖证书加载、依赖声明、初始化顺序与打包约束；没有代替实际 MAS / Ren'Py 游戏运行验证。

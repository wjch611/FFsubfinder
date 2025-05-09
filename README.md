## ffsubfinder

`ffsubfinder` 是一个集成 **被动子域名枚举**、**HTTP 存活探测** 以及 **FFUF 子域名猜解** 的 Python 自动化脚本。它能够批量处理域名列表，对每个域名执行子域名发现、存活验证、fuzz 发现，并最终合并去重有效子域名。

------

### 功能

1. 调用 [subfinder](https://github.com/projectdiscovery/subfinder) 被动枚举子域名。
2. 调用 [httpx](https://github.com/projectdiscovery/httpx) 对被动枚举结果做存活检测。
3. 调用 [ffuf](https://github.com/ffuf/ffuf) 基于字典对子域名进行 fuzz，过滤掉高频默认响应大小。
4. 合并 `httpx` 和 `ffuf` 输出，去重后输出最终子域名列表。
5. 自动清理中间结果文件。

------

### 前提条件

- Windows 环境。
- 安装有 Python 3.6+。
- 已下载并配置好以下可执行文件，并确保脚本中对应路径正确：
  - `subfinder.exe`
  - `go_httpx.exe` 或 `httpx.exe`
  - `ffuf.exe`
- 已准备以下字典文件：
  - `ua.txt`：User-Agent 列表。
  - `subnames_next.txt`：子域名 fuzz 字典。

------

### 安装与配置

1. 克隆或下载本项目到本地：

   ```powershell
   git clone https://your-repo-url/ffsubfinder.git
   cd ffsubfinder
   ```

2. 安装必要的 Python 依赖（如果存在第三方库需求）：

   ```powershell
   pip install -r requirements.txt
   ```

3. 修改脚本顶部的路径配置，确保可执行文件和字典文件路径正确：

   ```python
   SUBFINDER_PATH = r"E:\SecTools\passive_subdomain\subfinder.exe"
   HTTPX_PATH      = r"E:\SecTools\httpx_1.6.10_windows_amd64\go_httpx.exe"
   FFUF_PATH       = r"E:\SecTools\ffuf\ffuf.exe"
   UA_LIST_PATH    = r"E:\SecTools\dict\ua.txt"
   SUBNAME_DICT_PATH = r"E:\SecTools\dict\domain_dict\subnames_next.txt"
   OUTPUT_DIR      = r"E:\SecTools\ffsubfinder"
   ```

4. 确保 `OUTPUT_DIR` 指定的目录可写。

------

### 使用方法

1. 将要扫描的域名列表保存到 `domains.txt`，每行一个域名，例如：

   ```txt
   example.com
   testsite.org
   ```

2. 执行脚本：

   ```powershell
   python ffsubfinder.py -u domains.txt
   ```

3. 脚本完成后，结果文件会生成在 `OUTPUT_DIR` 目录下，每个域名对应一个 `.txt` 文件，包含已去重的存活子域名。

------

### 参数说明

- `-u, --urls`: 指定包含域名列表的文件路径（必选）。

------

### 自定义调整

- **线程数、超时等可在脚本 `run_command` 调用中修改**。
- **高频响应大小过滤阈值**：在 `extract_urls_from_ffuf_json` 函数中修改 `max_common_size_count` 值。

------

### 示例

```powershell
# 扫描 domains.txt 中的所有域名
python ffsubfinder.py -u C:\path\to\domains.txt

# 完成后查看结果
type E:\SecTools\ffsubfinder\example.com.txt
```

------

### 许可证

MIT License © 2025
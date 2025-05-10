1. # ffsubfinder - 子域名发现工具

   `ffsubfinder` 是一个结合被动和主动方式的子域名发现工具，基于 Subfinder、HTTPX 和 FFUF 实现。它通过被动枚举（Subfinder + HTTPX）和主动探测（FFUF）来发现目标域名的子域名，并对结果进行过滤以去除常见响应特征的无效子域名。

   ## 功能

   - **被动子域名发现**：使用 Subfinder 收集子域名，并通过 HTTPX 验证其有效性。
   - **主动子域名探测**：使用 FFUF 进行基于字典的子域名爆破。
   - **结果过滤**：通过响应状态码、响应长度和词数过滤掉常见的无效子域名。
   - **伪重定向过滤**：识别并过滤 HTTPX 返回状态码为 200 但实际发生重定向的子域名（需优化）。
   - **随机 User-Agent**：支持从用户代理列表中随机选择 User-Agent，增强探测隐蔽性。
   - **结果去重与整理**：合并被动和主动发现的子域名，输出整理后的结果。

   ## 依赖工具

   - **Subfinder**（v2.7.0）：用于被动子域名枚举。
   - **HTTPX**（v1.6.10）：用于验证子域名的有效性并获取响应信息。
   - **FFUF**：用于主动子域名爆破。
   - **Python 3.8+**：运行脚本所需环境。

   ## 安装

   1. **安装依赖工具**：

      - 下载并安装 Subfinder、HTTPX 和 FFUF，确保它们在系统 PATH 中或配置正确路径。
      - 示例路径：
        - Subfinder: `E:\SecTools\passive_subdomain\subfinder_2.7.0_windows_amd64\subfinder.exe`
        - HTTPX: `E:\SecTools\httpx_1.6.10_windows_amd64\go_httpx.exe`
        - FFUF: `E:\SecTools\ffuf\ffuf.exe`

   2. **准备字典文件**：

      - 用户代理列表：`E:\SecTools\dict\ua.txt`（每行一个 User-Agent）。
      - 子域名字典：`E:\SecTools\dict\domain_dict\subnames_next.txt`（每行一个子域名前缀）。

   3. **安装 Python 依赖**：

      ```bash
      pip install -r requirements.txt
      ```

      （如果需要，创建 `requirements.txt` 包含 `argparse` 等标准库无需额外安装）。

   4. **配置输出目录**：

      - 默认输出目录：`E:\SecTools\ffsubfinder`。
      - 确保目录存在或具有写权限。

   ## 使用方法

   1. **准备域名列表**：
      创建一个 `domains.txt` 文件，每行一个目标域名，例如：

      ```
      example.com
      test.com
      ```

   2. **运行脚本**：

      ```bash
      python ffsubfinder.py -u domains.txt
      ```

      - `-u` 或 `--urls`：指定包含目标域名的文件路径。

   3. **输出结果**：

      - 每个域名的最终子域名列表保存到 `E:\SecTools\ffsubfinder\<domain>.txt`。
      - 中间文件（如 Subfinder、HTTPX、FFUF 输出）会在处理完成后自动删除。

   ## 示例

   ```bash
   python ffsubfinder.py -u domains.txt
   ```

   **输出示例**：

   ```
   [+] Processing example.com ...
   [*] 开始解析 HTTPX 输出...
   [+] sub1.example.com | 状态: 200 | 词数: 1000 | 长度: 5000
   [+] sub2.example.com | 状态: 200 | 词数: 800 | 长度: 4500
   [*] 常见响应特征 (将被过滤): {(404, 200, 1000)}
   [+] 最终保留 2 个域名
   [+] Done: example.com
       └── Final : E:\SecTools\ffsubfinder\example.com.txt
   ```

   ## 输出文件

   - **`example.com.txt`**：包含去重后的子域名列表（被动 + 主动）。

   - 每行一个子域名，例如：

     ```
     sub1.example.com
     sub2.example.com
     ```

   ## 注意事项

   1. **工具路径**：确保 `SUBFINDER_PATH`、`HTTPX_PATH` 和 `FFUF_PATH` 配置正确。
   2. **字典质量**：子域名字典的质量直接影响 FFUF 的探测效果。
   3. **伪重定向过滤**：当前脚本未完全实现伪重定向过滤（HTTPX 返回 200 但实际重定向）。可参考以下优化建议。
   4. **性能**：HTTPX 和 FFUF 的线程数、速率限制等参数可根据需要调整。
   5. **清理**：中间文件会在每次运行后自动删除，确保磁盘空间充足。

   ## 优化建议

   - 伪重定向过滤

     ：

     - 检查 HTTPX 输出中的 `input` 和 `url` 字段，若不同则表示重定向。

     - 添加正则规则过滤重定向到登录页、404 页等无用页面（例如 `/login`、`/error`）。

     - 示例：

       ```python
       if input_url != final_url and re.search(r"/login|/error", final_url):
           continue
       ```

   - **并行处理**：使用 `concurrent.futures` 并行处理多个域名，提升效率。

   - **日志记录**：将 `print` 替换为 `logging` 模块，支持日志级别和文件输出。

   - **动态配置**：通过命令行参数支持自定义线程数、速率限制等。

   ## 贡献

   欢迎提交问题或优化建议！请通过 GitHub Issues 或 Pull Requests 反馈。

   ## 许可证

   本项目采用 MIT 许可证。详情见 `LICENSE` 文件。
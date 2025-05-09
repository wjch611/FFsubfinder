import os
import subprocess
import random
import json
from pathlib import Path
from collections import Counter
import re

# 配置路径
SUBFINDER_PATH = r"E:\SecTools\passive_subdomain\subfinder_2.7.0_windows_amd64\subfinder.exe"
HTTPX_PATH = r"E:\SecTools\httpx_1.6.10_windows_amd64\go_httpx.exe"
FFUF_PATH = r"E:\SecTools\ffuf\ffuf.exe"
UA_LIST_PATH = r"E:\SecTools\dict\ua.txt"
SUBNAME_DICT_PATH = r"E:\SecTools\dict\domain_dict\subnames.txt"
OUTPUT_DIR = r"E:\SecTools\ffsubfinder"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_user_agents(path):
    with open(path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def get_random_user_agent(ua_list):
    return random.choice(ua_list)

def run_command(cmd, shell=False):
    try:
        subprocess.run(cmd, shell=shell, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] Command failed: {' '.join(cmd)}")
        print(e)

def extract_urls_from_ffuf_json(ffuf_file, domain, max_common_size_count=5):
    try:
        with open(ffuf_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            results = data.get('results', [])

            sizes = [entry.get('length') for entry in results]
            size_counter = Counter(sizes)
            common_sizes = {size for size, count in size_counter.items() if count >= max_common_size_count}

            filtered_urls = []
            for entry in results:
                sub = entry['input']['SUB']
                size = entry.get('length')
                if size not in common_sizes:
                    filtered_urls.append(f"{sub}.{domain}")
            return filtered_urls
    except Exception as e:
        print(f"[!] Error parsing FFUF JSON: {ffuf_file}")
        print(e)
        return []

def clean_httpx_urls(urls):
    clean_urls = set()
    for url in urls:
        # 匹配并提取跳转后的真实域名
        match = re.match(r"https?://(?:www\.)?([a-zA-Z0-9.-]+)", url)
        if match:
            clean_urls.add(match.group(1))
    return clean_urls

def main(domains_file):
    ua_list = load_user_agents(UA_LIST_PATH)

    with open(domains_file, 'r', encoding='utf-8') as f:
        domains = [line.strip() for line in f if line.strip()]

    for domain in domains:
        print(f"\n[+] Processing {domain} ...")

        subfinder_output = Path(SUBFINDER_PATH).parent / f"{domain}.txt"
        httpx_output = Path(HTTPX_PATH).parent / f"passive_{domain}.txt"
        ffuf_output = Path(FFUF_PATH).parent / f"ffuf_{domain}.json"
        final_output_path = Path(OUTPUT_DIR) / f"{domain}.txt"

        # subfinder
        run_command([SUBFINDER_PATH, "-d", domain, "-o", str(subfinder_output), "-all"])

        # httpx
        run_command([HTTPX_PATH, "-l", str(subfinder_output), "-threads", "10", "-rate-limit", "30",
                     "-random-agent", "-timeout", "5", "-retries", "2", "-follow-redirects",
                     "-o", str(httpx_output)])

        # ffuf
        random_ua = get_random_user_agent(ua_list)
        ffuf_cmd = [
            FFUF_PATH,
            "-w", f"{SUBNAME_DICT_PATH}:SUB",
            "-H", f"User-Agent: {random_ua}",
            "-u", f"https://SUB.{domain}",
            "-t", "10",
            "-rate", "20",
            "-timeout", "5",
            "-p", "0.3",
            "-o", str(ffuf_output),
            "-of", "json",
            "-mc", "all"
        ]
        run_command(ffuf_cmd)

        # 合并 & 去重
        try:
            httpx_urls = set()
            if httpx_output.exists():
                with open(httpx_output, 'r', encoding='utf-8') as f:
                    httpx_urls = set(line.strip() for line in f if line.strip())

            ffuf_urls = set(extract_urls_from_ffuf_json(ffuf_output, domain))

            # 清理httpx中的URL：过滤跳转到www的URL并提取真实域名
            cleaned_httpx_urls = clean_httpx_urls(httpx_urls)
            all_urls = sorted(cleaned_httpx_urls.union(ffuf_urls))

            with open(final_output_path, 'w', encoding='utf-8') as f_out:
                for url in all_urls:
                    f_out.write(url + "\n")

            print(f"[+] Done: {domain} -> {final_output_path}")
        except Exception as e:
            print(f"[!] Error merging results for {domain}")
            print(e)

        # 清理中间文件
        for path in [subfinder_output, httpx_output, ffuf_output]:
            if path.exists():
                path.unlink()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ffsubfinder - passive+active subdomain discovery")
    parser.add_argument("-u", "--urls", required=True, help="Path to domains.txt file")
    args = parser.parse_args()

    main(args.urls)

import requests

import os
import requests

def get_files_in_dataset(dataset_repo, revision="main"):
    """获取数据集下所有文件名"""
    api_url = f"https://huggingface.co/api/datasets/{dataset_repo}/tree/{revision}"
    resp = requests.get(api_url, timeout=30)
    resp.raise_for_status()
    tree = resp.json()
    files = []
    def collect_files(items, prefix=""):
        for item in items:
            if item["type"] == "file":
                files.append(prefix + item["path"])
            elif item["type"] == "dir":
                collect_files(item.get("siblings", []), prefix + item["path"] + "/")
    collect_files(tree)
    return files

def get_cdn_url(dataset_repo, revision, file_path):
    """多次跳转获得某文件的 CDN 直链"""
    u1 = f"https://huggingface.co/datasets/{dataset_repo}/resolve/{revision}/{file_path}"
    r1 = requests.get(u1, allow_redirects=False)
    rel = r1.headers.get("location")
    if not rel:
        raise Exception(f"Failed to get redirect for {u1}")
    u2 = "https://huggingface.co" + rel
    r2 = requests.get(u2, allow_redirects=False)
    cdn_url = r2.headers.get("location")
    if not cdn_url:
        raise Exception(f"Failed to get CDN URL for {file_path}")
    return cdn_url

# 用例：下载 SWE-rebench 数据集所有 parquet 文件
DATASET = "nebius/SWE-rebench"
REVISION = "main"
SAVE_DIR = "downloads"

os.makedirs(SAVE_DIR, exist_ok=True)

# 获取所有文件，举例只下载 data/ 目录下的 .parquet 文件
files = get_files_in_dataset(DATASET, revision=REVISION)
target_files = [f for f in files if f.startswith("data/") and f.endswith(".parquet")]

for f in target_files:
    print("准备下载:", f)
    cdn_url = get_cdn_url(DATASET, REVISION, f)
    print("直链:", cdn_url)
    # 下载文件
    resp = requests.get(cdn_url, stream=True)
    save_path = os.path.join(SAVE_DIR, os.path.basename(f))
    with open(save_path, "wb") as out:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                out.write(chunk)
    print(f"已保存: {save_path}")


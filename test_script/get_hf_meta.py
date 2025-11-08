#!/usr/bin/env python3
"""
Simple test script to get models and datasets information from Hugging Face API
"""

import requests
import json
from typing import Dict, List, Any


def get_models_info(limit: int = 5) -> List[Dict[str, Any]]:
    """Get information about models from Hugging Face API"""
    url = "https://huggingface.co/api/models"
    params = {
        "limit": limit,
        "sort": "downloads",
        "direction": -1
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching models: {e}")
        return []


def get_datasets_info(limit: int = 5) -> List[Dict[str, Any]]:
    """Get information about datasets from Hugging Face API"""
    url = "https://huggingface.co/api/datasets"
    params = {
        "limit": limit,
        "sort": "downloads",
        "direction": -1
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching datasets: {e}")
        return []


def get_my_ip_and_location() -> dict:
    """
    获取当前机器的公网IP和地理位置。
    使用 ipinfo.io 的免费API。
    """
    url = "https://ipinfo.io/json"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching IP info: {e}")
        return {}


def get_swe_rebench_readme() -> str:
    """
    Fetch the README.md file from the SWE-rebench dataset on Hugging Face.
    等价于 curl -L "https://huggingface.co/datasets/nebius/SWE-rebench/resolve/main/README.md"
    """
    url = "https://huggingface.co/datasets/nebius/SWE-rebench/resolve/main/README.md"
    try:
        response = requests.get(url, allow_redirects=True, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching SWE-rebench README: {e}")
        return ""


def print_json(data: Any):
    """输出完整的json信息"""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def check_hf_cdn_lfs_headers() -> dict:
    """
    检查 Hugging Face CDN LFS 的响应头信息
    等价于 curl -I "https://cdn-lfs.huggingface.co"
    """
    url = "https://cdn-lfs.huggingface.co"
    try:
        response = requests.head(url, timeout=60)
        response.raise_for_status()
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "url": response.url
        }
    except requests.exceptions.RequestException as e:
        print(f"Error checking HF CDN LFS headers: {e}")
        return {}

def main():
    """Main function to test Hugging Face API"""
    print("Testing Hugging Face API...")
    print("=" * 50)
    
    # Get IP and location information
    print("Fetching your IP and location info...")
    ip_info = get_my_ip_and_location()
    if ip_info:
        print("=== MY IP AND LOCATION ===")
        print_json(ip_info)
    else:
        print("Failed to fetch IP info")
    print("=" * 50)
    
    # Check Hugging Face CDN LFS headers
    print("Checking Hugging Face CDN LFS headers...")
    cdn_headers = check_hf_cdn_lfs_headers()
    if cdn_headers:
        print("=== HF CDN LFS HEADERS ===")
        print_json(cdn_headers)
    else:
        print("Failed to check HF CDN LFS headers")
    print("=" * 50)
    
    
    
    


if __name__ == "__main__":
    main()

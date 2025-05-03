#!/usr/bin/env python3
import requests
import re
import json
from colorama import Fore, init
from bs4 import BeautifulSoup

init(autoreset=True)

# Fungsi untuk mendeteksi versi WordPress dari meta tag generator
def detect_wordpress_version(html):
    soup = BeautifulSoup(html, "html.parser")
    generator = soup.find("meta", attrs={"name": "generator"})
    if generator and "WordPress" in generator.get("content", ""):
        return generator["content"].replace("WordPress", "").strip()
    return None

# Fungsi untuk mengekstrak plugin dan tema dari konten halaman
def extract_components(html):
    plugins = sorted(set(re.findall(r"/wp-content/plugins/([a-zA-Z0-9-_]+)/", html)))
    themes = sorted(set(re.findall(r"/wp-content/themes/([a-zA0-9-_]+)/", html)))
    return plugins, themes

# Fungsi untuk memindai kerentanannya menggunakan WPScan API
def scan_wpscan_api(slug, comp_type, token):
    url = f"https://wpscan.com/api/v3/{comp_type}s/{slug}"
    headers = {"Authorization": f"Token token={token}"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
    except:
        return {"error": "Waktu habis (Timeout)"}

    result = {"type": comp_type, "vulnerabilities": []}
    if response.status_code != 200:
        result["error"] = f"HTTP {response.status_code}"
        return result

    data = response.json()
    for vuln in data.get("vulnerabilities", []):
        result["vulnerabilities"].append({
            "title": vuln.get("title"),
            "cve": vuln.get("cve", []),
            "description": vuln.get("description", "")[:150],
            "references": vuln.get("references", {}).get("url", [])
        })
    return result

# Fungsi untuk menampilkan hasil pemindaian
def display_result(name, data):
    print(f"\n{Fore.CYAN}[#] {name.upper()} ({data['type']})")
    if 'error' in data:
        print(f"{Fore.RED}  ! {data['error']}")
    elif not data['vulnerabilities']:
        print(f"{Fore.GREEN}  - Tidak ditemukan kerentanan.")
    else:
        for v in data['vulnerabilities']:
            print(f"{Fore.RED}  - {v['title']}")
            if v['cve']:
                print(f"    CVE : {', '.join(v['cve'])}")
            if v['references']:
                print(f"    URL : {v['references'][0]}")
            print(f"    Deskripsi: {v['description']}...")

# Fungsi utama untuk memindai URL dan menampilkan hasil
def main():
    print(Fore.YELLOW + "=== WPScan CLI Interaktif ===")
    url = input(Fore.CYAN + "[?] Masukkan URL target: ").strip()
    token = input(Fore.CYAN + "[?] Masukkan API Token WPScan: ").strip()

    try:
        print(Fore.BLUE + f"[~] Mengakses: {url}")
        resp = requests.get(url, timeout=10)
        html = resp.text
    except Exception as e:
        print(Fore.RED + f"[!] Gagal akses: {e}")
        return

    version = detect_wordpress_version(html)
    if version:
        print(Fore.GREEN + f"[+] Versi WordPress Terdeteksi: {version}")

    plugins, themes = extract_components(html)
    print(Fore.GREEN + f"[+] Plugin ditemukan: {len(plugins)} | Tema ditemukan: {len(themes)}")

    all_data = {"url": url, "version": version, "plugins": {}, "themes": {}}

    for plugin in plugins:
        data = scan_wpscan_api(plugin, "plugin", token)
        all_data["plugins"][plugin] = data
        display_result(plugin, data)

    for theme in themes:
        data = scan_wpscan_api(theme, "theme", token)
        all_data["themes"][theme] = data
        display_result(theme, data)

    simpan = input(Fore.CYAN + "\n[?] Simpan hasil ke file? (y/n): ").strip().lower()
    if simpan == "y":
        nama_file = input("Nama file (contoh: hasil.json): ").strip()
        with open(nama_file, "w") as f:
            json.dump(all_data, f, indent=2)
        print(Fore.YELLOW + f"[+] Hasil disimpan ke {nama_file}")

if __name__ == "__main__":
    main()

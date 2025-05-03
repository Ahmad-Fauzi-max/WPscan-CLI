#!/data/data/com.termux/files/usr/bin/bash

echo "[*] Memastikan Python & pip tersedia..."
pkg update -y && pkg install -y python git curl

echo "[*] Menginstall dependensi Python..."
pip install --upgrade pip
pip install requests colorama beautifulsoup4

echo "[*] Mengunduh skrip scanner..."
curl -sSL https://raw.githubusercontent.com/usernamekontol/WPscan-CLI/main/cli_wp_scanner.py -o $HOME/cli_wp_scanner.py

echo "[*] Membuat alias 'wpscan-cli'..."
echo 'alias wpscan-cli="python3 $HOME/cli_wp_scanner.py"' >> $HOME/.bashrc
source $HOME/.bashrc

echo "[✓] Instalasi selesai! Jalankan dengan perintah: wpscan-cli"

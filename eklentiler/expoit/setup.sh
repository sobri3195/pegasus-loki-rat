#!/bin/bash

echo "Membuat virtual environment..."
python3 -m venv venv

echo "Mengaktifkan virtual environment..."
source venv/bin/activate

echo "Menginstal dependencies dari requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Setup selesai. Untuk menjalankan pentest, aktifkan venv dan jalankan:"
echo "source venv/bin/activate"
echo "python main.py"

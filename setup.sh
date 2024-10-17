#!/bin/bash

# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и venv
sudo apt install python3 python3-venv python3-pip -y

# Создание виртуального окружения
python3 -m venv venv

# Активация виртуального окружения
source venv/bin/activate

# Установка зависимостей из requirements.txt
pip install -r requirements.txt

# Создание службы systemd для автозапуска приложения
cat << EOF | sudo tee /etc/systemd/system/qrgenerator.service
[Unit]
Description=QR Generator Flask App
After=network.target

[Service]
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/venv/bin/python $(pwd)/main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Перезагрузка демона systemd
sudo systemctl daemon-reload

# Включение и запуск службы
sudo systemctl enable qrgenerator.service
sudo systemctl start qrgenerator.service

echo "Установка завершена. Приложение запущено и добавлено в автозапуск."
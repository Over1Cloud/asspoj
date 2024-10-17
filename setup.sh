#!/bin/bash

# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и pip, если они еще не установлены
sudo apt install python3 python3-pip -y

# Установка зависимостей из requirements.txt
pip3 install -r requirements.txt

# Создание службы systemd для автозапуска приложения
cat << EOF | sudo tee /etc/systemd/system/qrgenerator.service
[Unit]
Description=QR Generator Flask App
After=network.target

[Service]
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(which python3) $(pwd)/main.py
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
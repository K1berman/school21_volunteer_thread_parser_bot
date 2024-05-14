#!/bin/bash

echo "Проверка наличия Python..."
python3_path=$(which python3)

if [ -z "$python3_path" ]; then
    echo "Python не установлен. Установка Python и pip..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv
elses
    echo "Python установлен по пути: $python3_path"
fi

echo "Создание виртуального окружения"
python3 -m venv env

echo "Активация виртуального окружения"
source env/bin/activate

echo "Обновление pip"
python3 -m pip install --upgrade pip

echo "Установка зависимостей"
pip install -r requirements.txt

echo "Запуск парсера"
python3 school21_parser.py

echo "Деактивация виртуального окружения"
deactivate

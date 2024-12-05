import os
import sys
import venv
import subprocess

def create_and_activate_venv():

    if os.path.exists('.venv'):
        activate_env()
        return

    print("Создание виртуального окружения...")
    venv.create('.venv', with_pip=True)

    if sys.platform.startswith('win'):
        activate_script = os.path.join('.venv', 'Scripts', 'activate')
    else:
        print
        activate_script = os.path.join('.venv', 'bin', 'activate')

    activate_env(activate_script)
    print("Virtual environment activated.")

def activate_env(activate_script=None):

    if sys.platform.startswith('win'):
        os.system(f"call {activate_script}")
    else:
        source_command = "source"
        os.system(f"{source_command} {activate_script}")

def install_requirements():

    print("Установка зависимостей с requirements.txt...")
    os.system(f"{sys.executable} -m pip install -r requirements.txt")
    print("Зависимости установлены.")
    print('Установка зависимостей c package.json')
    os.system(f"npm install")
    print("Зависимости установлены.")


def run_main_script(name, prog=True):

    print(f"Запускаю {name}...")
    if prog:
        subprocess.run([sys.executable, name])
    else:
        subprocess.run(name, check=True)

def main():

    create_and_activate_venv()

    if os.path.exists('requirements.txt'):
        install_requirements()
    else:
        print("Виртуальное окружение не найдено!")

    print("Виртуальное окружение установлено!")

    print("Запускаю бота!")

    run_main_script("school21_parser.py")

if __name__ == "__main__":
    main()
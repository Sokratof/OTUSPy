#!/usr/bin/env python3

import subprocess
import sys
import os

# Получаем абсолютный путь к корню проекта
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Список скриптов и команд для их запуска
scripts = [
    ("pytest", os.path.join(project_root, "tests", "test_ocfs_basic.py")),
    ("python3", os.path.join(project_root, "scripts", "create_stand.py")),
    ("pytest", os.path.join(project_root, "tests", "test_perf.py"))
]

for command, script in scripts:
    try:
        print(f"Запуск {command} {script}...")

        # Создаем окружение с добавленным PYTHONPATH
        env = os.environ.copy()
        env["PYTHONPATH"] = project_root

        # Запускаем скрипт с выводом в реальном времени
        with subprocess.Popen(
            [command, script],
            cwd=project_root,  # Запускаем из корня проекта
            env=env,
            stdout=subprocess.PIPE,  # Перехватываем stdout
            stderr=subprocess.STDOUT,  # Перенаправляем stderr в stdout
            text=True,  # Работаем с текстом (Python 3.7+)
            bufsize=1  # Буферизация построчно
        ) as proc:
            for line in proc.stdout:
                print(line, end="")  # Выводим каждую строку в реальном времени

        # Ждём завершения процесса и проверяем код завершения
        proc.wait()  # Убедимся, что процесс завершился
        if proc.returncode != 0:
            print(f"Ошибка в {script}: процесс завершился с кодом {proc.returncode}", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Ошибка при запуске {script}: {e}", file=sys.stderr)
        sys.exit(1)

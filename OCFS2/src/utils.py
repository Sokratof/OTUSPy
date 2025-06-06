import subprocess
import pytest
import re
import time
from typing import List, Optional, Union


# Функция проверки выполнения команды
def check_command_output(
        command: Union[List[str], str],
        expect: Optional[Union[List[str], str]] = None,
        should_fail: bool = False,
        negative_check: bool = False
        ):
    """
    :param command: Список аргументов для выполнения команды или строка команды.
    :param expect: Ожидаемый текст (строка или список строк).
    :param should_fail: Если True, команда должна завершиться с ошибкой.
    :param negative_check: Если True, проверяется отсутствие ожидаемого текста.
    """
    # Объединяем список команд в строку, если команду передали как список
    if isinstance(command, list):
        command = ' '.join(command)

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Объединяем stderr с stdout
            text=True,
            shell=True,
        )
        output = result.stdout.strip()
        print(f"Command output:\n{output}")  # Логируем весь вывод

        # Проверка кода завершения
        if should_fail:
            if result.returncode == 0:
                pytest.fail(f"Выполнение'{command}' ожидалось с ошибкой")
        else:
            if result.returncode != 0:
                pytest.fail(f"Ошибка выполнения '{command}'")

        # Проверка ожидаемого текста
        if expect is not None:
            if isinstance(expect, str):
                if negative_check:
                    assert expect not in output, f"Ожидаемый результат не должен быть '{expect}'."
                else:
                    assert expect in output, f"Ожидаемый результат '{expect}' не найден в выводе."
            elif isinstance(expect, list):
                for expected_text in expect:
                    pattern = re.escape(expected_text)
                    if negative_check:
                        if re.search(pattern, output):
                            pytest.fail(f"Ожидаемый результат не должен быть '{expected_text}'.")
                    else:
                        if not re.search(pattern, output):
                            pytest.fail(f"Ожидаемый результат '{expected_text}' не найден в выводе.")
            else:
                raise ValueError("Параметр 'expect' должен быть строкой или массивом строк.")

    except Exception as e:
        pytest.fail(f"Произошла ошибка при выполнении команды: {e}")


# Variables
CONN = "qemu+tcp://sudcr1.ipa.rbt/system"


# Функция управления ВМ
def manage_vm(action: str, vm_name: str):
    valid_actions = [
        "start",
        "shutdown",
        "destroy",
        "suspend",
        "resume"
    ]

    if action not in valid_actions:
        print(f"Error: Not valid action '{action}'.")
        return

    cmd = [
        "virsh",
        "-c",
        CONN,
        action,
        vm_name
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"VM '{vm_name}' successfully {action}.")
    except subprocess.CalledProcessError as e:
        print(f"'{action}' failed for VM '{vm_name}'. Error: {e}")


# Функция проверки, что ОС ВМ загружена
def check_load_os(vm_name: str, timeout: int):
    start_time = time.time()
    while time.time() - start_time < timeout:
        result = subprocess.run(
        ["virsh", "-c", CONN,
        "qemu-agent-command", vm_name,
        '{"execute": "guest-ping"}'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
        )
        if result.returncode == 0 and '"return":{}' in result.stdout:
            print(f"OS VM {vm_name} successfully load")
            return True
        time.sleep(5)
    raise TimeoutError(f"OS VM {vm_name} not loaded")

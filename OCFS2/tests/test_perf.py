#!/usr/bin/env python3

import pexpect
import pytest
import re
from .conftest import results_df

# Конфигурация
DISKS = ["sdb", "sdc", "sdd", "sde", "sdf", "sdg", "sdh", "sdi"]
IP = "192.168.122.10"
USER = "u"
PASSWORD = "1"
TIMEOUT = 120
PROMPT = r'[\$#] '


@pytest.fixture(scope="module")
def ssh_session():
    """Фикстура для создания SSH-сессии."""
    session = pexpect.spawn(f"ssh {USER}@{IP}", timeout=TIMEOUT)
    try:
        index = session.expect(['password:', PROMPT])
        if index == 0:
            session.sendline(PASSWORD)
            session.expect(PROMPT)
        yield session
    finally:
        session.close()


# Извлекает скорость записи
def extract_speed(output):
    match = re.search(r"(\d+([.,]\d+)?)\s*MB/s", output)
    if match:
        return float(match.group(1).replace(",", "."))
    return None


# Извлекает время выполнения
def extract_time(output):
    match = re.search(r"скопирован,\s*(\d+[\.,]\d+)\s*s", output)
    if match:
        return float(match.group(1).replace(",", "."))
    return None


@pytest.mark.parametrize("disk", DISKS)
def test_disk_performance(ssh_session, disk):
    """Тест производительности для каждого диска."""
    global results_df

    try:
        # Проверяем доступность диска
        ssh_session.sendline(f"ls /dev/{disk}")
        ssh_session.expect(PROMPT)
        if f"/dev/{disk}" not in ssh_session.before.decode():
            pytest.skip(f"Диск {disk} не найден")

        # Запускаем тест
        test_cmd = f"sudo dd if=/dev/zero of=/dev/{disk} bs=1M count=512 oflag=direct status=progress && echo 'result: '$?"
        ssh_session.sendline(test_cmd)

        # Ожидаем запрос пароля или вывод
        index = ssh_session.expect(['password', 'bytes', pexpect.TIMEOUT], timeout=10)
        if index == 0:
            ssh_session.sendline(PASSWORD)
            ssh_session.expect('bytes')

        # Ждем завершения
        ssh_session.expect(PROMPT, timeout=TIMEOUT)
        output = ssh_session.before.decode()

        # Проверяем результат
        status = "success" if "result: 0" in output else "failed"
        speed = extract_speed(output)
        time_sec = extract_time(output)

        # Сохраняем данные
        results_df.loc[len(results_df)] = {
            "disk": disk,
            "speed_mb_s": speed,
            "time_sec": time_sec,
            "status": status
        }

        assert status == "success", f"Тест не завершился для диска {disk}"

    except pexpect.exceptions.EOF:
        pytest.fail(f"SSH сессия оборвалась при тестировании диска {disk}")
    except pexpect.exceptions.TIMEOUT:
        ssh_session.sendcontrol('c')
        pytest.fail(f"Таймаут при тестировании диска {disk}. Последний вывод: {ssh_session.before.decode()}")

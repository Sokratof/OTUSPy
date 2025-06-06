import os
import subprocess
import pytest
from src.utils import check_command_output


@pytest.fixture
def ocfs2_mountpoint():
    return "/vm"


# Проверка монтирования OCFS2
def test_ocfs2_mounted():
    command = "mount -t ocfs2"
    expect = "ocfs2"
    check_command_output(command, expect, should_fail=False)


# Проверка статуса кластера O2CB
def test_o2cb_status():
    command = "sudo o2cb cluster-status"
    expect = "Cluster 'ocfs2' is online"
    check_command_output(command, expect, should_fail=False)


# Проверка создания файла (Негативный тест)
def test_ocfs2_file_create_negative(ocfs2_mountpoint):
    test_file = f"{ocfs2_mountpoint}/testfile.bin"
    command = "touch " + test_file
    expect = "Отказано в доступе"
    check_command_output(command, expect, should_fail=True)


# Проверка создания файла (Позитивный тест)
def test_ocfs2_file_create_positive(ocfs2_mountpoint):
    test_file = f"{ocfs2_mountpoint}/testfile.bin"
    command = "echo 'test' | sudo tee " + test_file
    expect = "test"
    check_command_output(command, expect, should_fail=False)
    subprocess.run(f"sudo rm -f {test_file}", shell=True, check=True)
    assert not os.path.exists(test_file)


# Проверка создания файла большого размера
def test_large_file_write(ocfs2_mountpoint):
    large_file = f"{ocfs2_mountpoint}/testfile.bin"
    command = "sudo dd if=/dev/urandom of=" + large_file + " bs=1M count=1000"
    expect = "1,0 GB, 1000 MiB"
    check_command_output(command, expect, should_fail=False)
    subprocess.run(f"sudo rm -f {large_file}", shell=True, check=True)
    assert not os.path.exists(large_file)


# Проверка пропускной способности
def test_fio_throughput():
    command = "sudo fio --name=test --filename=/mnt/ocfs2/fio_test --rw=write --bs=128k --size=1G --runtime=10"
    expect = "Disk stats (read/write):"
    check_command_output(command, expect, should_fail=False)


# Проверка задержки доступа
def test_ioping_latency(ocfs2_mountpoint):
    command = "sudo ioping -c 10 " + ocfs2_mountpoint
    expect = "generated 10 requests"
    check_command_output(command, expect, should_fail=False)


# Проверка создания 1 000 файлов
def test_create_500_files(ocfs2_mountpoint):
    for i in range(500):
        subprocess.run(
            ["sudo", "touch", f"{ocfs2_mountpoint}/file_{i}.txt"],
            check=True
        )
    command = "ls -lahi " + ocfs2_mountpoint + " | grep 499.txt"
    expect = "file_499.txt"
    check_command_output(command, expect, should_fail=False)
    subprocess.run(f"sudo rm -f {ocfs2_mountpoint}/file_*", shell=True, check=True)

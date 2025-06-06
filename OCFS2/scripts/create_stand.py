#!/usr/bin/env python3

import subprocess
import os
import sys
from time import sleep
from src.utils import CONN
from src.utils import manage_vm
from src.utils import check_load_os


sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../')

manage_vm("start", "ocfs_vm")
check_load_os("ocfs_vm", 60)


# Функция по созданию дисков
def create_disk(disk_format: str, name: str) -> None:
    cmd = [
        "sudo", "qemu-img", "create",
        "-f", disk_format,
        f"/vm/{name}.{disk_format}", "5G"
    ]

    if disk_format == "qcow2":
        cmd.insert(5, "-o")
        cmd.insert(6, "extended_l2=on,cluster_size=128k")
    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.DEVNULL
        )
        print(f"Disk '{name}' successfully created.")
    except subprocess.CalledProcessError:
        print(f"Disk '{name}' successfully failed.")

# Параметры дисков (формат, имя)
disks = [
    ("qcow2", "qcow2_cash_none"),
    ("qcow2", "qcow2_cash_unsafe"),
    ("qcow2", "qcow2_cash_directsync"),
    ("qcow2", "qcow2_cash_writeback"),
    ("raw", "raw_cash_none"),
    ("raw", "raw_cash_unsafe"),
    ("raw", "raw_cash_directsync"),
    ("raw", "raw_cash_writeback")
        ]

for disk_format, name in disks:
    create_disk(disk_format=disk_format, name=name)


# Подключение диска к ВМ
def add_disk_with_param(name: str, disk_format: str, cache_mode: str, target_device: str):
    """Подключает диск к ВМ с указанными параметрами"""
    disk_path = f"/vm/{name}.{disk_format}"
    cmd = [
        "virsh", "-c", CONN,
        "attach-disk", "ocfs_vm",
        disk_path, target_device,
        "--cache", cache_mode,
        "--persistent",
        "--targetbus", "scsi"
    ]

    if disk_format == "qcow2":
        cmd.extend(["--subdriver", "qcow2"])

    try:
        subprocess.run(cmd, check=True)
        print(f"Диск '{disk_path}' (кэш: {cache_mode}) успешно подключен к ВМ как {target_device}")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка подключения диска '{disk_path}': {e.stderr if e.stderr else str(e)}")

# Параметры дисков (имя, формат, режим кэша, целевое устройство)
disks = [
    ("qcow2_cash_none", "qcow2", "none", "sdb"),
    ("qcow2_cash_unsafe", "qcow2", "unsafe", "sdc"),
    ("qcow2_cash_directsync", "qcow2", "directsync", "sdd"),
    ("qcow2_cash_writeback", "qcow2", "writeback", "sde"),
    ("raw_cash_none", "raw", "none", "sdf"),
    ("raw_cash_unsafe", "raw", "unsafe", "sdg"),
    ("raw_cash_directsync", "raw", "directsync", "sdh"),
    ("raw_cash_writeback", "raw", "writeback", "sdi")
]

# Подключаем диски
for name, disk_format, cache_mode, target_device in disks:
    add_disk_with_param(
        name=name,
        disk_format=disk_format,
        cache_mode=cache_mode,
        target_device=target_device
    )


manage_vm("shutdown", "ocfs_vm")
sleep(20)
manage_vm("start", "ocfs_vm")
check_load_os("ocfs_vm", 100)

import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime


# Функция для построения графиков
def plot_results(data):
    print("\nФункция plot_results вызвана.")  # Отладочный вывод
    if data.empty:
        print("Нет данных для построения графиков.")
        return

    # Преобразование столбцов в числовой формат
    data["speed_mb_s"] = pd.to_numeric(data["speed_mb_s"], errors="coerce")
    data["time_sec"] = pd.to_numeric(data["time_sec"], errors="coerce")

    # Настройка стиля Seaborn
    sns.set(style="darkgrid")

    # Создание фигуры с тремя подграфиками
    fig, axes = plt.subplots(3, 1, figsize=(10, 18))

    # График 1: Скорость записи (MB/s)
    sns.barplot(
        ax=axes[0],
        x="disk",
        y="speed_mb_s",
        data=data,
        palette="Blues_d"
    )
    axes[0].set_title("Скорость записи дисков (MB/s)")
    axes[0].set_ylabel("Скорость записи (MB/s)")

    # График 2: Время выполнения (секунды)
    sns.barplot(
        ax=axes[1],
        x="disk",
        y="time_sec",
        data=data,
        palette="Greens_d"
    )
    axes[1].set_title("Время выполнения операций (секунды)")
    axes[1].set_ylabel("Время выполнения (с)")

    # График 3: Статус (успешно/неуспешно)
    status_mapping = {"success": 1, "failed": 0}
    data["status_numeric"] = data["status"].map(status_mapping)

    sns.barplot(
        ax=axes[2],
        x="disk",
        y="status_numeric",
        data=data,
        palette="Reds_d"
    )
    axes[2].set_title("Статус операций")
    axes[2].set_ylabel("Статус (1 = success, 0 = failed)")
    axes[2].set_yticks([0, 1])  # Устанавливаем метки для оси Y

    # Настройка макета
    plt.tight_layout()

    # Сохранение графика в PDF
    home_dir = os.path.expanduser("~")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    pdf_filename = f"disk_performance_plots_{timestamp}.pdf"
    pdf_path = os.path.join(home_dir, pdf_filename)
    plt.savefig(pdf_path, format="pdf")
    print(f"График сохранён в файл: {pdf_path}")

    # Показать графики
    plt.show()
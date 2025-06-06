import os
import pandas as pd
import time
from OCFS2.src.graf import plot_results

# Глобальная переменная для хранения результатов
results_df = pd.DataFrame(columns=["disk", "speed_mb_s", "time_sec", "status"])


def pytest_sessionfinish(session, exitstatus):
    global results_df
    print("\npytest_sessionfinish вызван.")  # Отладочный вывод
    if not results_df.empty:
        home_dir = os.path.expanduser("~")
        output_file = os.path.join(home_dir, "disk_performance_results.csv")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        results_df.to_csv(output_file, index=False)
        print(f"\nРезультаты сохранены в: {output_file}")
        print("\nОжидание 3 секунд перед построением графиков.")
        time.sleep(3)
        plot_results(results_df)
    else:
        print("\nНет данных для сохранения.")

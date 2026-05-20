from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd


def save_csv_report(
    rows: list[dict[str, Any]],
    output_file: str,
) -> None:
    df = pd.DataFrame(rows)
    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print(f"CSV-отчёт сохранён: {output_file}")


def save_bot_distribution_chart(
    rows: list[dict[str, Any]],
    output_file: str,
) -> None:
    if not rows:
        print("Нет данных для построения диаграммы")
        return

    total = len(rows)
    bots_count = sum(1 for row in rows if row.get("is_detected_bot"))
    real_count = total - bots_count

    labels = ["Боты", "Реальные пользователи"]
    values = [bots_count, real_count]

    plt.figure(figsize=(7, 7))
    plt.pie(
        values,
        labels=labels,
        autopct="%1.1f%%",
        startangle=90,
    )
    plt.title("Доля подозрительных аккаунтов среди подписчиков")
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Диаграмма сохранена: {output_file}")


def print_summary(rows: list[dict[str, Any]]) -> None:
    total = len(rows)
    bots_count = sum(1 for row in rows if row.get("is_detected_bot"))
    real_count = total - bots_count

    if total == 0:
        print("Подписчики не найдены")
        return

    bot_percent = bots_count / total * 100

    avg_bot_score = average_score(
        [row for row in rows if row.get("is_detected_bot")]
    )

    avg_real_score = average_score(
        [row for row in rows if not row.get("is_detected_bot")]
    )

    print()
    print("Итоги анализа")
    print("-" * 40)
    print(f"Всего аккаунтов: {total}")
    print(f"Классифицированы как боты: {bots_count}")
    print(f"Классифицированы как реальные: {real_count}")
    print(f"Доля ботов: {bot_percent:.2f}%")
    print(f"Средний балл ботов: {avg_bot_score:.2f}")
    print(f"Средний балл реальных пользователей: {avg_real_score:.2f}")


def average_score(rows: list[dict[str, Any]]) -> float:
    if not rows:
        return 0.0

    return sum(int(row.get("score", 0)) for row in rows) / len(rows)

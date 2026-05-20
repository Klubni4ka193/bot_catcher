import argparse
import asyncio
from pathlib import Path
from typing import Any

import yaml

from collector import TelegramCollector
from features import extract_features
from report import (
    print_summary,
    save_bot_distribution_chart,
    save_csv_report,
)
from scoring import analyze_user


def load_config(path: str) -> dict[str, Any]:
    config_path = Path(path)

    if not config_path.exists():
        raise FileNotFoundError(f"Файл конфигурации не найден: {path}")

    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


async def run_analysis(channel: str, config_path: str) -> None:
    config = load_config(config_path)

    threshold = int(config["threshold"])
    weights = config["weights"]

    max_subscribers = int(config["limits"]["max_subscribers"])
    batch_size = int(config["limits"]["batch_size"])

    csv_file = config["output"]["csv_file"]
    chart_file = config["output"]["chart_file"]

    collector = TelegramCollector()

    try:
        print("Подключение к Telegram...")
        await collector.connect()

        print(f"Сбор подписчиков канала: {channel}")
        users = await collector.fetch_subscribers(
            channel_username=channel,
            limit=max_subscribers,
            batch_size=batch_size,
        )

        print(f"Получено аккаунтов: {len(users)}")

        analyzed_rows = []

        for user in users:
            user_features = extract_features(user)

            analyzed_user = analyze_user(
                user=user,
                features=user_features,
                weights=weights,
                threshold=threshold,
            )

            analyzed_rows.append(analyzed_user)

        save_csv_report(analyzed_rows, csv_file)
        save_bot_distribution_chart(analyzed_rows, chart_file)
        print_summary(analyzed_rows)

    finally:
        await collector.disconnect()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Анализ подписчиков Telegram-канала и обнаружение ботов"
    )

    parser.add_argument(
        "--channel",
        required=True,
        help="Username публичного Telegram-канала, например @channel_name",
    )

    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Путь до YAML-конфига",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    asyncio.run(
        run_analysis(
            channel=args.channel,
            config_path=args.config,
        )
    )

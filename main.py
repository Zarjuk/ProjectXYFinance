import asyncio
from modules.xyfinance import XYFinance
from modules.client import Client
from loguru import logger
from configs.config import CHAIN_ID_BY_NAME
import os


def configure_logging():
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    logger.add(os.path.join(log_dir, 'app.log'), format="{time} {level} {message}", level="DEBUG", rotation="1 MB")


async def main():
    configure_logging()

    valid_networks = list(CHAIN_ID_BY_NAME.keys())

    print("Доступные сети отправки:")
    for idx, network in enumerate(valid_networks, 1):
        print(f"{idx}. {network}")
    try:
        from_network_idx = int(input("Выберите номер сети-отправителя: ")) - 1
        if not 0 <= from_network_idx < len(valid_networks):
            logger.error("Ошибка: Некорректный выбор сети.")
            return
        from_network = valid_networks[from_network_idx]
    except ValueError:
        logger.error("Ошибка: Введите корректный номер сети.")
        return

    print("\nДоступные сети получения:")
    for idx, network in enumerate(valid_networks, 1):
        print(f"{idx}. {network}")
    try:
        to_network_idx = int(input("Выберите номер сети-получателя: ")) - 1
        if not 0 <= to_network_idx < len(valid_networks):
            logger.error("Ошибка: Некорректный выбор сети.")
            return
        to_network = valid_networks[to_network_idx]
        if from_network == to_network:
            logger.error("Сеть-отправитель и сеть-получатель не должны совпадать.")
            return
    except ValueError:
        logger.error("Ошибка: Введите корректный номер сети.")
        return

    private_key = input("Введите ваш приватный ключ: ").strip()
    if not private_key:
        logger.error("Ошибка: Приватный ключ не указан.")
        return

    try:
        amount = float(input("Введите количество нативного токена для перевода: ").strip())
        if amount <= 0:
            logger.error("Ошибка: Некорректное количество токенов для перевода.")
            return
    except ValueError:
        logger.error("Ошибка: Введите корректное число для количества токенов.")
        return

    try:
        client = Client(private_key=private_key, network_name=from_network)
        xy_finance = XYFinance(client=client)
    except Exception as e:
        logger.error(f"Ошибка при создании клиента: {e}")
        return

    try:
        await xy_finance.bridge(to_network=to_network, amount=amount)
    except Exception as e:
        logger.error(f"Ошибка при выполнении бриджа: {e}")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}")

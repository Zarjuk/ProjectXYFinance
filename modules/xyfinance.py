import asyncio
import json
from aiohttp import ClientSession, ClientConnectionError, ClientResponseError
from loguru import logger
from modules.client import Client
from configs.config import (
    CHAIN_ID_BY_NAME,
    XY_API_KEY,
    NATIVE_TOKEN_ADDRESS
)


class XYFinance:
    def __init__(self, client: Client):
        self.client = client
        self.api_url = 'https://aggregator-api.xy.finance/v1'

    async def get_quote(self, from_chain: int, to_chain: int, amount: int, from_address: str, to_address: str):
        params = {
            'fromChain': from_chain,
            'toChain': to_chain,
            'fromToken': NATIVE_TOKEN_ADDRESS,
            'toToken': NATIVE_TOKEN_ADDRESS,
            'fromAmount': str(amount),
            'slippage': '1',
            'fromAddress': from_address,
            'toAddress': to_address,
            'enableExpress': 'false',
        }
        headers = {}
        if XY_API_KEY:
            headers['Authorization'] = XY_API_KEY

        async with ClientSession() as session:
            try:
                async with session.get(f"{self.api_url}/quote", params=params, headers=headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    if data.get('status', {}).get('code') != 'SUCCESS':
                        raise Exception(data.get('status', {}).get('message', 'Неизвестная ошибка'))
                    return data.get('data')
            except Exception as e:
                logger.error(f"Ошибка при получении котировки: {e}")
                raise

    async def get_swap(self, quote_data: dict, sender_address: str, receiver_address: str):
        headers = {'Content-Type': 'application/json'}
        if XY_API_KEY:
            headers['Authorization'] = XY_API_KEY

        swap_request = quote_data
        swap_request['senderAddress'] = sender_address
        swap_request['receiverAddress'] = receiver_address
        swap_request['fromToken'] = NATIVE_TOKEN_ADDRESS
        swap_request['toToken'] = NATIVE_TOKEN_ADDRESS

        async with ClientSession() as session:
            try:
                async with session.post(f"{self.api_url}/swap", json=swap_request, headers=headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    if data.get('status', {}).get('code') != 'SUCCESS':
                        raise Exception(data.get('status', {}).get('message', 'Неизвестная ошибка'))
                    return data.get('data')
            except Exception as e:
                logger.error(f"Ошибка при получении данных для свапа: {e}")
                raise

    async def bridge(self, to_network: str, amount: float):
        from_chain_id = self.client.chain_id
        to_chain_id = CHAIN_ID_BY_NAME[to_network]
        amount_in_wei = int(amount * 10 ** 18)

        balance = await self.client.get_balance()
        if balance < amount_in_wei:
            logger.error("Недостаточно средств для выполнения бриджа.")
            return

        quote_data = await self.get_quote(
            from_chain=from_chain_id,
            to_chain=to_chain_id,
            amount=amount_in_wei,
            from_address=self.client.address,
            to_address=self.client.address
        )

        swap_data = await self.get_swap(
            quote_data=quote_data,
            sender_address=self.client.address,
            receiver_address=self.client.address
        )

        tx_data = swap_data.get('txData')
        if not tx_data:
            logger.error("Не удалось получить данные транзакции.")
            return

        nonce = await self.client.w3.eth.get_transaction_count(self.client.address)
        tx = {
            'from': self.client.address,
            'to': tx_data['to'],
            'value': int(tx_data['value']),
            'gas': int(tx_data['gasLimit']),
            'gasPrice': int(tx_data['gasPrice']),
            'nonce': nonce,
            'data': tx_data['data'],
            'chainId': from_chain_id,
        }

        tx_hash = await self.client.send_transaction(tx)

        logger.info("Ожидание подтверждения транзакции...")
        receipt = await self.client.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            logger.success(f"Бридж успешно выполнен! Транзакция: {tx_hash}")
        else:
            logger.error("Транзакция не выполнена.")

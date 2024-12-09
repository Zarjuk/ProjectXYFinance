import asyncio
from web3 import AsyncWeb3, AsyncHTTPProvider
from web3.exceptions import TransactionNotFound
from web3.middleware import geth_poa_middleware
from loguru import logger
from configs.config import RPC_URLS, CHAIN_ID_BY_NAME


class Client:
    def __init__(self, private_key: str, network_name: str, proxy: str = None):
        self.private_key = private_key
        self.chain_name = network_name.lower()
        if self.chain_name not in CHAIN_ID_BY_NAME:
            raise ValueError(f"Сеть '{network_name}' не поддерживается.")
        self.chain_id = CHAIN_ID_BY_NAME[self.chain_name]
        self.proxy = proxy
        self.w3 = self.get_web3_instance()
        self.address = self.w3.to_checksum_address(self.w3.eth.account.from_key(self.private_key).address)

    def get_web3_instance(self):
        rpc_url = RPC_URLS[self.chain_name]
        request_kwargs = {}
        if self.proxy:
            request_kwargs['proxies'] = {'http': f'http://{self.proxy}', 'https': f'https://{self.proxy}'}
        provider = AsyncHTTPProvider(rpc_url, request_kwargs=request_kwargs)
        w3 = AsyncWeb3(provider)
        if self.chain_name in ['bsc', 'polygon']:
            w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        return w3

    async def get_balance(self) -> int:
        return await self.w3.eth.get_balance(self.address)

    async def send_transaction(self, tx: dict) -> str:
        try:
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)
            tx_hash = await self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            logger.info(f"Транзакция отправлена. Хэш: {tx_hash.hex()}")
            return tx_hash.hex()
        except Exception as e:
            logger.error(f"Ошибка при отправке транзакции: {e}")
            raise

    async def wait_for_transaction_receipt(self, tx_hash: str, timeout: int = 120, poll_latency: int = 5):
        try:
            receipt = await self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout, poll_latency=poll_latency)
            return receipt
        except Exception as e:
            logger.error(f"Ошибка при ожидании подтверждения транзакции: {e}")
            raise

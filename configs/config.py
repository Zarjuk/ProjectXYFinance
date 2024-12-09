import os

RPC_URLS = {
    'ethereum': 'https://eth.llamarpc.com',
    'bsc': 'https://bsc-dataseed.binance.org/',
    'polygon': 'https://polygon.llamarpc.com',
}

CHAIN_ID_BY_NAME = {
    'ethereum': 1,
    'bsc': 56,
    'polygon': 137,
}

XY_FINANCE_CONTRACTS = {
    'ethereum': '0x6A6c963553E4F37e361AE7Dc8Aef0b7833CcE7fC',
    'bsc': '0x5d37ed3d5eAaa1Ceb38bDf9E6e6c6A140FAbd7Bd',
    'polygon': '0x30310e2e20B49D4D476cE3d9e13809fb47a2f446',
}

NATIVE_TOKEN_ADDRESS = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'

XY_API_KEY = None

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs', 'app.log')

import requests
import logging
from retrying import retry

# Set up logging to file and console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Endpoints for Aave on Arbitrum
BUY_API_URL = 'https://arbitrum-api.co/api/aave/lend'
SELL_API_URL = 'https://arbitrum-api.co/api/aave/borrow'
PRICE_API_URL = 'https://arbitrum-api.co/api/aave/market/data/'

# Your private key for authorization
PRIVATE_KEY = 'your_private_key_here'

# Configure trading parameters
AMOUNT_TO_LEND = 100  # Amount in WETH
TOKEN_TO_LEND = '0x1234567890abcdef1234567890abcdef12345678'  # Token contract address for lending
SLIPPAGE = 1  # Slippage tolerance (e.g., 1%)
AMOUNT_TO_BORROW = 1000  # Amount to borrow (e.g., USDC)

# Retry decorator to handle temporary issues with the API
@retry(stop_max_attempt_number=5, wait_fixed=2000)
def fetch_data_with_retry(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Will retry in case of status code 500 or connection error
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from {url}: {e}")
        raise

# Fetch real-time price of a token on Aave
def get_token_price(token_address):
    url = f'{PRICE_API_URL}{token_address}'
    try:
        price_data = fetch_data_with_retry(url)
        logger.info(f"Price data for token {token_address}: {price_data}")
        return price_data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching price for token {token_address}: {e}")
        return None

# Lend tokens on Aave via Arbitrum
def lend_tokens(amount, token_address, slippage):
    payload = {
        'private_key': PRIVATE_KEY,
        'token_in': token_address,
        'amount_in': amount,
        'slippage': slippage
    }
    try:
        response = requests.post(BUY_API_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        if data['status'] == 'success':
            logger.info(f"Successfully lent {amount} of token {token_address}. TXID: {data['txid']}")
        else:
            logger.error(f"Error lending tokens: {data['message']}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making lend request for {token_address}: {e}")

# Borrow tokens from Aave via Arbitrum
def borrow_tokens(amount, token_address, slippage):
    payload = {
        'private_key': PRIVATE_KEY,
        'token_out': token_address,
        'amount_out': amount,
        'slippage': slippage
    }
    try:
        response = requests.post(SELL_API_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        if data['status'] == 'success':
            logger.info(f"Successfully borrowed {amount} of token {token_address}. TXID: {data['txid']}")
        else:
            logger.error(f"Error borrowing tokens: {data['message']}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making borrow request for {token_address}: {e}")

# Trailing stop logic (protecting profits)
def trailing_stop(initial_price, current_price, threshold=0.02):
    """Trigger sell if the price falls by more than the threshold (e.g., 2%)"""
    if current_price <= initial_price * (1 - threshold):
        return True
    return False

# Main trading logic
def main():
    token_address = TOKEN_TO_LEND
    token_price_data = get_token_price(token_address)
    
    if token_price_data:
        initial_price = token_price_data.get('USD')
        logger.info(f"Initial price for token {token_address}: {initial_price}")
        
        # Add your conditions here for when to lend or borrow
        if token_price_data['USD'] < 0.01:  # Example condition to lend
            logger.info(f"Price is below threshold. Lending token {token_address}.")
            lend_tokens(AMOUNT_TO_LEND, token_address, SLIPPAGE)
        
        elif token_price_data['USD'] > 0.02:  # Example condition to borrow
            logger.info(f"Price is above threshold. Borrowing token {token_address}.")
            borrow_tokens(AMOUNT_TO_BORROW, token_address, SLIPPAGE)

        # Implement trailing stop if price moves in favorable direction
        if trailing_stop(initial_price, token_price_data['USD']):
            logger.info("Triggering trailing stop to protect profit.")
            borrow_tokens(AMOUNT_TO_BORROW, token_address, SLIPPAGE)
    else:
        logger.error("Failed to fetch token price.")

if __name__ == "__main__":
    main()


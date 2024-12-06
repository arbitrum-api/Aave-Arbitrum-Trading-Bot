

# Aave Arbitrum Trading Bot

This repository contains a Python-based trading bot that interacts with the Aave lending and borrowing platform on the **Arbitrum** network. The bot is designed to lend and borrow tokens based on dynamic price conditions, with a trailing stop mechanism to protect profits.

https://medium.com/@landonscott03/aave-api-for-arbitrum-borrow-lend-and-fetch-market-data-80e896b14ed3

## Features

- **Lend tokens** to Aave's lending pool via Arbitrum.
- **Borrow tokens** from Aave via Arbitrum.
- Fetch real-time token prices from Aave's market data.
- Implement **trailing stop** logic to protect profits when market prices move against your position.
- **Retry mechanism** to handle temporary API failures.

## Prerequisites

- Python 3.7 or later.
- `requests` and `retrying` libraries for making API requests and handling retries.

You can install the required dependencies using `pip`:

```bash
pip install requests retrying



# CoinGecko API proxy for Google Sheets:

Ways to use CoinGecko API in google sheets to get recent price data.

Currently just manual CLI (as POC), but the idea is to have an API proxy.

### Manual CLI usage:
- Copy your column of ticker symbols from sheets.
- Run (in activated venv): `python cli.py "<paste-here>"` (paste before closing the quote)
- Copy paste from terminal output back into sheets. 

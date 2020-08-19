# CoinGecko API proxy for Google Sheets:

Using CoinGecko API in Sheets to get price data by just using ImportXML e.g.
`=importxml("https://your-api-address/xml/price/btc","result")`

## API usage

### Local API via tunneling (e.g using [ngrok](https://ngrok.com/)):
#### Run the API locally:
<details><summary> With local python </summary>

1. Install in local virtual env after cloning: `make install`
2. Run local server: `make server`

</details>

<details><summary> Docker with local code </summary>

1. After cloning: `make docker-server`

</details>
    
    
<details><summary> Docker without cloning repo </summary>

1. `docker run -it --rm -p 9000:9000 artdgn/coingecko-sheets` (or `-p 1234:9000` to run on different port)

</details>

#### Set up tunnelling:    
For the API to be accessible from Sheets it needs to be publicly accessible 
(because google is making the requests not from your local machine).
One way to expose a locally running API (for development, or for **temporary** personal usage) 
is via [ngrok](https://ngrok.com/) tunelling (or any other similar alternative).
- After [setting up an ngrok account and local client](https://ngrok.com/download):
- Run `/path/to/ngrok http <port-number>` to run ngrok (e.g. `~/ngrok/ngrok http 9000` 
    if ngrok lives in `~/ngrok/` and you're using the default port of 9000. If you have the local 
    repo, you can also just `make ngrok` to run this command.
    
#### Usage in Sheets:
In Sheets, use ImportXML function to talk to the api: e.g. in a cell `=importxml("https://your-ngrok-temp-address.io/xml/price/btc","result")`.
 
For full documentation (live OpenAPI) go to `https://your-api-address/docs`.
E.g. for currencies other than USD add `?currency=aud` (e.g. for AUD).

## Simple manual CLI usage (not API)
<details><summary>Manual CLI usage instructions</summary>

- Copy your column of ticker symbols from sheets.
- Run:
    - Local python virtual environment: `python cli.py "<paste-here>"` (paste before closing the quote)
    - Docker: `docker run -it --rm artdgn/coingecko-sheets python cli.py "<paste-here>"` 
- Copy paste from terminal output back into sheets. 

</details>
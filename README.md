![CI](https://github.com/artdgn/coingecko-sheets/workflows/CI/badge.svg)

# CoinGecko API proxy for Google Sheets:
Using CoinGecko API in Sheets to get price data by just using ImportXML.

## Usage in Sheets:
In Sheets, use ImportXML function to talk to the api: e.g. in a cell:
> `=importxml("https://your-api-address/xml/price/btc","result")`.
 
![](https://artdgn.github.io/images/coingecko-sheets.gif)

For full documentation (live OpenAPI) go to `https://your-api-address/docs`.
E.g. for currencies other than USD add `?currency=aud`.

## Running the API
For the API to be accessible from Sheets it needs to be publicly accessible 
(because Google is making the requests not from your local machine).

### Host API on Heroku
> This option is easiest for actual usage (the free tier should be enough).

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/artdgn/coingecko-sheets)


### Run API locally and expose publicly via [ngrok](https://ngrok.com/):
> This option is best for development or temporary usage (free as well).

#### 1. Run the API locally:
<details><summary> Local python (instructions) </summary>

1. Install in local virtual env after cloning: `make install`
2. Run local server: `make server`

</details>

<details><summary> Docker with local code (instructions) </summary>

1. After cloning: `make docker-server`

</details>
    
    
<details><summary> Docker without cloning repo (instructions) </summary>

1. `docker run -it --rm -p 9000:9000 artdgn/coingecko-sheets` (or `-p 1234:9000` to run on different port)

</details>

#### 2. Set up tunnelling: 
- After [setting up an ngrok account and local client](https://ngrok.com/download):
- Run `/path/to/ngrok http <port-number>` to run ngrok (e.g. `~/ngrok/ngrok http 9000` 
    if ngrok lives in `~/ngrok/` and you're using the default port of 9000. If you have the local 
    repo, you can also just `make ngrok` to run this command.
    

## Simple manual CLI usage (not API)
<details><summary>Manual CLI usage instructions</summary>

- Copy your column of ticker symbols from sheets.
- Run:
    - Local python virtual environment: `python cli.py "<paste-here>"` (paste before closing the quote)
    - Docker: `docker run -it --rm artdgn/coingecko-sheets python cli.py "<paste-here>"` 
- Copy paste from terminal output back into sheets. 

</details>


## Alternative solutions
<details><summary>Some other options that didn't work for me</summary>

- [CRYPTOFINANCE](https://cryptofinance.ai) stopped working. In general trying any of the Google App Scripts solutions (like [IMPORTJSON](https://github.com/qeet/IMPORTJSONAPI) or like the updated CRYPTOFINANCE) didn't work for me because of the Auth issues (banged my head against it for a couple of hours and decided to just not use the Google Apps Scripts if making an external request from a script is such a herculian feat).
- Other Google Sheet add-ons like [Apipheny](https://apipheny.io/) were either paid or required API keys (so registration, or additional Yak-Shaving).
- In terms of actual cryptocurrency data APIs: CoinGecko is completely open, no need for API keys (for now?), so I went with it.
</details>

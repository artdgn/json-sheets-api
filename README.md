![CI](https://github.com/artdgn/coingecko-sheets/workflows/CI/badge.svg) ![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/artdgn/coingecko-sheets?label=dockerhub&logo=docker) ![GitHub deployments](https://img.shields.io/github/deployments/artdgn/coingecko-sheets/coingecko-sheets?label=heroku&logo=heroku)


# CoinGecko API proxy for Google Sheets  
Using CoinGecko API in Sheets to get cryptocurrency price data.

## Basic usage

Use [ImportXML](https://support.google.com/docs/answer/3093342?hl=en) to 
get basic price data:
> `=importxml("https://your-api-address/coingecko/xml/price/btc","result")`.
 
![](https://artdgn.github.io/images/coingecko-sheets.gif)

For full documentation of proxy endpoints (live OpenAPI) go to `https://your-api-address/docs`

## Live example API and Sheet:
- [Example API on Heroku](https://coingecko-sheets.herokuapp.com) free tier, use only as example, otherwise throttling and free tier limits will make it unusable.
- [Example Sheet](https://docs.google.com/spreadsheets/d/1cY8n9s1QnW7HQuMdJjihjpKlVSit2kRAT7oe7lFySLg/edit?usp=sharing) with the examples from this readme.

## Advanced usage (for other API routes or params)
Use `/xml/get` or `/datapoint/get` to import data from any other API URL that returns a JSON.

For any other data from CoinGecko API use [CoinGecko API live docs](https://www.coingecko.com/ja/api#explore-api) to create your target URL.

> Example: Use `coins/{id}/history` to get a particular date's price: `https://api.coingecko.com/api/v3/coins/bitcoin/history?date=17-12-2017`

<details><summary> Using JSONPath and ImportXML </summary>


> JSONPath should be preferred because not every valid JSON can be converted into XML (e.g. if some keys start with numbers).

1. Check the API's output JSON by going to the target URL in the browser.
2. Use [JSONPath syntax](https://restfulapi.net/json-jsonpath/) to create a JSONPath expression to get to your value. An example JSONPath expression to extract the historic price in USD would be `market_data.current_price.usd`.
3. In Sheets: pass the JSONPath expression as another parameter in the url for ImportXML function: 
`=importxml("https://your-api-address/xml/get?url=<your-target-url>&jsonpath=<your-jsonpath>","result")`.

Example
```
=importxml("https://your-api-address/xml/get?url=https://api.coingecko.com/api/v3/coins/bitcoin/history?date=17-12-2017&jsonpath=market_data.current_price.usd","result")
```

</details>

<details><summary> Using XPath and ImportXML </summary>

> Xpath expression can be used more easilty since the full XML is directly visible as output of the proxy API.

1. Check the proxy API's output XML by going to `https://your-api-address/xml/get?url=<target-url>` in the browser.
2. Use [XPath syntax](https://www.w3schools.com/xml/xpath_syntax.asp) to create an XPath expression to extract your data. An example XPath expression to extract the historic price in USD would be `result/market_data/current_price/usd`.
3. In Sheets: pass the XPath as second argument for ImportXML function: `=importxml("https://your-api-address/xml/get?url=<your-target-url>","<your-xpath>")`

Example: 
```
=importxml("https://your-api-address/xml/get?url=https://api.coingecko.com/api/v3/coins/bitcoin/history?date=17-12-2017","result/market_data/current_price/usd")
```

</details>

<details><summary> Using JSONPath and ImportDATA </summary>

> ImportDATA is limited to 50 calls per sheet, so should be used in small sheets only.

The `/datapoint/get` endpoint can be used to return just the value as plain text which allows using ImportDATA
Sheets function instead of ImportXML.

Follow the same steps as for JSONPath with ImportXML above, but use a `/datapoint/get` proxy route and ImportDATA instead of ImportXML

Example
```
=importdata("https://your-api-address/xml/get?url=https://api.coingecko.com/api/v3/coins/bitcoin/history?date=17-12-2017&jsonpath=market_data.current_price.usd")
```

</details>

## Running the API
For the API to be accessible from Sheets it needs to be publicly accessible 
(because Google is making the requests not from your local machine).

### Host API on Heroku
> This option is best for actual usage (the free tier should be enough). Also best in terms of privacy

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
<details><summary> Tunnelling with ngrok </summary>

- After [setting up an ngrok account and local client](https://ngrok.com/download):
- Run `/path/to/ngrok http <port-number>` to run ngrok (e.g. `~/ngrok/ngrok http 9000` 
    if ngrok lives in `~/ngrok/` and you're using the default port of 9000. If you have the local 
    repo, you can also just `make ngrok` to run this command.
    
</details>

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

## Privacy thoughts
<details><summary>Privacy related thoughts</summary>

TL;DR: probably best to host your own.

1. I don't think there's a way to know which accounts are making any of the requests.
2. Hosting your own proxy API (e.g. on Heroku) is probably the best option since your requests will be visible to your proxy (and Heroku).
3. Hosting a local proxy API via tunnelling (the "ngrok" option) will mean that requests to CoinGecko (or any other API you're using through this) will come from your machine.
4. Using my example deployment means that I can see the request parameters in the logs (but with no idea about the google accounts).

</details>

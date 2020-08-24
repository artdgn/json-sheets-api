![CI](https://github.com/artdgn/json-sheets-api/workflows/CI/badge.svg) ![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/artdgn/json-sheets-api?label=dockerhub&logo=docker) ![GitHub deployments](https://img.shields.io/github/deployments/artdgn/json-sheets-api/json-sheets-api?label=heroku&logo=heroku)

# ImportJSON API for Google Sheets
Use any JSON API in Google Sheets by using ImportXML / ImportDATA and a proxy API.

![](https://artdgn.github.io/images/sheets-import-json-api.gif)

## Live example API and Sheet:
- [Example API on Heroku](https://json-sheets-api.herokuapp.com) free tier, welcome to use as example.
- [Example Sheet](https://docs.google.com/spreadsheets/d/1RRnpLPIVuN5KoPVxIYraOcUHicL69hZPaTf7HpM9NU4/edit?usp=sharing) with the examples from this readme.

## What can this be useful for?
Use [this great list of public APIs](https://github.com/public-apis/public-apis) to find anything that might be useful to you. Books? Health? Jobs? Scraping & open data? Business? Ctyptocurrency? Stocks? Events? News? Shopping? Movies / TV?

## Usage
Use `/xml/get` or `/datapoint/get` to import data from any API URL GET endpoint that returns a JSON. 
Use `/xml/post` or `/datapoint/post` for POST target endpoints.

Example: We'll use [Chuck Norris API](https://api.chucknorris.io/) to extract "sheet" related jokes. The target URL for that will be `https://api.chucknorris.io/jokes/search?query=sheets`.

<details><summary> Using JSONPath and ImportXML </summary>

> JSONPath should be preferred because not every valid JSON can be converted into XML (e.g. if some keys start with numbers).

1. Check the target API's output JSON by going to the target URL in the browser.
2. Use [JSONPath syntax](https://restfulapi.net/json-jsonpath/) to create a JSONPath expression to get to your value. An example JSONPath expression to extract the first joke will be `result[0].value`.
3. In Sheets: pass the JSONPath expression as another parameter in the url for ImportXML function: 
`=importxml("https://your-api-address/xml/get?url=<your-target-url>&jsonpath=<your-jsonpath>","result")`.

Example
```
=importxml("https://your-api-address/xml/get?
    url=https://api.chucknorris.io/jokes/search?query=sheets&
    jsonpath=result[0].value","result")
```

</details>

<details><summary> Using XPath and ImportXML </summary>

> Xpath expression can be used more easilty since the full XML is directly visible as output of the proxy API.

1. Check the proxy API's output XML by going to `https://your-api-address/xml/get?url=<target-url>` in the browser.
2. Use [XPath syntax](https://www.w3schools.com/xml/xpath_syntax.asp) to create an XPath expression to extract your data. An example XPath expression to extract the first joke will be `result/result[1].value`.
3. In Sheets: pass the XPath as second argument for ImportXML function: `=importxml("https://your-api-address/xml/get?url=<your-target-url>","<your-xpath>")`

Example: 
```
=importxml("https://your-api-address/xml/get?
    url=https://api.chucknorris.io/jokes/search?query=sheets"
    ,"result/result[1].value")
```

</details>

<details><summary> Using JSONPath and ImportDATA </summary>

> ImportDATA is limited to 50 calls per sheet, so should be used in small sheets only. Also, if your value contains commas, the value will be interpreted as a table and broken into multiple cells.

The `/datapoint/get` endpoint can be used to return just the value as plain text which allows using ImportDATA
Sheets function instead of ImportXML.

Follow the same steps as for JSONPath with ImportXML above, but use a `/datapoint/get` proxy route and ImportDATA instead of ImportXML

Example
```
=importdata("https://your-api-address/datapoint/get?
    url=https://api.chucknorris.io/jokes/search?query=sheets&
    jsonpath=result[0].value")
```
</details>

<details><summary> Using POST target endpoints </summary>

POST endpoints usage (`/xml/post` or `/datapoint/post`) is exactly as their GET counterparts, except a required `body_json` URL paramater is expected to contain the JSON to be sent to the target API. Note that in Sheets quotes in that JSON need to be doubled to be escaped. 

Example:
```
=importxml("https://your-api-address/xml/post?
        url=https://jsonplaceholder.typicode.com/posts&
        body_json={""title"":""bla""}",
        "result/id")
```
</details>

## Running the API
For the API to be accessible from Sheets it needs to be publicly accessible 
(because Google is making the requests not from your local machine).

### Host API on Heroku
> This option is best for actual usage (the free tier should be enough). Also best in terms of privacy

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/artdgn/json-sheets-api)


### Run API locally and expose publicly via [ngrok](https://ngrok.com/):
> This option is best for development or temporary usage (free as well).

#### 1. Run the API locally:
<details><summary> Local python option </summary>

1. Install in local virtual env after cloning: `make install`
2. Run local server: `make server`

</details>

<details><summary> Docker with local code option </summary>

1. After cloning: `make docker-server`

</details>
    
    
<details><summary> Docker without cloning repo option </summary>

1. `docker run -it --rm -p 9000:9000 artdgn/json-sheets-api` (or `-p 1234:9000` to run on different port)

</details>

#### 2. Set up tunnelling: 
<details><summary> Tunnelling with ngrok </summary>

- After [setting up an ngrok account and local client](https://ngrok.com/download):
- Run `/path/to/ngrok http <port-number>` to run ngrok (e.g. `~/ngrok/ngrok http 9000` 
    if ngrok lives in `~/ngrok/` and you're using the default port of 9000. If you have the local 
    repo, you can also just `make ngrok` to run this command.
    
</details>


## Alternative solutions
<details><summary>Some other options that didn't work for me</summary>

- Trying any of the Google App Scripts solutions (like [IMPORTJSON](https://github.com/qeet/IMPORTJSONAPI) didn't work for me because of the Auth issues (banged my head against it for a couple of hours and decided to just not use the Google Apps Scripts if making an external request from a script is such a herculian feat).
- Other Google Sheet add-ons like [Apipheny](https://apipheny.io/) were either paid or required API keys (so registration, or additional Yak-Shaving).
</details>

## Privacy thoughts
<details><summary>Privacy related thoughts</summary>

TL;DR: probably best to host your own.

1. I don't think there's a way to know which accounts are making any of the requests.
2. Hosting your own proxy API (e.g. on Heroku) is probably the best option since your requests will be visible only to your proxy (and Heroku).
3. Hosting a local proxy API via tunnelling (the "ngrok" option) will mean that external requests will come from your machine.
4. Using my example deployment means that I can see the request parameters in the logs (but with no idea about the google accounts).

</details>

### Related resources
- This is actually a more generalised version of [crypto-sheets-api](https://github.com/artdgn/crypto-sheets-api/) that supports POST requests, and doesn't have crypto-currency related endpoints, or examples. This is because this one aims to be useful for any target API.
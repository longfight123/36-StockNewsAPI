"""

This script uses a news API and a stock price API
to search for big changes in stocks the user is tracking
and obtains the news on that company. The app sends a SMS
notification to the user.

This script requires that 'requests', 'twilio', 'python_dotenv'
be installed within the Python
environment you are running this script in.

"""

import requests
from twilio.rest import Client
import datetime as dt
from dotenv import load_dotenv
import os

load_dotenv(".env")
STOCK = "MSFT"
COMPANY_NAME = "Microsoft"
STOCK_API_KEY = os.getenv("STOCK_API_KEY")
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_APIKEY = os.getenv("NEWS_APIKEY")
STOCK_PARAMETERS = {
    'function': 'TIME_SERIES_DAILY_ADJUSTED',
    'symbol': STOCK,
    'apikey': STOCK_API_KEY
}
NEWS_PARAMETERS = {
    'qInTitle': COMPANY_NAME,
    'apiKey': NEWS_APIKEY,
    'sortby': 'popularity'
}
account_sid = os.getenv("account_sid")
auth_token = os.getenv("auth_token")
arrow_symbol = None

## STEP 1: Use https://newsapi.org/docs/endpoints/everything
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
#HINT 1: Get the closing price for yesterday and the day before yesterday. Find the positive difference between the two prices. e.g. 40 - 20 = -20, but the positive difference is 20.
#HINT 2: Work out the value of 5% of yerstday's closing stock price.

response = requests.get(url=STOCK_ENDPOINT, params=STOCK_PARAMETERS)
response.raise_for_status()
raw_stock_data = response.json()
yesterday = dt.datetime.today() - dt.timedelta(days=1)
two_days_ago = yesterday - dt.timedelta(days=1)
while yesterday.weekday() in [6, 5]:
    yesterday = yesterday - dt.timedelta(days=1)
    two_days_ago = yesterday - dt.timedelta(days=1)
yesterday = yesterday.strftime('%Y-%m-%d')
two_days_ago = two_days_ago.strftime('%Y-%m-%d')
yesterday_close_price = float(raw_stock_data['Time Series (Daily)'][yesterday]['4. close'])
two_days_ago_close_price = float(raw_stock_data['Time Series (Daily)'][two_days_ago]['4. close'])

percentage_increase = abs((yesterday_close_price-two_days_ago_close_price)/two_days_ago_close_price*100)
if percentage_increase > 5:
    get_news = True
else:
    get_news = False

if yesterday_close_price > two_days_ago_close_price:
    arrow_symbol = '⬆'
else:
    arrow_symbol = '⬇'

## STEP 2: Use https://newsapi.org/docs/endpoints/everything
# Instead of printing ("Get News"), actually fetch the first 3 articles for the COMPANY_NAME. 
#HINT 1: Think about using the Python Slice Operator

# get_news = True for testing purposes

if get_news:
    response = requests.get(url=NEWS_ENDPOINT, params=NEWS_PARAMETERS)
    response.raise_for_status()
    articles = response.json()['articles'][0:3]

## STEP 3: Use twilio.com/docs/sms/quickstart/python
# Send a separate message with each article's title and description to your phone number. 
#HINT 1: Consider using a List Comprehension.

    client = Client(account_sid, auth_token)
    for article in articles:
        message = client.messages \
                        .create(
                             body=f"\n\n{STOCK} {arrow_symbol} {percentage_increase}%\n\nHeadline: {article['title']}\n\nBrief: {article['description']}",
                             from_='+12158678688',
                             to='+14036693979'
                         )

        print(message.status)


#Optional: Format the SMS message like this: 
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""


import os
import requests
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from a .env file

STOCK_NAME = "SPY"
COMPANY_NAME = "S&P 500"
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

Stock_API = os.getenv("Stock_API")
News_API = os.getenv("News_API")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")


def fetch_stock_data(stock_name):
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": stock_name,
        "apikey": Stock_API,
    }
    try:
        response = requests.get(STOCK_ENDPOINT, params=params)
        response.raise_for_status()
        data = response.json()["Time Series (Daily)"]
        return list(data.values())
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return None


def calculate_percentage_difference(data):
    if not data or len(data) < 2:
        return 0
    yesterday_close = float(data[0]["4. close"])
    day_before_close = float(data[1]["4. close"])
    diff = abs(yesterday_close - day_before_close)
    return (diff / yesterday_close) * 100


def fetch_news(company_name):
    params = {
        "apikey": News_API,
        "qInTitle": company_name,
    }
    try:
        response = requests.get(NEWS_ENDPOINT, params=params)
        response.raise_for_status()
        return response.json().get("articles", [])[:3]
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []


def send_sms(messages):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    for message in messages:
        try:
            client.messages.create(
                body=message,
                from_="+18886195395",
                to="+14324440705"
            )
        except Exception as e:
            print(f"Error sending SMS: {e}")


def main():
    stock_data = fetch_stock_data(STOCK_NAME)
    percentage_diff = calculate_percentage_difference(stock_data)

    if percentage_diff > 5:
        news_articles = fetch_news(COMPANY_NAME)
        formatted_articles = [
            f"{STOCK_NAME}: 🔺{percentage_diff:.2f}%\nHeadline: {article['title']}\nBrief: {article['description']}"
            for article in news_articles
        ]
        send_sms(formatted_articles)


if __name__ == "__main__":
    main()


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
    print(f"[INFO] Fetching stock data for {stock_name}...")
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": stock_name,
        "apikey": Stock_API,
    }
    try:
        response = requests.get(STOCK_ENDPOINT, params=params)
        response.raise_for_status()
        data = response.json().get("Time Series (Daily)", {})
        if not data:
            raise ValueError("Missing 'Time Series (Daily)' in API response.")
        print("[INFO] Stock data fetched successfully.")
        return list(data.values())
    except Exception as e:
        print(f"[ERROR] Error fetching stock data: {e}")
        return None

def calculate_percentage_difference(data):
    print("[INFO] Calculating percentage difference...")
    if not data or len(data) < 2:
        print("[WARNING] Not enough data to calculate percentage difference.")
        return 0
    yesterday_close = float(data[0]["4. close"])
    day_before_close = float(data[1]["4. close"])
    diff = abs(yesterday_close - day_before_close)
    percentage_diff = (diff / yesterday_close) * 100
    print(f"[INFO] Percentage difference calculated: {percentage_diff:.2f}%")
    return percentage_diff

def fetch_news(company_name):
    print(f"[INFO] Fetching news for {company_name}...")
    params = {
        "apikey": News_API,
        "qInTitle": company_name,
    }
    try:
        response = requests.get(NEWS_ENDPOINT, params=params)
        response.raise_for_status()
        articles = response.json().get("articles", [])[:3]
        print("[INFO] News fetched successfully.")
        return articles
    except Exception as e:
        print(f"[ERROR] Error fetching news: {e}")
        return []

def send_sms(messages):
    print("[INFO] Sending SMS notifications...")
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    for message in messages:
        try:
            client.messages.create(
                body=message,
                from_="+18886195395",
                to="+14324440705"
            )
            print(f"[INFO] Message sent: {message[:30]}...")  # Log first 30 chars
        except Exception as e:
            print(f"[ERROR] Error sending SMS: {e}")

def main():
    print("[INFO] Starting stock and news notification process...")
    stock_data = fetch_stock_data(STOCK_NAME)
    if not stock_data:
        print("[ERROR] Stock data could not be fetched. Exiting...")
        return

    percentage_diff = calculate_percentage_difference(stock_data)
    if percentage_diff > 5:
        print(f"[INFO] Significant stock change detected ({percentage_diff:.2f}%). Fetching news...")
        news_articles = fetch_news(COMPANY_NAME)
        if news_articles:
            formatted_articles = [
                f"{STOCK_NAME}: 🔺{percentage_diff:.2f}%\nHeadline: {article['title']}\nBrief: {article['description']}"
                for article in news_articles
            ]
            send_sms(formatted_articles)
        else:
            print("[WARNING] No news articles found to send.")
    else:
        print("[INFO] No significant stock change detected. No news fetched.")

    print("[INFO] Process completed.")

if __name__ == "__main__":
    main()


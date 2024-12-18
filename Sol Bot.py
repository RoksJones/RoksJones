import requests
from bs4 import BeautifulSoup
import json
import time


def fetch_gmgn_trending():
    url = "https://gmgn.com/trending-tokens"  # Replace with GMGN's actual URL for trending tokens
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    trending_tokens = []
    # Adjust the following selectors based on the actual structure of GMGN
    for token_row in soup.select("div.token-row"):
        token_name = token_row.select_one("span.token-name").text.strip()
        volume = token_row.select_one("span.token-volume").text.strip()
        liquidity = token_row.select_one("span.token-liquidity").text.strip()
        age = token_row.select_one("span.token-age").text.strip()
        holders = token_row.select_one("span.token-holders").text.strip()
        ca = token_row.select_one("span.token-ca").text.strip()

        trending_tokens.append({
            "name": token_name,
            "volume": float(volume.replace(",", "")),
            "liquidity": float(liquidity.replace(",", "")),
            "age": int(age.replace(" hours", "")),
            "holders": int(holders.replace(",", "")),
            "ca": ca
        })

    return trending_tokens


def fetch_dexscreener_trending():
    url = "https://www.dexscreener.com/api/trending"  # Replace with Dexscreener's actual API or URL
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()  # Assuming API returns JSON
    trending_tokens = []

    for token in data.get("tokens", []):
        trending_tokens.append({
            "name": token["name"],
            "volume": token["volume"],
            "liquidity": token.get("liquidity"),
            "age": token.get("age"),
            "holders": token.get("holders"),
            "ca": token.get("ca")
        })

    return trending_tokens


def filter_tokens(tokens):
    filtered_tokens = [
        token["ca"] for token in tokens
        if token["liquidity"] < 100000 and
           token["volume"] < 250000 and
           token["age"] >= 24 and
           token["holders"] <= 300
    ]
    return filtered_tokens


def fetch_rugcheck_report(ca):
    url = f"https://rugcheck.example.com/api/check?ca={ca}"  # Replace with the actual Rugcheck API endpoint
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    report = response.json()  # Assuming the API returns JSON

    return report


def check_rug_safety(filtered_tokens):
    safe_tokens = []

    for ca in filtered_tokens:
        try:
            print(f"Checking Rugcheck report for CA: {ca}")
            report = fetch_rugcheck_report(ca)

            # Assuming the report contains a "minimum_score" field
            if report.get("minimum_score", "") in ["Good", "Excellent"]:
                safe_tokens.append({"ca": ca, "report": report})
        except Exception as e:
            print(f"Error fetching Rugcheck report for CA {ca}: {e}")

    return safe_tokens


def fetch_tweetscout_data(ca):
    url = f"https://tweetscout.example.com/api/check?ca={ca}"  # Replace with the actual Tweetscout API endpoint
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()  # Assuming the API returns JSON

    return {
        "engagement_score": data.get("engagement_score"),
        "top_influencers": data.get("top_influencers", [])[:20]  # Top 20 influencers
    }


def send_to_telegram_bot(ca):
    bot_token = "your_telegram_bot_token"  # Replace with your Telegram bot token
    chat_id = "your_chat_id"  # Replace with your Telegram chat ID
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    message = f"Token CA: {ca} passed all criteria."

    payload = {"chat_id": chat_id, "text": message}

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"Successfully sent CA {ca} to Telegram bot.")
    except Exception as e:
        print(f"Error sending CA {ca} to Telegram bot: {e}")


def main():
    try:
        print("Fetching GMGN trending tokens...")
        gmgn_tokens = fetch_gmgn_trending()
        filtered_gmgn = filter_tokens(gmgn_tokens)
        print("Filtered GMGN Tokens:", json.dumps(filtered_gmgn, indent=4))

        print("Checking Rugcheck reports for GMGN tokens...")
        safe_gmgn_tokens = check_rug_safety(filtered_gmgn)
        print("Safe GMGN Tokens:", json.dumps(safe_gmgn_tokens, indent=4))

        for token in safe_gmgn_tokens:
            print(f"Fetching Tweetscout data for CA: {token['ca']}")
            tweetscout_data = fetch_tweetscout_data(token['ca'])
            print(f"Tweetscout Data for {token['ca']}:", json.dumps(tweetscout_data, indent=4))
            send_to_telegram_bot(token['ca'])
    except Exception as e:
        print(f"Error processing GMGN tokens: {e}")

    try:
        print("Fetching Dexscreener trending tokens...")
        dexscreener_tokens = fetch_dexscreener_trending()
        filtered_dexscreener = filter_tokens(dexscreener_tokens)
        print("Filtered Dexscreener Tokens:", json.dumps(filtered_dexscreener, indent=4))

        print("Checking Rugcheck reports for Dexscreener tokens...")
        safe_dexscreener_tokens = check_rug_safety(filtered_dexscreener)
        print("Safe Dexscreener Tokens:", json.dumps(safe_dexscreener_tokens, indent=4))

        for token in safe_dexscreener_tokens:
            print(f"Fetching Tweetscout data for CA: {token['ca']}")
            tweetscout_data = fetch_tweetscout_data(token['ca'])
            print(f"Tweetscout Data for {token['ca']}:", json.dumps(tweetscout_data, indent=4))
            send_to_telegram_bot(token['ca'])
    except Exception as e:
        print(f"Error processing Dexscreener tokens: {e}")


if __name__ == "__main__":
    main()

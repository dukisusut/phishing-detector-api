import requests

API_URL = "http://127.0.0.1:8000/predict-url"

test_urls = [
    # ===== LEGIT =====
    "https://google.com",
    "https://facebook.com",
    "https://paypal.com",
    "https://github.com",

    # ===== PHISHING =====
    "http://paypal-login-secure.com",
    "http://secure-bank-login.xyz",
    "http://verify-account-update.com",

    # ===== EDGE CASE =====
    "http://192.168.1.1/login",
    "http://google.com.fake-site.xyz",
    "http://paypal.com.secure-login.xyz",
    "http://login-facebook.com",
]


def test_url(url):
    try:
        res = requests.post(API_URL, json={"url": url})
        data = res.json()

        print("=" * 60)
        print(f"URL: {url}")
        print(f"→ phishing: {data.get('is_phishing')}")
        print(f"→ confidence: {data.get('confidence')}")
        print(f"→ source: {data.get('source')}")
        print(f"→ reason: {data.get('reason')}")

    except Exception as e:
        print(f"❌ Error with {url}: {e}")


if __name__ == "__main__":
    for url in test_urls:
        test_url(url)

import requests

OPENPHISH_URL = "https://openphish.com/feed.txt"

OUTPUT_FILE = "data/blacklist.txt"


def update_blacklist():

    print("Downloading phishing feed...")

    response = requests.get(OPENPHISH_URL)

    urls = response.text.splitlines()

    with open(OUTPUT_FILE, "w") as f:

        for url in urls:
            f.write(url.strip() + "\n")

    print(f"Saved {len(urls)} phishing URLs")


if __name__ == "__main__":

    update_blacklist()

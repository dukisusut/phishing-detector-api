import pandas as pd
import random

df = pd.read_csv("data/tranco.csv", header=None)
df.columns = ["rank", "domain"]

# ===== CONFIG =====

paths = [
    "/",
    "/search?q=iphone",
    "/login",
    "/product/123",
    "/category/item",
    "/user/profile?id=123",
    "/cart",
    "/checkout",
    "/news/latest",
    "/blog/post"
]

subdomains = ["www", "m", "app", "shop", "news"]

# ===== GENERATOR =====

def add_subdomain(domain):
    if random.random() < 0.4:
        sub = random.choice(subdomains)
        return f"{sub}.{domain}"
    return domain


def add_path():
    return random.choice(paths)


def generate_legit_url(domain):
    # thêm subdomain
    domain = add_subdomain(domain)

    # random https/http
    scheme = "https" if random.random() < 0.8 else "http"

    # thêm path
    path = add_path()

    return f"{scheme}://{domain}{path}"


# ===== APPLY =====

df = df.head(10000)

df["url"] = df["domain"].apply(generate_legit_url)

df = df[["url"]]
df["label"] = 0

df.to_csv("data/legit.csv", index=False)

print("Done legit dataset (REALISTIC VERSION)")

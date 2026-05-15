import pandas as pd

# ===== LOAD DATA =====
df = pd.read_csv("data/online-valid.csv")

# chỉ lấy cột url
df = df[["url"]]

# ===== CLEAN DATA =====

# drop null
df = df.dropna()

# chỉ giữ url hợp lệ
df = df[df["url"].str.startswith(("http://", "https://"), na=False)]

# normalize lowercase
df["url"] = df["url"].str.lower()

# remove duplicate
df = df.drop_duplicates()

# ===== LIMIT SIZE (có thể chỉnh) =====
df = df.head(60000)

# ===== ADD HARD PHISH (BONUS) =====

hard_phish = [
    "http://paypal-login-secure.com",
    "http://facebook.verify-account.xyz",
    "http://apple-id-confirm.top/login",
    "http://bank-secure-update.tk",
    "http://secure-google-login.com",
    "http://amazon-account-verify.net",
    "http://microsoft-security-check.xyz/login",
    "http://instagram-login-help.top",
    "http://netflix-billing-update.tk",
    "http://shopee-login-secure.xyz"
]

df_extra = pd.DataFrame({
    "url": hard_phish
})

# merge vào dataset
df = pd.concat([df, df_extra], ignore_index=True)

# ===== FINAL CLEAN (sau khi merge) =====
df = df.drop_duplicates()

# ===== LABEL =====
df["label"] = 1

# ===== SAVE =====
df.to_csv("data/phish.csv", index=False)

# ===== LOG =====
print("Done phishing dataset (CLEAN + HARD CASES)")
print("Total samples:", len(df))

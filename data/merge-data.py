import pandas as pd

phish = pd.read_csv("data/phish.csv")
legit = pd.read_csv("data/legit.csv")

# ghép lại
df = pd.concat([phish, legit])

# shuffle
df = df.sample(frac=1).reset_index(drop=True)

# clean
df = df.dropna()
df = df.drop_duplicates()

df.to_csv("data/url_dataset.csv", index=False)

print("Final dataset ready!")

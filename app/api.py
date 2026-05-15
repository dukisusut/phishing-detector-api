import json
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import urlparse

from app.predictor import Predictor
from training.feature import extract_features
from app.rules import check_rules

app = FastAPI()

# =========================================================
# Cau hinh CORS de extension/browser co the goi API
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# File luu cache va reputation
# =========================================================

CACHE_FILE = "data/cache.json"

REPUTATION_FILE = "data/domain_reputation.json"

# =========================================================
# Tao thu muc data neu chua ton tai
# =========================================================

os.makedirs("data", exist_ok=True)

# =========================================================
# Load cache tu file
# =========================================================

if os.path.exists(CACHE_FILE):

    with open(CACHE_FILE, "r") as f:

        CACHE = json.load(f)

else:

    CACHE = {}

# =========================================================
# Load domain reputation tu file
# =========================================================

if os.path.exists(REPUTATION_FILE):

    with open(REPUTATION_FILE, "r") as f:

        DOMAIN_REPUTATION = json.load(f)

else:

    DOMAIN_REPUTATION = {}

# =========================================================
# Thong ke he thong
# =========================================================

STATS = {
    "total_scans": 0,
    "phishing_detected": 0,
    "safe_urls": 0,
    "cache_hits": 0,
    "domain_blocks": 0
}

# =========================================================
# Load model ML
# =========================================================

predictor = Predictor(
    "model/url_model.pkl",
    threshold=0.55
)

# =========================================================
# Ham save cache va reputation ra file
# =========================================================

def save_data():

    with open(CACHE_FILE, "w") as f:

        json.dump(CACHE, f, indent=4)

    with open(REPUTATION_FILE, "w") as f:

        json.dump(DOMAIN_REPUTATION, f, indent=4)

# =========================================================
# API health check
# =========================================================

@app.get("/")
def health():

    return {
        "status": "ok"
    }

# =========================================================
# API predict bang raw features
# Dung de test model
# =========================================================

@app.post("/predict")
def predict(data: dict):

    try:

        features = data.get("features")

        if not features:

            raise HTTPException(
                status_code=400,
                detail="Missing features"
            )

        return predictor.predict(features)

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

# =========================================================
# API detect phishing bang URL
# =========================================================

@app.post("/predict-url")
def predict_url(data: dict):

    try:

        # =================================================
        # Kiem tra input URL
        # =================================================

        url = data.get("url")

        if not url:

            raise HTTPException(
                status_code=400,
                detail="Missing URL"
            )

        # =================================================
        # Tang tong so lan scan
        # =================================================

        STATS["total_scans"] += 1

        # =================================================
        # Kiem tra cache
        # Neu URL da scan roi thi tra ket qua luon
        # =================================================

        if url in CACHE:

            STATS["cache_hits"] += 1

            print("[CACHE HIT]", url)

            return CACHE[url]

        # =================================================
        # Tach domain
        # =================================================

        domain = urlparse(url).netloc.lower()

        # =================================================
        # Kiem tra reputation domain
        # Neu domain da tung phishing thi chan luon
        # =================================================

        if domain in DOMAIN_REPUTATION:

            STATS["domain_blocks"] += 1

            print("[DOMAIN BLOCKED]", domain)

            result = {
                "url": url,
                "is_phishing": True,
                "confidence": 1.0,
                "source": "domain_reputation",
                "threshold": predictor.threshold,
                "reason": ["Known phishing domain"]
            }

            # Luu cache
            CACHE[url] = result

            save_data()

            return result

        # =================================================
        # Rule engine check
        # =================================================

        rule = check_rules(url)

        # =================================================
        # URL trusted
        # =================================================

        if rule == 0:

            STATS["safe_urls"] += 1

            result = {
                "url": url,
                "is_phishing": False,
                "confidence": 0.0,
                "source": "rule",
                "threshold": predictor.threshold,
                "reason": ["Trusted domain"]
            }

            # Luu cache
            CACHE[url] = result

            save_data()

            return result

        # =================================================
        # Rule detect phishing
        # =================================================

        if rule == 1:

            STATS["phishing_detected"] += 1

            # Danh dau domain nguy hiem
            DOMAIN_REPUTATION[domain] = True

            result = {
                "url": url,
                "is_phishing": True,
                "confidence": 1.0,
                "source": "rule",
                "threshold": predictor.threshold,
                "reason": ["Rule engine detected phishing"]
            }

            # Luu cache
            CACHE[url] = result

            save_data()

            return result

        # =================================================
        # Extract features tu URL
        # =================================================

        features = extract_features(url)

        # =================================================
        # Predict bang ML model
        # =================================================

        prob = predictor.predict_proba(features)

        is_phishing = prob > predictor.threshold

        # =================================================
        # Log ket qua
        # =================================================

        print(f"[LOG] {url} -> prob={prob}")

        # =================================================
        # Tao response
        # =================================================

        result = {
            "url": url,
            "is_phishing": bool(is_phishing),
            "confidence": float(prob),
            "source": "ml",
            "threshold": predictor.threshold,
            "reason": generate_reason(url)
        }

        # =================================================
        # Neu ML detect phishing
        # thi danh dau domain nguy hiem
        # =================================================

        if is_phishing:

            STATS["phishing_detected"] += 1

            DOMAIN_REPUTATION[domain] = True

        else:

            STATS["safe_urls"] += 1

        # =================================================
        # Luu cache
        # =================================================

        CACHE[url] = result

        save_data()

        return result

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

# =========================================================
# API thong ke he thong
# =========================================================

@app.get("/stats")
def stats():

    return {
        "stats": STATS,
        "cache_size": len(CACHE),
        "blocked_domains": len(DOMAIN_REPUTATION)
    }

# =========================================================
# Tao ly do giai thich cho user
# =========================================================

def generate_reason(url: str):

    reasons = []

    if len(url) > 75:
        reasons.append("URL too long")

    if "@" in url:
        reasons.append("Contains @ symbol")

    if "login" in url.lower():
        reasons.append("Contains login keyword")

    if "secure" in url.lower():
        reasons.append("Contains secure keyword")

    if "-" in url:
        reasons.append("Contains hyphen")

    return reasons

import re
import ipaddress
from urllib.parse import urlparse

# =========================================================
# LOAD BLACKLIST
# =========================================================

BLACKLIST = set()

try:

    with open("data/blacklist.txt") as f:

        for line in f:

            line = line.strip().lower()

            if line:
                BLACKLIST.add(line)

except:

    print("Blacklist not loaded")

# =========================================================
# TRUSTED DOMAINS
# =========================================================

WHITELIST = [
    "google.com",
    "facebook.com",
    "youtube.com",
    "github.com",
    "paypal.com",
    "amazon.com",
    "apple.com",
    "microsoft.com",
    "linkedin.com",
    "netflix.com",
    "shopee.vn",
    "openai.com"
]

# =========================================================
# REAL BRANDS TARGETED BY PHISHING
# =========================================================

REAL_BRANDS = [
    "google",
    "facebook",
    "paypal",
    "apple",
    "amazon",
    "microsoft",
    "youtube",
    "netflix",
    "instagram",
    "linkedin",
    "telegram",
    "discord",
    "steam",
    "openai",
    "chatgpt",
    "gmail",
    "outlook",
    "office365",
    "icloud",
    "binance",
    "coinbase"
]

# =========================================================
# PHISHING KEYWORDS
# =========================================================

SUSPICIOUS_KEYWORDS = [
    "login",
    "signin",
    "verify",
    "verification",
    "secure",
    "security",
    "account",
    "update",
    "confirm",
    "password",
    "wallet",
    "bank",
    "support",
    "recovery",
    "unlock",
    "suspended",
    "billing",
    "payment",
    "invoice",
    "gift",
    "bonus",
    "crypto",
    "airdrop"
]

# =========================================================
# SUSPICIOUS TLDS
# =========================================================

BAD_TLDS = [
    ".tk",
    ".ml",
    ".ga",
    ".cf",
    ".gq",
    ".xyz",
    ".top",
    ".click",
    ".work",
    ".support",
    ".country",
    ".stream"
]

# =========================================================
# HOMOGLYPH / LOOKALIKE MAP
# =========================================================

HOMOGLYPHS = {
    "0": "o",
    "1": "l",
    "3": "e",
    "4": "a",
    "5": "s",
    "7": "t",
    "@": "a",
    "$": "s",
    "!": "i",
    "|": "l",
    "I": "l"
}

# =========================================================
# NORMALIZE DOMAIN
# =========================================================

def normalize_domain(domain: str):

    normalized = ""

    for c in domain:

        normalized += HOMOGLYPHS.get(c, c)

    return normalized.lower()

# =========================================================
# CHECK IF IP ADDRESS
# =========================================================

def is_ip(domain: str):

    try:

        ipaddress.ip_address(domain.split(":")[0])

        return True

    except:

        return False

# =========================================================
# MAIN RULE ENGINE
# =========================================================

def check_rules(url):

    parsed = urlparse(url)

    domain = parsed.netloc.lower()

    path = parsed.path.lower()

    # remove port
    domain = domain.split(":")[0]

    normalized_domain = normalize_domain(domain)

    print("DOMAIN:", domain)

    print("NORMALIZED:", normalized_domain)

    # =====================================================
    # IGNORE INTERNAL BROWSER URLS
    # =====================================================

    if (
        url.startswith("chrome://") or
        url.startswith("edge://") or
        url.startswith("about:") or
        url.startswith("chrome-error://")
    ):

        return 0

    # =====================================================
    # IGNORE LOCALHOST
    # =====================================================

    if (
        domain == "localhost" or
        domain.startswith("127.") or
        domain.startswith("192.168.") or
        domain.startswith("10.")
    ):

        return 0

    # =====================================================
    # BLACKLIST CHECK
    # =====================================================

    if (
        domain in BLACKLIST or
        normalized_domain in BLACKLIST
    ):

        print("[BLACKLIST HIT]", domain)

        return 1

    # =====================================================
    # WHITELIST
    # =====================================================

    for site in WHITELIST:

        if (
            domain == site or
            domain.endswith("." + site)
        ):

            return 0

    # =====================================================
    # RAW IP ADDRESS
    # =====================================================

    if is_ip(domain):

        return 1

    # =====================================================
    # @ SYMBOL TRICK
    # =====================================================

    if "@" in url:

        return 1

    # =====================================================
    # DOUBLE // TRICK
    # =====================================================

    if url.count("//") > 1:

        return 1

    # =====================================================
    # TOO MANY HYPHENS
    # =====================================================

    if domain.count("-") >= 3:

        return 1

    # =====================================================
    # TOO MANY SUBDOMAINS
    # =====================================================

    if domain.count(".") >= 4:

        return 1

    # =====================================================
    # BAD TLD
    # =====================================================

    if any(domain.endswith(tld) for tld in BAD_TLDS):

        return 1

    # =====================================================
    # PUNYCODE / IDN SPOOF
    # =====================================================

    if "xn--" in domain:

        return 1

    # =====================================================
    # BRAND SPOOF DETECTION
    # =====================================================

    for brand in REAL_BRANDS:

        if brand in normalized_domain:

            official = [
                f"{brand}.com",
                f"www.{brand}.com"
            ]

            legit = any(
                domain == o or domain.endswith("." + o)
                for o in official
            )

            if not legit:

                return 1

    # =====================================================
    # SUSPICIOUS KEYWORDS
    # =====================================================

    keyword_hits = sum(
        keyword in url.lower()
        for keyword in SUSPICIOUS_KEYWORDS
    )

    if keyword_hits >= 2:

        return 1

    # =====================================================
    # SUSPICIOUS FILE TYPES
    # =====================================================

    suspicious_files = [
        ".exe",
        ".scr",
        ".zip",
        ".rar",
        ".js",
        ".bat"
    ]

    if any(path.endswith(ext) for ext in suspicious_files):

        return 1

    # =====================================================
    # LONG DOMAIN
    # =====================================================

    if len(domain) > 45:

        return 1

    # =====================================================
    # RANDOM LOOKING DOMAIN
    # =====================================================

    random_pattern = re.search(
        r"[a-z0-9]{18,}",
        domain.replace("-", "")
    )

    if random_pattern:

        return 1

    # =====================================================
    # URL SHORTENER
    # =====================================================

    shorteners = [
        "bit.ly",
        "tinyurl.com",
        "goo.gl",
        "t.co",
        "is.gd",
        "ow.ly"
    ]

    if any(domain.endswith(s) for s in shorteners):

        return 1

    return None

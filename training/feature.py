import re
import math

from urllib.parse import urlparse

# =========================================================
# KEYWORDS
# =========================================================

SUSPICIOUS_KEYWORDS = [
    "login",
    "verify",
    "bank",
    "secure",
    "account",
    "signin",
    "update",
    "confirm",
    "password",
    "wallet",
    "recovery",
    "unlock",
    "billing",
    "payment"
]

# =========================================================
# BAD TLDS
# =========================================================

BAD_TLDS = [
    ".tk",
    ".ml",
    ".ga",
    ".cf",
    ".xyz",
    ".top",
    ".click",
    ".work"
]

# =========================================================
# BRANDS
# =========================================================

BRANDS = [
    "paypal",
    "google",
    "facebook",
    "apple",
    "amazon",
    "microsoft",
    "youtube",
    "instagram",
    "netflix",
    "gmail",
    "icloud"
]

# =========================================================
# ENTROPY
# =========================================================

def entropy(s):

    if len(s) == 0:
        return 0

    prob = [
        float(s.count(c)) / len(s)
        for c in dict.fromkeys(list(s))
    ]

    return -sum([
        p * math.log2(p)
        for p in prob
    ])

# =========================================================
# SPECIAL CHARACTER COUNT
# =========================================================

def count_special_chars(s):

    special_chars = "-_=@%&?$"

    return sum(
        c in special_chars
        for c in s
    )

# =========================================================
# REPEATED CHARACTERS
# vd:
# gooooogle-login
# =========================================================

def has_repeated_chars(domain):

    return int(
        bool(
            re.search(r"(.)\1{2,}", domain)
        )
    )

# =========================================================
# PATH DEPTH
# vd:
# /login/account/verify
# =========================================================

def path_depth(path):

    return len([
        p for p in path.split("/")
        if p
    ])

# =========================================================
# ENCODED CHARACTERS
# vd:
# %20 %2F
# =========================================================

def encoded_chars(url):

    return url.count("%")

# =========================================================
# SUSPICIOUS FILE
# =========================================================

def suspicious_file(path):

    suspicious = [
        ".php",
        ".exe",
        ".scr",
        ".zip",
        ".rar",
        ".js"
    ]

    return int(
        any(
            path.endswith(ext)
            for ext in suspicious
        )
    )

# =========================================================
# RANDOM LOOKING DOMAIN
# vd:
# ajskdjqwiozxcm
# =========================================================

def random_domain(domain):

    return int(
        bool(
            re.search(
                r"[a-z0-9]{15,}",
                domain.replace("-", "")
            )
        )
    )

# =========================================================
# FEATURE EXTRACTION
# =========================================================

def extract_features(url):

    parsed = urlparse(url)

    domain = parsed.netloc.lower()

    path = parsed.path.lower()

    features = []

    # =====================================================
    # 1. URL LENGTH
    # =====================================================

    features.append(len(url))

    # =====================================================
    # 2. DIGIT RATIO
    # =====================================================

    digits = sum(
        c.isdigit()
        for c in domain
    )

    features.append(
        digits / len(domain)
        if len(domain) > 0 else 0
    )

    # =====================================================
    # 3. HTTPS
    # =====================================================

    features.append(
        int(
            url.startswith("https")
        )
    )

    # =====================================================
    # 4. DOT COUNT
    # =====================================================

    features.append(
        domain.count(".")
    )

    # =====================================================
    # 5. HAS IP ADDRESS
    # =====================================================

    features.append(
        int(
            bool(
                re.search(
                    r"\d+\.\d+\.\d+\.\d+",
                    domain
                )
            )
        )
    )

    # =====================================================
    # 6. KEYWORD COUNT
    # =====================================================

    keyword_count = sum(
        k in url.lower()
        for k in SUSPICIOUS_KEYWORDS
    )

    features.append(keyword_count)

    # =====================================================
    # 7. BAD TLD
    # =====================================================

    features.append(
        int(
            any(
                domain.endswith(tld)
                for tld in BAD_TLDS
            )
        )
    )

    # =====================================================
    # 8. DOMAIN LENGTH
    # =====================================================

    features.append(
        len(domain)
    )

    # =====================================================
    # 9. PATH LENGTH
    # =====================================================

    features.append(
        len(path)
    )

    # =====================================================
    # 10. HYPHEN COUNT
    # =====================================================

    features.append(
        domain.count("-")
    )

    # =====================================================
    # 11. ENTROPY
    # =====================================================

    features.append(
        entropy(domain)
    )

    # =====================================================
    # 12. SUBDOMAIN COUNT
    # =====================================================

    features.append(
        max(domain.count(".") - 1, 0)
    )

    # =====================================================
    # 13. BRAND SPOOF
    # =====================================================

    brand_spoof = 0

    for brand in BRANDS:

        if brand in domain:

            legit_patterns = [
                f"{brand}.com",
                f"www.{brand}.com"
            ]

            if not any(
                domain == p or
                domain.endswith("." + p)
                for p in legit_patterns
            ):

                brand_spoof = 1

    features.append(brand_spoof)

    # =====================================================
    # 14. SUSPICIOUS CHAR COUNT
    # =====================================================

    suspicious_chars = [
        "0",
        "1",
        "I",
        "l",
        "@"
    ]

    features.append(
        sum(
            c in domain
            for c in suspicious_chars
        )
    )

    # =====================================================
    # 15. SPECIAL CHAR COUNT
    # =====================================================

    features.append(
        count_special_chars(url)
    )

    # =====================================================
    # 16. REPEATED CHARS
    # =====================================================

    features.append(
        has_repeated_chars(domain)
    )

    # =====================================================
    # 17. PATH DEPTH
    # =====================================================

    features.append(
        path_depth(path)
    )

    # =====================================================
    # 18. ENCODED CHAR COUNT
    # =====================================================

    features.append(
        encoded_chars(url)
    )

    # =====================================================
    # 19. SUSPICIOUS FILE
    # =====================================================

    features.append(
        suspicious_file(path)
    )

    # =====================================================
    # 20. RANDOM DOMAIN
    # =====================================================

    features.append(
        random_domain(domain)
    )

    return features

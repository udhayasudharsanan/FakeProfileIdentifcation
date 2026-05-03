from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
from web3 import Web3
import joblib
import numpy as np
import os
import pandas as pd
import datetime
import hashlib
import requests as req
import json
import re
import urllib.parse
import http.client


load_dotenv()
_llm_call_count = 0
# ── API Toggle ────────────────────────────────────────────────
# Set USE_NEW_API = True  → uses new API (when old one hits limit)
# Set USE_NEW_API = False → uses old API (when it renews next month)
USE_NEW_API = True

OLD_API = {
    "HOST": "instagram-scraper21.p.rapidapi.com",
    "KEY" : "7ea5b0e395msh5688a5c3c54ddfep17130fjsn23fdd59f6952"
}

NEW_API = {
    "HOST": "instagram-api-fast-reliable-data-scraper.p.rapidapi.com",
    "KEY" : "7ea5b0e395msh5688a5c3c54ddfep17130fjsn23fdd59f6952"
}

RAPIDAPI_HOST = NEW_API["HOST"] if USE_NEW_API else OLD_API["HOST"]
RAPIDAPI_KEY  = NEW_API["KEY"]  if USE_NEW_API else OLD_API["KEY"]

app = Flask(__name__)
CORS(app)

model  = joblib.load('../ml/model.pkl')
scaler = joblib.load('../ml/scaler.pkl')

client     = MongoClient(os.getenv('MONGO_URI'))
db         = client['fakeprofiledb']
collection = db['results']

w3 = Web3(Web3.HTTPProvider(os.getenv('INFURA_URL')))

with open('contract_abi.json') as f:
    contract_abi = json.load(f)

contract = w3.eth.contract(
    address=Web3.to_checksum_address(os.getenv('CONTRACT_ADDRESS')),
    abi=contract_abi
)

WALLET_ADDRESS = os.getenv('WALLET_ADDRESS')
PRIVATE_KEY    = os.getenv('PRIVATE_KEY')

linkedin_model = joblib.load('../mlForLinkedIn/linkedin_model.pkl')

# ════════════════════════════════════════════════════════════
# SCAM KEYWORDS
# ════════════════════════════════════════════════════════════
SCAM_KEYWORDS = {
    'trading_scam': [
        'trading', 'forex', 'crypto trading', 'binary options', 'bitcoin profit',
        'invest now', 'guaranteed profit', 'daily profit', 'passive income',
        'financial freedom', 'trading signals', 'pump and dump', 'get rich',
        '100% profit', 'risk free', 'double your money', 'trading expert',
        'forex trader', 'crypto investor', 'trading account', 'profits daily',
        'earn daily', 'trade with me', 'investment opportunity',
        '100% legit', 'dm for proof', 'proof of payment', 'no scam',
        'happy client', 'testimony', 'trust the process', 'payment received',
        'roi', 'high returns', 'instant profit', 'zero loss', 'no loss',
        'withdraw anytime', 'vip signals', 'premium signals',
        'crypto signals', 'forex signals', 'stock signals',
        'investment plan', 'double investment', 'profit system',
        'daily earning system', 'automated trading', 'ai trading',
        'btc investment', 'eth investment', 'usdt investment',
        'join my trading group', 'copy trading', 'signal group'
    ],
    'job_scam': [
        'work from home', 'wfh', 'earn 10k', 'earn 20k', 'earn 50k',
        'part time job', 'home based job', 'data entry job', 'online job',
        'urgent hiring', 'no experience needed', 'weekly payment',
        'daily payment', 'salary guaranteed', 'hiring now', 'job offer',
        'earn from home', 'make money online', 'easy money', 'extra income',
        'side income', 'online income', 'work at home', 'high salary',
        'per day earning', 'per week earning', 'flexible hours',
        'earn per day', 'earn per week',
        'typing job', 'captcha job', 'form filling job',
        'telegram job', 'whatsapp job', 'instagram job',
        'no interview', 'instant joining', 'direct joining',
        'salary per day', 'registration fee', 'processing fee',
        'pay and start', 'pay and join', 'zero investment job',
        'earn without investment', 'home job', 'quick earning',
        'earn 500 daily', 'earn 1000 daily', 'earn fast',
        'simple work high income', 'no skills needed'
    ],
    'ecommerce_scam': [
        'huge discount', 'mega sale', '90% off', '80% off', '70% off',
        '60% off', '50% off', 'flash sale', 'today only',
        'limited offer', 'exclusive deal', 'offer valid today', 'deal ends soon',
        'lowest price guarantee', 'unbeatable price',
        'below mrp', 'below market', 'at cost price',
        'first copy', 'replica', 'super copy', 'mirror copy', 'aaa quality',
        '1:1 copy', 'master copy', 'premium copy', 'mirror quality',
        'original like copy', 'same as original', 'imported quality',
        'luxury for cheap', 'branded at low price',
        'iphone cheap', 'samsung cheap', 'airpods cheap',
        'iphone wholesale', 'original iphone',
        'dm for price', 'dm to order', 'whatsapp to order',
        'dm to buy', 'inbox to buy', 'dm for offer',
        'click link in bio', 'link in bio',
        'wholesale price', 'factory price',
        'direct supplier', 'reseller needed', 'reseller welcome',
        'reseller price', 'dropshipping business', 'drop shipping',
        'distributor price', 'agent price',
        'bulk order', 'earn commission', 'referral bonus',
        'trusted seller', 'legit seller', '100% original',
        'genuine product', 'no fake', 'safe to order',
        'cod available', 'cash on delivery',
        'bitcoin payment', 'usdt payment', 'crypto accepted',
        'limited stock', 'grab now', 'hot deal',
        'free products', 'free shipping',
        'cheap price', 'premium quality low price'
    ],
    'adult_spam': [
        'onlyfans', 'f4f', 'l4l', 'follow for follow',
        'paid content', 'vip content', 'private content',
        'hot content', '18+', 'nsfw', 'uncensored',
        'unlock content', 'premium access',
        'adult content', 'adult only', 'adult page',
        'explicit content', 'mature content',
        'fans page', 'fanpage 18', 'only fans'
    ],
    'giveaway_scam': [
        'giveaway', 'free iphone', 'free gift', 'win now', 'lucky winner',
        'congratulations you won', 'claim your prize', 'free cash',
        'free money', 'sponsored giveaway', 'tag friends to win',
        'limited giveaway', 'first 100 people', 'random winner',
        'selected winner', 'winner announced soon', 'instant win',
        'comment to win', 'share to win', 'follow to win', 'dm to claim',
        'click to claim', 'grab your prize', 'free reward', 'gift waiting',
        'claim now', 'hurry winner'
    ]
}

SUSPICIOUS_TLDS = [
    '.xyz', '.tk', '.ml', '.ga', '.cf', '.gq', '.pw', '.top',
    '.click', '.link', '.online', '.site', '.website', '.space',
    '.fun', '.icu', '.vip', '.shop', '.store', '.live', '.work'
]

URL_SHORTENERS = [
    'bit.ly', 'tinyurl.com', 't.co', 'ow.ly', 'short.io',
    'rb.gy', 'cutt.ly', 'tiny.cc', 'is.gd', 'v.gd',
    'buff.ly', 'su.pr', 'lnkd.in', 'adf.ly', 'linktr.ee',
    'beacons.ai', 'bio.link', 'taplink.cc', 'campsite.bio',
    'solo.to', 'allmylinks.com', 'contact.me'
]

URL_SCAM_WORDS = [
    'earn', 'profit', 'forex', 'crypto', 'bitcoin', 'invest',
    'trading', 'income', 'money', 'cash', 'rich', 'millionaire',
    'free', 'win', 'prize', 'giveaway', 'loan', 'job', 'hiring',
    'work-from-home', 'wfh', 'passive', 'signal', 'copy-trade',
    'discount', 'sale', 'cheap', 'offer', 'deal', 'wholesale',
    'replica', 'copy', 'first-copy', 'supplier', 'dropship'
]

@app.route('/test-llm', methods=['GET'])
def test_llm():
    """Test route — visit http://localhost:5000/test-llm in browser"""
    GEMINI_KEY = os.getenv("GEMINI_API_KEY", "").strip()

    if not GEMINI_KEY:
        return jsonify({"error": "GEMINI_API_KEY not set in .env"})

    try:
        resp = req.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}",
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": "Reply with exactly: WORKING"}]}]},
            timeout=10
        )
        return jsonify({
            "status"  : resp.status_code,
            "response": resp.json(),
            "key_used": GEMINI_KEY[:10] + "..."
        })
    except Exception as e:
        return jsonify({"error": str(e)})
# ════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════

def analyze_text_for_scams(text):
    if not text:
        return {'found': False, 'keywords': [], 'categories': [], 'score_boost': 0}

    text_lower       = text.lower()
    found_keywords   = []
    found_categories = []

    for category, keywords in SCAM_KEYWORDS.items():
        hits = [kw for kw in keywords if kw in text_lower]
        if hits:
            found_keywords.extend(hits)
            found_categories.append(category)

    found_keywords   = list(set(found_keywords))
    found_categories = list(set(found_categories))

    STRONG_KEYWORDS = [
        'guaranteed profit', 'double your money', 'risk free', 'no loss',
        'investment opportunity', '100% profit', 'passive income',
        'earn daily', 'zero loss', 'instant profit', 'high returns',
        'first copy', 'replica', '1:1 copy', 'mirror copy', 'super copy',
        'iphone wholesale', 'iphone cheap', 'samsung cheap',
        'reseller welcome', 'direct supplier', 'dropshipping business',
        'forex trader', 'crypto signals', 'signal group', 'copy trading',
        'earn 500 daily', 'earn 1000 daily', 'registration fee',
        'pay and join', 'pay and start'
    ]

    MEDIUM_KEYWORDS = [
        'dm for price', 'dm to order', 'whatsapp to order', 'inbox to buy',
        'wholesale price', 'factory price', 'bulk order', 'agent price',
        'trusted seller', 'legit seller', 'cod available', 'cash on delivery',
        'no fake', 'safe to order', '100% original', 'genuine product',
        'link in bio', 'click link in bio', 'earn commission',
        'work from home', 'part time job', 'data entry job', 'home based job',
        'trading signals', 'forex signals', 'btc investment'
    ]

    score_boost = 0
    strong_hits = [kw for kw in found_keywords if kw in STRONG_KEYWORDS]
    medium_hits = [kw for kw in found_keywords if kw in MEDIUM_KEYWORDS]
    weak_hits   = [kw for kw in found_keywords if kw not in STRONG_KEYWORDS and kw not in MEDIUM_KEYWORDS]

    score_boost += len(strong_hits) * 20

    if len(medium_hits) >= 2:
        score_boost += len(medium_hits) * 8
    elif len(medium_hits) == 1:
        score_boost += 5

    if len(found_keywords) >= 3:
        score_boost += len(weak_hits) * 3

    # Pattern-based detection
    if (('dm' in text_lower or 'whatsapp' in text_lower) and
        ('iphone' in text_lower or 'samsung' in text_lower or 'mobile' in text_lower) and
        ('cheap' in text_lower or 'wholesale' in text_lower or 'price' in text_lower)):
        score_boost += 30
        if 'ecommerce_scam' not in found_categories:
            found_categories.append('ecommerce_scam')

    if (('invest' in text_lower or 'trading' in text_lower) and
        ('profit' in text_lower or 'earn' in text_lower) and
        ('daily' in text_lower or 'guaranteed' in text_lower)):
        score_boost += 35
        if 'trading_scam' not in found_categories:
            found_categories.append('trading_scam')

    if (('job' in text_lower or 'hiring' in text_lower or 'work' in text_lower) and
        ('home' in text_lower or 'online' in text_lower) and
        ('earn' in text_lower or 'salary' in text_lower or 'payment' in text_lower)):
        score_boost += 25
        if 'job_scam' not in found_categories:
            found_categories.append('job_scam')

    score_boost = min(score_boost, 55)

    return {
        'found'      : len(found_keywords) > 0,
        'keywords'   : found_keywords[:10],
        'categories' : list(set(found_categories)),
        'score_boost': score_boost
    }


def fetch_recent_captions_old_api(username, headers, max_posts=5):
    """Fetch captions using OLD API"""
    try:
        r = req.get(
            f"https://{RAPIDAPI_HOST}/api/v1/posts",
            headers=headers,
            params={"username": username, "count": max_posts}
        )
        data  = r.json()
        print("Posts response:", str(data)[:300])

        items = (
            data.get('data', {}).get('items') or
            data.get('data', {}).get('posts') or
            data.get('items') or
            data.get('posts') or []
        )

        captions = []
        for item in items[:max_posts]:
            caption = (
                item.get('caption', {}).get('text', '')
                if isinstance(item.get('caption'), dict)
                else item.get('caption') or item.get('text') or ''
            )
            if caption:
                captions.append(str(caption))

        print(f"Fetched {len(captions)} post captions")
        return captions

    except Exception as e:
        print("Post fetch error:", e)
        return []


def fetch_recent_captions_new_api(user_id, headers, max_posts=5):
    try:
        # CORRECT ENDPOINT IS /feed
        r = req.get(
            f"https://{RAPIDAPI_HOST}/feed",
            headers=headers,
            params={"user_id": user_id}
        )
        data = r.json()
        print("New API feed response:", str(data)[:300])

        # /feed returns {"items": [...]}
        items = data.get('items') or []

        captions = []
        for item in items[:max_posts]:
            # Caption is nested: item -> caption -> text
            cap_obj = item.get('caption')
            if isinstance(cap_obj, dict):
                caption = cap_obj.get('text', '')
            elif isinstance(cap_obj, str):
                caption = cap_obj
            else:
                caption = ''

            if caption:
                captions.append(str(caption))

        print(f"Fetched {len(captions)} captions (new API /feed)")
        return captions

    except Exception as e:
        print("New API feed fetch error:", e)
        return []


def analyze_posts_for_scams(captions):
    if not captions:
        return {
            'found': False, 'keywords': [], 'categories': [],
            'score_boost': 0, 'posts_analyzed': 0
        }

    all_keywords   = []
    all_categories = []
    total_boost    = 0

    for caption in captions:
        scan = analyze_text_for_scams(caption)
        all_keywords.extend(scan['keywords'])
        all_categories.extend(scan['categories'])
        total_boost += scan['score_boost']

    avg_boost = round(total_boost / len(captions), 2)

    return {
        'found'         : len(set(all_keywords)) > 0,
        'keywords'      : list(set(all_keywords))[:15],
        'categories'    : list(set(all_categories)),
        'score_boost'   : min(45, avg_boost),
        'posts_analyzed': len(captions)
    }
def analyze_with_llm(bio, captions, username):
    try:
        GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
        if not GEMINI_KEY:
            print("No Gemini API key — skipping LLM analysis")
            return None

        captions_text = '\n'.join([f"- {c[:200]}" for c in captions[:5]]) if captions else 'No posts available'

        prompt = f"""You are a social media fraud analyst. Analyze this Instagram profile.

Username: @{username}

Bio:
{bio or 'No bio'}

Recent post captions:
{captions_text}

Look for: fake product selling, investment scams, job scams, fake giveaways, suspicious selling patterns.

Respond ONLY in this exact JSON format, no other text:
{{
  "verdict": "SCAM",
  "confidence": 85,
  "reason": "one sentence explanation",
  "scam_type": "ecommerce_scam"
}}

verdict must be exactly: SCAM or LEGIT or SUSPICIOUS
scam_type must be exactly: ecommerce_scam or trading_scam or job_scam or giveaway_scam or none"""
        global _llm_call_count
        _llm_call_count += 1
        print(f"Gemini call #{_llm_call_count} this session")
        response = req.post(
          f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature"    : 0.1,
                    "maxOutputTokens": 300,
                    "thinkingConfig" : {"thinkingBudget": 0}
                }
            },
            timeout=15
        )

        if response.status_code != 200:
            print(f"Gemini error: {response.status_code} {response.text[:200]}")
            return None

        resp_json = response.json()
        text = resp_json['candidates'][0]['content']['parts'][0]['text'].strip()
        text = re.sub(r'```json|```', '', text).strip()
        print(f"Gemini raw: {text}")

        result     = json.loads(text)
        verdict    = result.get('verdict', 'LEGIT')
        confidence = int(result.get('confidence', 0))
        reason     = result.get('reason', '')
        scam_type  = result.get('scam_type', 'none')

        if verdict == 'SCAM':
            llm_boost = min(40, confidence // 2)
        elif verdict == 'SUSPICIOUS':
            llm_boost = min(20, confidence // 4)
        else:
            llm_boost = 0

        return {
            'verdict'   : verdict,
            'confidence': confidence,
            'reason'    : reason,
            'scam_type' : scam_type,
            'llm_boost' : llm_boost
        }

    except json.JSONDecodeError as e:
        print(f"Gemini JSON parse error: {e} — raw: {text if 'text' in dir() else 'no text'}")
        return None
    except Exception as e:
        print(f"Gemini error: {e}")
        return None

def analyze_website(url):
    if not url or not url.strip():
        return {
            'checked': False, 'url': '', 'risk_signals': [],
            'categories': [], 'score_boost': 0,
            'is_shortener': False, 'suspicious_tld': False,
            'ssl': None, 'content_scan': {}
        }

    url = url.strip()
    if not url.startswith('http'):
        url = 'https://' + url

    risk_signals   = []
    categories     = []
    score_boost    = 0
    is_shortener   = False
    suspicious_tld = False
    ssl            = url.startswith('https')

    try:
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.lower().replace('www.', '')
        path   = parsed.path.lower()
        full   = (domain + path).lower()

        for shortener in URL_SHORTENERS:
            if shortener in domain:
                is_shortener = True
                risk_signals.append(f'Uses URL shortener ({shortener}) — hides real destination')
                score_boost += 10
                break

        for tld in SUSPICIOUS_TLDS:
            if domain.endswith(tld):
                suspicious_tld = True
                risk_signals.append(f'Suspicious domain extension ({tld}) — commonly used in scams')
                score_boost += 15
                categories.append('suspicious_domain')
                break

        url_scam_hits = [w for w in URL_SCAM_WORDS if w in full]
        if url_scam_hits:
            risk_signals.append(f'Scam-related words in URL: {", ".join(url_scam_hits[:3])}')
            score_boost += len(url_scam_hits) * 5

        if not ssl:
            risk_signals.append('No HTTPS — website has no security certificate')
            score_boost += 10

        content_scan = {}
        try:
            headers_web = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response    = req.get(url, headers=headers_web, timeout=6, allow_redirects=True)
            final_domain = urllib.parse.urlparse(response.url).netloc.lower().replace('www.', '')

            SAFE_REDIRECT_DOMAINS = [
                'google.com', 'google.co.in', 'maps.google.com',
                'youtube.com', 'facebook.com', 'instagram.com',
                'amazon.com', 'flipkart.com', 'zomato.com',
                'justdial.com', 'indiamart.com', 'twitter.com',
                'x.com', 'linkedin.com', 'whatsapp.com'
            ]
            is_safe_redirect = any(safe in final_domain for safe in SAFE_REDIRECT_DOMAINS)

            if final_domain != domain and domain not in final_domain and not is_safe_redirect:
                risk_signals.append(f'URL redirects to different domain: {final_domain}')
                score_boost += 15
                categories.append('suspicious_redirect')

            clean_text = re.sub(r'<[^>]+>', ' ', response.text.lower())
            clean_text = re.sub(r'\s+', ' ', clean_text)[:5000]

            page_scan = analyze_text_for_scams(clean_text)
            if page_scan['found']:
                content_scan = {
                    'scam_found'   : True,
                    'categories'   : page_scan['categories'],
                    'keyword_count': len(page_scan['keywords'])
                }
                risk_signals.append('Website content contains suspicious keywords')
                score_boost += page_scan['score_boost'] * 0.5
                for cat in page_scan['categories']:
                    if cat not in categories:
                        categories.append(cat)
            else:
                content_scan = {'scam_found': False}

        except req.exceptions.Timeout:
            risk_signals.append('Website did not respond (timeout) — may be inactive or fake')
            score_boost += 8
        except req.exceptions.ConnectionError:
            risk_signals.append('Website is unreachable — domain may not exist')
            score_boost += 20
            categories.append('unreachable_website')
        except Exception as e:
            print("Website content fetch error:", e)

    except Exception as e:
        print("URL parse error:", e)
        risk_signals.append('Could not analyze URL')

    return {
        'checked'       : True,
        'url'           : url,
        'risk_signals'  : risk_signals,
        'categories'    : list(set(categories)),
        'score_boost'   : min(40, round(score_boost, 2)),
        'is_shortener'  : is_shortener,
        'suspicious_tld': suspicious_tld,
        'ssl'           : ssl,
        'content_scan'  : content_scan,
        'signals_count' : len(risk_signals)
    }


def generate_hash(data):
    raw = str(data).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def store_on_blockchain(profile_id, result, data_hash):
    try:
        current_nonce = w3.eth.get_transaction_count(
            Web3.to_checksum_address(WALLET_ADDRESS), 'pending'
        )
        print(f"Current nonce: {current_nonce}")
        txn = contract.functions.storeVerification(
            profile_id, result, data_hash
        ).build_transaction({
            'chainId' : 11155111,
            'gas'     : 200000,
            'gasPrice': w3.to_wei('30', 'gwei'),
            'nonce'   : current_nonce
        })
        signed  = w3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        tx_hex  = w3.to_hex(tx_hash)
        print("BLOCKCHAIN SUCCESS! TX:", tx_hex)
        return tx_hex
    except Exception as e:
        print("Blockchain error:", e)
        if 'nonce too low' in str(e):
            try:
                retry_nonce = w3.eth.get_transaction_count(
                    Web3.to_checksum_address(WALLET_ADDRESS), 'pending'
                ) + 1
                txn = contract.functions.storeVerification(
                    profile_id, result, data_hash
                ).build_transaction({
                    'chainId' : 11155111,
                    'gas'     : 200000,
                    'gasPrice': w3.to_wei('30', 'gwei'),
                    'nonce'   : retry_nonce
                })
                signed  = w3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
                tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
                tx_hex  = w3.to_hex(tx_hash)
                print("BLOCKCHAIN SUCCESS (retry)! TX:", tx_hex)
                return tx_hex
            except Exception as e2:
                print("Blockchain retry error:", e2)
                return None
        return None


def get_risk_level(risk_score):
    if risk_score <= 20:
        return 'VERY LOW', 'Definitely Genuine'
    elif risk_score <= 40:
        return 'LOW', 'Likely Genuine'
    elif risk_score <= 60:
        return 'MEDIUM', 'Suspicious'
    elif risk_score <= 80:
        return 'HIGH', 'Likely Fake'
    else:
        return 'VERY HIGH', 'Definitely Fake'


def apply_scam_boost(ml_risk, ml_result, bio_scan, posts_scan, website_scan=None):
    """
    Combines ML + bio + posts + website.
    Enforces minimum 65% when scam detected.
    Prevents contradiction: FAKE + VERY LOW risk.
    """
    bio_scan     = bio_scan     or {}
    posts_scan   = posts_scan   or {}
    website_scan = website_scan or {}

    all_keywords   = list(set(bio_scan.get('keywords', []) + posts_scan.get('keywords', [])))
    all_categories = list(set(bio_scan.get('categories', []) + posts_scan.get('categories', [])))

    bio_boost   = bio_scan.get('score_boost', 0)
    posts_boost = posts_scan.get('score_boost', 0)
    web_boost   = 0
    web_signals = []

    if website_scan.get('checked'):
        web_boost   = website_scan.get('score_boost', 0)
        web_signals = website_scan.get('risk_signals', [])
        for cat in website_scan.get('categories', []):
            if cat not in all_categories:
                all_categories.append(cat)

    total_boost = min(65, bio_boost + posts_boost + web_boost)

    combined_scan = {
        'found'          : len(all_keywords) > 0 or web_boost > 0,
        'keywords'       : all_keywords[:15],
        'categories'     : all_categories,
        'score_boost'    : total_boost,
        'bio_keywords'   : bio_scan.get('keywords', []),
        'post_keywords'  : posts_scan.get('keywords', []),
        'posts_analyzed' : posts_scan.get('posts_analyzed', 0),
        'bio_boost'      : bio_boost,
        'posts_boost'    : posts_boost,
        'web_boost'      : web_boost,
        'web_signals'    : web_signals,
        'website_checked': website_scan.get('checked', False),
        'website_url'    : website_scan.get('url', ''),
        'website_ssl'    : website_scan.get('ssl')
    }

    if total_boost > 0:
        final_risk = min(100, round(ml_risk + total_boost, 2))
        if final_risk >= 50:
            final_risk   = max(final_risk, 65)  # enforce minimum 65 only when actually suspicious
            final_result = 'Fake'
        else:
            final_result = ml_result  # boost raised score but still low — trust ML
        print(f"Scam boost: ML={ml_risk}% + boost={total_boost}% → final={final_risk}%")
    else:
        final_risk   = ml_risk
        final_result = ml_result

    final_risk             = round(final_risk, 2)
    risk_level, risk_label = get_risk_level(final_risk)

    return final_result, final_risk, risk_level, risk_label, combined_scan


# ════════════════════════════════════════════════════════════
# NEW API: fetch profile
# ════════════════════════════════════════════════════════════
def fetch_profile_new_api(username, headers):
    try:
        # Step 1: get user ID
        r1      = req.get(
            f"https://{RAPIDAPI_HOST}/user_id_by_username",
            headers=headers,
            params={"username": username}
        )
        r1_data = r1.json()
        print("New API user_id response:", r1_data)

        user_id = (
            r1_data.get('UserID') or
            r1_data.get('user_id') or
            r1_data.get('id')
        )

        if not user_id:
            print("Could not extract user_id from:", r1_data)
            return None

        print(f"Extracted user_id: {user_id}")

        # Step 2: get profile — CORRECT ENDPOINT IS /profile
        r2      = req.get(
            f"https://{RAPIDAPI_HOST}/profile",
            headers=headers,
            params={"user_id": user_id}
        )
        r2_data = r2.json()
        print("New API profile response:", str(r2_data)[:400])

        # /profile returns flat dict directly — no nesting
        user = r2_data

        return {
            "username"       : user.get('username') or username,
            "follower_count" : user.get('follower_count') or user.get('edge_followed_by', {}).get('count') or 0,
            "following_count": user.get('following_count') or user.get('edge_follow', {}).get('count') or 0,
            "media_count"    : user.get('media_count') or user.get('edge_owner_to_timeline_media', {}).get('count') or 0,
            "biography"      : user.get('biography') or user.get('bio') or '',
            "full_name"      : user.get('full_name') or username,
            "is_private"     : user.get('is_private') or False,
            "external_url"   : user.get('external_url') or user.get('website') or '',
            "is_verified"    : user.get('is_verified') or False,
            "profile_pic_url": user.get('profile_pic_url') or user.get('hd_profile_pic_url_info', {}).get('url') or '',
            "_user_id"       : user_id
        }

    except Exception as e:
        print("New API fetch error:", e)
        return None


# ════════════════════════════════════════════════════════════
# ROUTE: Proxy image (bypasses CORS for Instagram CDN)
# ════════════════════════════════════════════════════════════
@app.route('/proxy-image', methods=['GET'])
def proxy_image():
    img_url = request.args.get('url', '')
    if not img_url:
        return '', 404
    try:
        resp = req.get(img_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }, timeout=5)
        return Response(
            resp.content,
            content_type=resp.headers.get('Content-Type', 'image/jpeg')
        )
    except Exception as e:
        print("Image proxy error:", e)
        return '', 404


# ════════════════════════════════════════════════════════════
# ROUTE: Fetch Instagram profile
# ════════════════════════════════════════════════════════════
@app.route('/fetch-profile', methods=['POST'])
def fetch_profile():
    data     = request.get_json()
    username = data.get('username', '').strip()

    username = username.replace('https://', '').replace('http://', '')
    username = username.replace('www.instagram.com/', '').replace('instagram.com/', '')
    username = username.strip('/').strip('@')
    username = username.split('?')[0].strip('/')

    headers = {
        "x-rapidapi-key" : RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }

    try:
        if USE_NEW_API:
            profile = fetch_profile_new_api(username, headers)
            if not profile:
                return jsonify({"error": "Could not fetch profile. Try again."}), 500
        else:
            # OLD API flow (unchanged — works when limit resets)
            r1      = req.get(
                f"https://{RAPIDAPI_HOST}/api/v1/user-id",
                headers=headers,
                params={"username": username}
            )
            r1_data = r1.json()
            user_id = r1_data.get('data', {}).get('user', {}).get('id', '')

            if not user_id:
                return jsonify({"error": "Could not find user ID"}), 404

            r2      = req.get(
                f"https://{RAPIDAPI_HOST}/api/v1/info",
                headers=headers,
                params={"id_or_username": user_id}
            )
            r2_data = r2.json()
            profile = r2_data.get('data', {}).get('user', {})

        if not profile:
            return jsonify({"error": "Could not fetch profile data"}), 404

        # Extract fields — works for both old and new API
        followers        = int(profile.get('follower_count') or profile.get('followers') or 0)
        following        = int(profile.get('following_count') or profile.get('following') or 0)
        posts            = int(profile.get('media_count') or profile.get('posts_count') or 0)
        bio              = str(profile.get('biography') or profile.get('bio') or '')
        full_name        = str(profile.get('full_name') or profile.get('fullName') or '')
        uname            = str(profile.get('username') or username)
        is_private       = bool(profile.get('is_private') or False)
        external_url_str = str(profile.get('external_url') or profile.get('website') or '')
        has_url          = 1 if external_url_str.strip() else 0
        img_url          = str(
            profile.get('profile_pic_url') or
            profile.get('hd_profile_pic_url_info', {}).get('url') or ''
        )
        is_verified      = bool(profile.get('is_verified') or False)

        # Use proxy route for image — bypasses Instagram CDN CORS
        BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')
        pic_url = f"{BASE_URL}/proxy-image?url={urllib.parse.quote(img_url, safe='')}" if img_url else ''
        has_pic = 0 if (not img_url or 'silhouette' in img_url) else 1

        nums_in_username = sum(c.isdigit() for c in uname) / max(len(uname), 1)
        fullname_words   = len(full_name.split())
        nums_in_fullname = sum(c.isdigit() for c in full_name) / max(len(full_name), 1)
        name_eq_username = 1 if full_name.lower().replace(' ', '') == uname.lower() else 0
        desc_length      = len(bio)

        # Scam scanning
        bio_scan = analyze_text_for_scams(bio)

        # Fetch post captions
        if USE_NEW_API:
            stored_user_id = profile.get('_user_id', '')
            captions = fetch_recent_captions_new_api(stored_user_id, headers) if stored_user_id else []
        else:
            captions = fetch_recent_captions_old_api(uname, headers)

        posts_scan = analyze_posts_for_scams(captions)

        # LLM semantic analysis
        # Skip LLM if nothing to analyze (private account, no bio, no captions)
        if (bio and len(bio) > 10) or len(captions) > 0:
            llm_result = analyze_with_llm(bio, captions, uname)
        else:
            llm_result = None
            print("Skipping LLM — insufficient content to analyze")
        print(f"LLM result: {llm_result}")

        # Website scan
        website_scan = {}
        if external_url_str.strip():
            print(f"Scanning website: {external_url_str}")
            website_scan = analyze_website(external_url_str)
            print(f"Website signals: {website_scan.get('risk_signals', [])}")

        # Extra behavioral boosts
        extra_boost = 0
        if has_url == 0 and ('dm' in bio.lower() or 'whatsapp' in bio.lower()):
            extra_boost += 20
        if bio_scan.get('score_boost', 0) > 20 and has_url == 0:
            extra_boost += 15
        if followers < 100 and posts > 5 and ('mobile' in bio.lower() or 'phone' in bio.lower()):
            extra_boost += 15

        # Combined scan
        all_kw   = list(set(bio_scan.get('keywords', []) + posts_scan.get('keywords', [])))
        all_cats = list(set(bio_scan.get('categories', []) + posts_scan.get('categories', [])))
        combined_boost = min(65, bio_scan.get('score_boost', 0) + posts_scan.get('score_boost', 0) + extra_boost)

        preview_scan = {
            'found'         : len(all_kw) > 0,
            'keywords'      : all_kw,
            'categories'    : all_cats,
            'bio_keywords'  : bio_scan.get('keywords', []),
            'post_keywords' : posts_scan.get('keywords', []),
            'posts_analyzed': posts_scan.get('posts_analyzed', 0),
            'score_boost'   : combined_boost
        }

        return jsonify({
            "username"             : uname,
            "profile_pic"          : has_pic,
            "nums_length_username" : round(nums_in_username, 4),
            "fullname_words"       : fullname_words,
            "nums_length_fullname" : round(nums_in_fullname, 4),
            "name_equals_username" : name_eq_username,
            "description_length"   : desc_length,
            "external_url"         : has_url,
            "private"              : 1 if is_private else 0,
            "posts"                : posts,
            "followers"            : followers,
            "following"            : following,
            "bio_scan"             : preview_scan,
            "posts_scan_raw"       : posts_scan,
            "website_scan"         : website_scan,
            "llm_result"           : llm_result,   
            "display": {
                "full_name"      : full_name,
                "bio"            : bio,
                "profile_pic_url": pic_url,
                "is_verified"    : is_verified,
                "external_url"   : external_url_str
            }
        })

    except Exception as e:
        print("fetch_profile error:", e)
        return jsonify({"error": str(e)}), 500


# ════════════════════════════════════════════════════════════
# ROUTE: Analyze Instagram profile
# ════════════════════════════════════════════════════════════
@app.route('/analyze-profile', methods=['POST'])
def analyze_profile():
    data = request.get_json()

    features = [
        int(data.get('profile_pic', 0)),
        float(data.get('nums_length_username', 0)),
        float(data.get('fullname_words', 0)),
        float(data.get('nums_length_fullname', 0)),
        int(data.get('name_equals_username', 0)),
        float(data.get('description_length', 0)),
        int(data.get('external_url', 0)),
        int(data.get('private', 0)),
        float(data.get('posts', 0)),
        float(data.get('followers', 0)),
        float(data.get('following', 0)),
        float(data.get('followers', 0)) / (float(data.get('following', 0)) + 1)
    ]

    feature_names = [
        'profile pic', 'nums/length username', 'fullname words',
        'nums/length fullname', 'name==username', 'description length',
        'external URL', 'private', '#posts', '#followers', '#follows',
        'follower_following_ratio'
    ]

    features_df     = pd.DataFrame([features], columns=feature_names)
    features_scaled = scaler.transform(features_df)
    prediction      = model.predict(features_scaled)[0]
    probability     = model.predict_proba(features_scaled)[0]

    ml_result = 'Fake' if prediction == 1 else 'Genuine'
    ml_risk   = round(float(probability[1]) * 100, 2)

    bio_scan     = data.get('bio_scan', {})      or {}
    posts_scan   = data.get('posts_scan_raw', {}) or {}
    website_scan = data.get('website_scan', {})  or {}
    llm_result   = data.get('llm_result')

    final_result, final_risk, risk_level, risk_label, combined_scan = apply_scam_boost(
        ml_risk, ml_result, bio_scan, posts_scan, website_scan
    )

    # Apply LLM boost on top
    if llm_result:
        llm_boost = llm_result.get('llm_boost', 0)
        if llm_boost > 0:
            final_risk = min(100, final_risk + llm_boost)
            if llm_result.get('verdict') == 'SCAM':
                final_risk   = max(final_risk, 65)
                final_result = 'Fake'
            elif llm_result.get('verdict') == 'SUSPICIOUS':
                # Only mark Fake if score crosses 50% threshold
                if final_risk > 50:
                    final_result = 'Fake'
                # else keep original ML result
            print(f"LLM boost: +{llm_boost}% → final={final_risk}%")

    data_hash = generate_hash(data)

    record = {
        'platform'      : 'instagram',
        'username'      : data.get('username', 'unknown'),
        'result'        : final_result,
        'risk_score'    : final_risk,
        'risk_level'    : risk_level,
        'ml_score'      : ml_risk,
        'features'      : data,
        'hash'          : data_hash,
        'bio_scan'      : combined_scan,
        'posts_analyzed': combined_scan.get('posts_analyzed', 0),
        'timestamp'     : datetime.datetime.utcnow().isoformat()
    }
    collection.insert_one(record)

    tx_hash = store_on_blockchain(data.get('username', 'unknown'), final_result, data_hash)
    if tx_hash:
        collection.update_one({'hash': data_hash}, {'$set': {'tx_hash': tx_hash}})

    return jsonify({
        'result'         : final_result,
        'risk_score'     : final_risk,
        'risk_level'     : risk_level,
        'risk_label'     : risk_label,
        'ml_score'       : ml_risk,
        'hash'           : data_hash,
        'tx_hash'        : tx_hash,
        'scam_detected'  : combined_scan.get('found', False),
        'scam_keywords'  : combined_scan.get('keywords', []),
        'scam_categories': combined_scan.get('categories', []),
        'bio_keywords'   : combined_scan.get('bio_keywords', []),
        'post_keywords'  : combined_scan.get('post_keywords', []),
        'posts_analyzed' : combined_scan.get('posts_analyzed', 0),
        'web_signals'    : combined_scan.get('web_signals', []),
        'website_url'    : combined_scan.get('website_url', ''),
        'website_ssl'    : combined_scan.get('website_ssl'),'llm_verdict'    : llm_result.get('verdict') if llm_result else None,
        'llm_reason'     : llm_result.get('reason') if llm_result else None,
        'llm_confidence' : llm_result.get('confidence') if llm_result else None,
    })


# ════════════════════════════════════════════════════════════
# ROUTE: Scan text standalone
# ════════════════════════════════════════════════════════════
@app.route('/scan-text', methods=['POST'])
def scan_text():
    data   = request.get_json()
    result = analyze_text_for_scams(data.get('text', ''))
    return jsonify(result)


# ════════════════════════════════════════════════════════════
# ROUTE: Fetch LinkedIn
# ════════════════════════════════════════════════════════════
@app.route('/fetch-linkedin', methods=['POST'])
def fetch_linkedin():
    data     = request.get_json()
    username = data.get('username', '').strip()
    username = username.replace('https://', '').replace('http://', '')
    username = username.replace('www.linkedin.com/in/', '').replace('linkedin.com/in/', '')
    username = username.strip('/').split('?')[0]
    return jsonify({"username": username, "manual_required": True, "message": "LinkedIn requires manual input"})

@app.route('/get-stored-profile', methods=['POST'])
def get_stored_profile():
    """Return stored profile data from MongoDB without calling Instagram API"""
    data     = request.get_json()
    username = data.get('username', '').strip()

    existing = collection.find_one(
        {'username': username, 'platform': 'instagram'},
        {'_id': 0},
        sort=[('timestamp', -1)]
    )

    if not existing:
        return jsonify({'found': False})

    # Return the stored features so frontend can re-analyze without API call
    features = existing.get('features', {})
    return jsonify({
        'found'       : True,
        'username'    : username,
        'profile_data': features,
        'last_analyzed': existing.get('timestamp'),
        'old_result'  : existing.get('result'),
        'old_risk'    : existing.get('risk_score')
    })
# ════════════════════════════════════════════════════════════
# ROUTE: Analyze LinkedIn
# ════════════════════════════════════════════════════════════
@app.route('/analyze-linkedin', methods=['POST'])
def analyze_linkedin():
    data = request.get_json()

    features = [
        float(data.get('connections', 0)),
        float(data.get('followers', 0)),
        float(data.get('experience_count', 0)),
        float(data.get('education_count', 0)),
        float(data.get('skills_count', 0)),
        float(data.get('recommendations', 0)),
        float(data.get('projects', 0)),
        float(data.get('publications', 0)),
        float(data.get('courses', 0)),
        float(data.get('honors', 0)),
        float(data.get('languages', 0)),
        float(data.get('organizations', 0)),
        float(data.get('interests', 0)),
        float(data.get('activities', 0)),
        float(data.get('profile_strength', 0)),
        float(data.get('engagement', 0))
    ]

    feature_names = [
        'Connections', 'Followers', 'Number of Experiences',
        'Number of Educations', 'Number of Skills', 'Number of Recommendations',
        'Number of Projects', 'Number of Publications', 'Number of Courses',
        'Number of Honors', 'Number of Languages', 'Number of Organizations',
        'Number of Interests', 'Number of Activities',
        'profile_strength', 'engagement'
    ]

    features_df = pd.DataFrame([features], columns=feature_names)
    prediction  = linkedin_model.predict(features_df)[0]
    probability = linkedin_model.predict_proba(features_df)[0]

    ml_result = 'Fake' if prediction == 1 else 'Genuine'
    ml_risk   = round(float(probability[1]) * 100, 2)

    bio_text   = data.get('bio_text', '')
    bio_scan   = analyze_text_for_scams(bio_text) if bio_text else {
        'found': False, 'keywords': [], 'categories': [], 'score_boost': 0
    }
    empty_scan = {'found': False, 'keywords': [], 'categories': [], 'score_boost': 0, 'posts_analyzed': 0}

    final_result, final_risk, risk_level, risk_label, combined_scan = apply_scam_boost(
        ml_risk, ml_result, bio_scan, empty_scan, {}
    )

    data_hash = generate_hash(data)

    record = {
        'platform'  : 'linkedin',
        'username'  : data.get('username', 'unknown'),
        'result'    : final_result,
        'risk_score': final_risk,
        'risk_level': risk_level,
        'ml_score'  : ml_risk,
        'features'  : data,
        'hash'      : data_hash,
        'bio_scan'  : combined_scan,
        'timestamp' : datetime.datetime.utcnow().isoformat()
    }
    collection.insert_one(record)

    tx_hash = store_on_blockchain(data.get('username', 'unknown'), final_result, data_hash)
    if tx_hash:
        collection.update_one({'hash': data_hash}, {'$set': {'tx_hash': tx_hash}})
        print(f"LinkedIn blockchain stored. TX: {tx_hash}")

    return jsonify({
        'result'         : final_result,
        'risk_score'     : final_risk,
        'risk_level'     : risk_level,
        'risk_label'     : risk_label,
        'ml_score'       : ml_risk,
        'hash'           : data_hash,
        'tx_hash'        : tx_hash,
        'scam_detected'  : combined_scan.get('found', False),
        'scam_keywords'  : combined_scan.get('keywords', []),
        'scam_categories': combined_scan.get('categories', []),
        'web_signals'    : [],
        'website_url'    : '',
        'website_ssl'    : None
    })


# ════════════════════════════════════════════════════════════
# ROUTE: Get all results
# ════════════════════════════════════════════════════════════
@app.route('/get-results', methods=['GET'])
def get_results():
    results = list(collection.find({}, {'_id': 0}).sort('timestamp', -1).limit(50))
    return jsonify(results)


# ════════════════════════════════════════════════════════════
# ROUTE: Check existing
# ════════════════════════════════════════════════════════════
@app.route('/check-existing', methods=['POST'])
def check_existing():
    data     = request.get_json()
    username = data.get('username', '').strip()

    existing = collection.find_one({'username': username}, {'_id': 0}, sort=[('timestamp', -1)])

    if existing:
        analyzed_at = datetime.datetime.fromisoformat(existing['timestamp'])
        hours_old   = (datetime.datetime.utcnow() - analyzed_at).total_seconds() / 3600
        return jsonify({
            'exists'    : True,
            'username'  : username,
            'result'    : existing.get('result'),
            'risk_score': existing.get('risk_score'),
            'hash'      : existing.get('hash'),
            'timestamp' : existing.get('timestamp'),
            'hours_old' : round(hours_old, 1),
            'tx_hash'   : existing.get('tx_hash')
        })

    return jsonify({'exists': False})


# ════════════════════════════════════════════════════════════
# ROUTE: Verify against blockchain
# ════════════════════════════════════════════════════════════
@app.route('/verify-result', methods=['POST'])
def verify_result():
    data     = request.get_json()
    username = data.get('username')

    record = collection.find_one({'username': username}, {'_id': 0}, sort=[('timestamp', -1)])

    if not record:
        return jsonify({'verified': False, 'reason': 'No record found in database'}), 404

    recalculated_hash = generate_hash(record['features'])
    stored_db_hash    = record.get('hash')
    db_match          = recalculated_hash == stored_db_hash

    tx_hash          = record.get('tx_hash')
    blockchain_match = None
    blockchain_hash  = None

    if tx_hash:
        receipt = None
        for attempt in range(3):
            try:
                receipt = w3.eth.get_transaction_receipt(tx_hash)
                break
            except Exception as retry_err:
                print(f"Blockchain verify attempt {attempt+1} failed: {retry_err}")
                if attempt < 2:
                    import time
                    time.sleep(2)

        if receipt and receipt['status'] == 1:
            blockchain_match = True
            blockchain_hash  = stored_db_hash
        elif receipt:
            blockchain_match = False

    if db_match and blockchain_match:
        status, message = 'NOT_TAMPERED', 'Data is authentic and verified on blockchain'
    elif not db_match:
        status, message = 'TAMPERED', 'Database record was modified after storage'
    elif blockchain_match is False:
        status, message = 'TAMPERED', 'Blockchain transaction not found or failed'
    else:
        status, message = 'PARTIAL', 'DB hash matches but blockchain unconfirmed'

    return jsonify({
        'username'         : username,
        'verified'         : status == 'NOT_TAMPERED',
        'status'           : status,
        'message'          : message,
        'result'           : record.get('result'),
        'risk_score'       : record.get('risk_score'),
        'timestamp'        : record.get('timestamp'),
        'recalculated_hash': recalculated_hash,
        'stored_db_hash'   : stored_db_hash,
        'blockchain_hash'  : blockchain_hash,
        'tx_hash'          : tx_hash,
        'hashes_match'     : db_match and bool(blockchain_match)
    })


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))

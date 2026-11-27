import json
import os
import random
import time
import uuid
from datetime import datetime, timezone

CATEGORIES = ["elektronik", "fashion", "gadget", "rumah_tangga", "kecantikan"]
PAYMENTS = ["e_wallet", "virtual_account", "kartu_kredit", "cod"]
CITIES = ["Jakarta", "Bandung", "Surabaya", "Yogyakarta", "Medan", "Makassar", "Depok", "Semarang"]
DEVICES = ["android_app", "ios_app", "web_chrome", "web_safari"]
REFERRERS = ["direct", "search", "instagram_ads", "flash_sale_banner", "tiktok_shop"]

NORMAL_REVIEWS = [
    "barang original, pengiriman cepet dan packing rapi",
    "kualitas sesuai harga, penjual ramah dan responsif",
    "produk berfungsi dgan baik, puas belanja di toko ini",
    "bahan nyaman dipakai, ukuran pas sesuai deskripsi",
    "sampai tepat waktu, kondisi mulus tanpa cacat",
]


def make_event(event_type, user_id, merchant_id, category, amount_idr=0, quantity=1, review_text="", rating=0):
    # gabungin 3 jenis data (terstruktur, JSON clickstream, teks ulasan) dlam satu pesan JSON
    now_iso = datetime.now(timezone.utc).isoformat()
    return {
        "event_id": str(uuid.uuid4())[:12],
        "event_time": now_iso,
        "event_type": event_type,
        "user_id": user_id,
        "merchant_id": merchant_id,
        "category": category,
        "amount_idr": int(amount_idr),
        "quantity": int(quantity),
        "payment_method": random.choice(PAYMENTS) if event_type == "checkout" else "none",
        "clickstream": {
            "session_id": f"sess_{random.randint(10000, 99999)}",
            "device": random.choice(DEVICES),
            "city": random.choice(CITIES),
            "ip_address": f"103.{random.randint(10, 220)}.{random.randint(1, 250)}.{random.randint(2, 254)}",
            "referrer": random.choice(REFERRERS),
        },
        "review_text": review_text,
        "rating": int(rating),
    }

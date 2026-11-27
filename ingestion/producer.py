from kafka import KafkaProducer
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


def build_normal_event():
    category = random.choice(CATEGORIES)
    user_id = f"usr_{random.randint(1001, 1400)}"
    merchant_id = f"mrc_{random.randint(101, 130)}"

    # kategori elektronik sama gadget dibikin banyak klik tp checkout rendah biar sinyal voucher kebaca nyata
    if category in ("elektronik", "gadget"):
        event_type = random.choices(["view", "add_to_cart", "checkout", "review"], weights=[72, 18, 5, 5])[0]
    else:
        event_type = random.choices(["view", "add_to_cart", "checkout", "review"], weights=[45, 22, 23, 10])[0]

    if event_type == "checkout":
        base_price = random.randint(85_000, 2_800_000)
        qty = random.randint(1, 3)
        return make_event("checkout", user_id, merchant_id, category, amount_idr=base_price * qty, quantity=qty)
    if event_type == "review":
        return make_event("review", user_id, merchant_id, category, review_text=random.choice(NORMAL_REVIEWS), rating=random.choice([4, 5]))
    return make_event(event_type, user_id, merchant_id, category)


def connect_producer(bootstrap_servers):
    # tunggu kafka siap biar ga langsung crash pas container baru start
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                linger_ms=50,
                retries=5,
            )
            print(f"[producer] tersambung ke kafka di {bootstrap_servers}")
            return producer
        except Exception as err:
            print(f"[producer] menunggu kafka siap ({err}), coba lagi 3 detik")
            time.sleep(3)

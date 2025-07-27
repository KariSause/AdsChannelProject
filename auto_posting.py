import asyncio
import sqlite3
from aiogram import Bot, types
from datetime import datetime, timedelta

# --- Config ---
DB_PATH = 'reklama.db'


# --- Auto-posting variants ---
POSTING_VARIANTS = {
    # Some types of subscriptions and tariffs
    'sub_berlin_99': {'count': 10, 'days': 30},
    'sub_berlin_150': {'count': 30, 'days': 30},
    'sub_berlin_199': {'count': 30, 'days': 30, 'pin': True},
    'tariff_berlin_25': {'count': 1, 'days': 1},
    'tariff_berlin_50': {'count': 1, 'days': 1, 'pin': True},
    'tariff_berlin_80': {'count': 7, 'days': 7, 'pin': True},

    'sub_eur_70': {'count': 10, 'days': 30},
    'sub_eur_100': {'count': 30, 'days': 30},
    'sub_eur_150': {'count': 30, 'days': 30, 'pin': True},
    'tariff_eur_15': {'count': 1, 'days': 1},
    'tariff_eur_30': {'count': 1, 'days': 1, 'pin': True},
    'tariff_eur_50': {'count': 7, 'days': 7},

    'sub_usd_100': {'count': 10, 'days': 20},
    'sub_usd_150': {'count': 30, 'days': 30},
    'tariff_usd_30': {'count': 1, 'days': 1},
    'tariff_usd_60': {'count': 1, 'days': 1, 'pin': True},
    'tariff_usd_99': {'count': 7, 'days': 7},
}


def init_auto_posts_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS auto_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ad_id INTEGER,
        next_post_at TEXT,
        remaining_posts INTEGER,
        interval_days INTEGER,
        status TEXT
    )''')
    conn.commit()
    conn.close()


def get_auto_ads():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, group_id, text, photos, tariff, created_at FROM ads WHERE tariff IN ({}) AND status='paid'".format(
        ','.join(f"'{k}'" for k in POSTING_VARIANTS.keys())
    ))
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_due_auto_posts():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("SELECT id, ad_id, next_post_at, remaining_posts, interval_days FROM auto_posts WHERE status='active' AND next_post_at<=?", (now,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def create_auto_post(ad_id, variant):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    interval = max(1, variant['days'] // variant['count'])
    next_post_at = datetime.now().isoformat()
    cursor.execute("INSERT INTO auto_posts (ad_id, next_post_at, remaining_posts, interval_days, status) VALUES (?, ?, ?, ?, ?)",
                   (ad_id, next_post_at, variant['count'], interval, 'active'))
    conn.commit()
    conn.close()


def update_auto_post(auto_post_id, remaining_posts, next_post_at, status):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE auto_posts SET remaining_posts=?, next_post_at=?, status=? WHERE id=?",
                   (remaining_posts, next_post_at, status, auto_post_id))
    conn.commit()
    conn.close()


async def auto_posting(bot):
    init_auto_posts_table()
    while True:
        ads = get_auto_ads()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        for ad in ads:
            ad_id, user_id, group_id, text, photos, tariff, created_at = ad
            variant = POSTING_VARIANTS.get(tariff)
            if not variant:
                continue
            cursor.execute("SELECT id FROM auto_posts WHERE ad_id=?", (ad_id,))
            if not cursor.fetchone():
                create_auto_post(ad_id, variant)
        conn.close()
        due_posts = get_due_auto_posts()
        for auto_post in due_posts:
            auto_post_id, ad_id, next_post_at, remaining_posts, interval_days = auto_post
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, group_id, text, photos, tariff FROM ads WHERE id=?", (ad_id,))
            ad_row = cursor.fetchone()
            conn.close()
            if not ad_row:
                continue
            user_id, group_id, text, photos, tariff = ad_row
            variant = POSTING_VARIANTS.get(tariff)
            group_link = get_group_link(group_id)
            chat_id = extract_chat_id(group_link)
            msg = None
            if photos:
                photo_ids = photos.split(',')
                media = [types.InputMediaPhoto(media=photo_ids[0], caption=text)]
                for pid in photo_ids[1:]:
                    media.append(types.InputMediaPhoto(media=pid))
                if len(media) == 1:
                    msg = await bot.send_photo(chat_id, media[0].media, caption=media[0].caption)
                else:
                    msgs = await bot.send_media_group(chat_id, media)
                    msg = msgs[0] if msgs else None
            else:
                msg = await bot.send_message(chat_id, text or ' ')
            if variant.get('pin') and msg:
                try:
                    await bot.pin_chat_message(chat_id, msg.message_id, disable_notification=True)
                except Exception as e:
                    print(f"Pinning error: {e}")
            remaining_posts -= 1
            if remaining_posts > 0:
                next_post = (datetime.now() + timedelta(days=interval_days)).isoformat()
                update_auto_post(auto_post_id, remaining_posts, next_post, 'active')
            else:
                update_auto_post(auto_post_id, 0, '', 'done')
            print(f"Post {ad_id} posted! Remaining: {remaining_posts}")
        await asyncio.sleep(86400)  


def get_group_link(group_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT link FROM groups WHERE id=?', (group_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def extract_chat_id(link):
    if not link:
        return link
    if link.startswith('https://t.me/'):
        return '@' + link.split('/')[-1]
    elif link.startswith('t.me/'):
        return '@' + link.split('/')[-1]
    return link

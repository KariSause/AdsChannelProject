import sqlite3
from sqlite3 import Error


conn = sqlite3.connect('reklama.db')
cursor = conn.cursor()

# --- Инициализация БД и создание таблиц ---
async def init_db():
    # Таблица групп/каналов
    cursor.execute('''CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        link TEXT UNIQUE NOT NULL
    )''')
    # Таблица заявок на рекламу
    cursor.execute('''CREATE TABLE IF NOT EXISTS ads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        group_id INTEGER NOT NULL,
        text TEXT,
        photos TEXT, -- Сохраняем id файлов через запятую
        status TEXT DEFAULT 'pending', -- pending/paid/posted
        tariff TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(group_id) REFERENCES groups(id)
    )''')
    # Таблица для хранения инструкции и реквизитов
    cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    # Таблица для хранения запрещённых слов
    cursor.execute('''CREATE TABLE IF NOT EXISTS forbidden_words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT 
    )''')
    # Если нет дефолтных значений, добавить
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('instruction', 'Введите инструкцию...')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('requisites', 'Введите реквизиты...')")

    conn.commit()


# --- Работа с группами ---
async def add_group(name, link):
    try:
        cursor.execute('INSERT OR IGNORE INTO groups (name, link) VALUES (?, ?)', (name, link))
        conn.commit()
    except Error as e:
        print(f"Error adding group: {e}")

async def get_groups():
    cursor.execute('SELECT id, name, link FROM groups')
    groups = cursor.fetchall()
    return groups

async def delete_group(group_id):
    cursor.execute('DELETE FROM groups WHERE id=?', (group_id,))
    conn.commit()

# --- Работа с заявками ---
async def add_ad(user_id, group_id, text, photos, tariff):
    cursor.execute('INSERT INTO ads (user_id, group_id, text, photos, tariff) VALUES (?, ?, ?, ?, ?)', (user_id, group_id, text, photos, tariff))
    conn.commit()

# --- Работа с настройками (инструкция, реквизиты) ---
async def get_setting(key):
    cursor.execute('SELECT value FROM settings WHERE key=?', (key,))
    row = cursor.fetchone()
    return row[0] if row else None

async def set_setting(key, value):
    cursor.execute('REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
    conn.commit()

# --- Работа с запрещёнными словами ---
async def get_forbidden_words():
    cursor.execute('SELECT word FROM forbidden_words')
    return [row[0] for row in cursor.fetchall()]

async def add_forbidden_word(word):
    cursor.execute('INSERT OR IGNORE INTO forbidden_words (word) VALUES (?)', (word.lower(),))
    conn.commit()

async def delete_forbidden_word(id_word ):
    cursor.execute('DELETE FROM forbidden_words WHERE id=?', (id_word,))
    conn.commit()


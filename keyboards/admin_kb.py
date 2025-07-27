from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from data_base.db import get_groups, get_forbidden_words



starterAdminKeyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='🚫 Forbidden Words')],
        [KeyboardButton(text='💸 Payment Details')],
        [KeyboardButton(text='🔺 Add/Remove Group')]
    ],
    resize_keyboard=True
)

ADMIN_GROUPS_PER_PAGE = 30
ADMIN_MAX_BUTTONS_PER_ROW = 1

async def get_admin_forbidword_keyboard(page=0):
    words = await get_forbidden_words()
    total = len(words)
    start = page * ADMIN_GROUPS_PER_PAGE
    end = start + ADMIN_GROUPS_PER_PAGE
    page_words = words[start:end]
    rows = []
    row = []
    for idx, word_tuple in enumerate(page_words, 1):
        row.append(InlineKeyboardButton(text=f"❌{word_tuple}", callback_data=f'admin_wordforbide_{idx}'))
        if len(row) == ADMIN_MAX_BUTTONS_PER_ROW:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    nav_row = []
    if start > 0:
        nav_row.append(InlineKeyboardButton(text='⬅️', callback_data=f'admin_words_page_{page-1}'))
    if end < total:
        nav_row.append(InlineKeyboardButton(text='➡️', callback_data=f'admin_words_page_{page+1}'))
    if nav_row:
        rows.append(nav_row)
    rows.append([InlineKeyboardButton(text='➕ Add Word', callback_data='admin_add_word')])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb

async def get_admin_groups_keyboard(page=0):
    groups = await get_groups()
    total = len(groups)
    start = page * ADMIN_GROUPS_PER_PAGE
    end = start + ADMIN_GROUPS_PER_PAGE
    page_groups = groups[start:end]
    rows = []
    row = []
    for idx, (group_id, name, link) in enumerate(page_groups, 1):
        row.append(InlineKeyboardButton(text=f"❌{name}", callback_data=f'admin_group_{group_id}'))
        if len(row) == ADMIN_MAX_BUTTONS_PER_ROW:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    nav_row = []
    if start > 0:
        nav_row.append(InlineKeyboardButton(text='⬅️', callback_data=f'admin_groups_page_{page-1}'))
    if end < total:
        nav_row.append(InlineKeyboardButton(text='➡️', callback_data=f'admin_groups_page_{page+1}'))
    if nav_row:
        rows.append(nav_row)
    rows.append([InlineKeyboardButton(text='➕ Add Group', callback_data='admin_add_group')])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb

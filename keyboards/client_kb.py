from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from data_base.db import get_groups

GROUPS_PER_PAGE = 5
MAX_BUTTONS_PER_ROW = 5

starterClientKeyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='📄Order Advertisement')],
        [KeyboardButton(text='💸 Price')],
        [KeyboardButton(text='🧑‍💻 Support Service')]
    ],
    resize_keyboard=True
)

def get_menu_keyboard():
    menuKeyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='📌 Place Advertisement', callback_data='news_tariff')],
        ]
    )
    return menuKeyboard

async def get_groups_keyboard(page=0):
    groups = await get_groups()
    total = len(groups)
    start = page * GROUPS_PER_PAGE
    end = start + GROUPS_PER_PAGE
    page_groups = groups[start:end]
    rows = []
    for group_id, name, link in page_groups:
        rows.append([InlineKeyboardButton(text=name, callback_data=f'group_{group_id}')])
    nav_row = []
    if start > 0:
        nav_row.append(InlineKeyboardButton(text='⬅️', callback_data=f'groups_page_{page-1}'))
    if end < total:
        nav_row.append(InlineKeyboardButton(text='➡️', callback_data=f'groups_page_{page+1}'))
    if nav_row:
        rows.append(nav_row)
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import types, Router
from keyboards.client_kb import get_groups_keyboard, starterClientKeyboard
from keyboards.admin_kb import starterAdminKeyboard, get_admin_forbidword_keyboard
from data_base.db import add_ad, get_groups, add_group, delete_group, get_setting, set_setting, get_forbidden_words, add_forbidden_word, delete_forbidden_word
from aiogram import F
import sqlite3
from aiogram.enums.chat_type import ChatType


router = Router()

class AdStates(StatesGroup):
    waiting_for_group = State()
    waiting_for_post = State()
    waiting_for_type = State()
    waiting_for_value = State()
    waiting_for_tariff = State()
    waiting_for_payment = State()
    waiting_for_confirm = State()

class AddChannelStates(StatesGroup):
    waiting_for_link = State()
    waiting_for_name = State()
    

class BroadcastStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_photo = State()

class SettingsStates(StatesGroup):
    waiting_for_instruction = State()
    waiting_for_requisites = State()
    
class ForbiddenWordsStates(StatesGroup):
    waiting_for_word = State()


ADMINS = [7962357637]

@router.message(lambda message: message.text == '⬅️ Back')
async def handle_back_button(message: types.Message, state: FSMContext):
    await state.clear()
    if message.from_user.id in ADMINS: 
        await message.answer("Cancelled. Returning to menu.", reply_markup=starterAdminKeyboard)
    else:
        await message.answer(
            "Cancelled. Returning to menu.",
            reply_markup=starterClientKeyboard
        )

async def contains_forbidden(text):
    forbidden_words = await get_forbidden_words()
    for word in forbidden_words:
        if word.lower() in text.lower():
            return word
    return None

@router.message(lambda m: m.text and m.text.startswith('/start'))
async def start_command(message: types.Message, state: FSMContext):
    await state.clear()
    try:
        chat_id = '@typicalberlin'
        text = (
            "📢 Want to place an ad? It's easier than ever!\n\n"
            "Now you can order ads directly through the bot — no chats, fast and convenient.\n\n"
            "👆 Click here 👉 @ourbot\n"
            "and create a post in 1 minute:\n\n"
            "✅ Current prices\n"
            "✅ Payment via Monobank, Wise, PayPal, USDT\n"
            "✅ Automatic post submission for moderation\n\n"
            "⚡ Everything happens in a few clicks — try it now!"
        )
        kb = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="✅Place Ad", url="https://t.me/ourbot")]
            ]
        )
        await message.bot.send_message(chat_id, text, reply_markup=kb)
    except Exception as e:
        print(f"Error sending promotional message to Berlin: {e}")

    if message.chat.type == 'private':
        if message.from_user.id in ADMINS: 
            await message.answer(f"Hello, admin {message.from_user.first_name}! 👋", reply_markup=starterAdminKeyboard)
        else:
            await message.answer(
                "Hello!👋 I am a bot for placing ads in groups.\n"
                "📍 Audience: active Ukrainians across Germany, New York, and Poland\n"
                "📊 Average reach: up to 6000 views per post\n"
                "⚡️ Fast response | Clear report | Discounts for regular customers",
                reply_markup=starterClientKeyboard
            )
    
@router.message(lambda m: m.text == '📄Order Advertisement')
async def show_menu(message: types.Message, state: FSMContext):
    await message.answer('Select a group for advertising:', reply_markup=await get_groups_keyboard(0))
    await state.set_state(AdStates.waiting_for_group)

@router.message(lambda m: m.text == '💸 Price')
async def show_price(message: types.Message):
    await message.answer(
        '''💡 TARIFFS:
✅ $30 – 1 post
✅ $60 – post + pin for 3 days
✅ $99 – week (1 post per day + pin for 3 days)

🎯 SUBSCRIPTIONS:
🔹 $100 – 10 posts within 20 days
🔹 $150 – 30 posts within a month

💡 TARIFF PLACEMENT:
✅ €15 – 1 post
✅ €30 – post + pin for 3 days
✅ €50 – week (1 post per day + pin for 3 days)

🎯 SUBSCRIPTIONS:
🔹 €70 – 10 posts within a month
🔹 €100 – 30 posts within a month
🔹 €150 – 30 posts within a month + pin for the whole month''',
    )
    
@router.message(lambda m: m.text == '🧑‍💻 Support Service')    
async def support(message: types.Message):
    await message.answer(
        'If you have questions or need help, contact support:\n'
        '📩 Admin: @Fr7878\n'
        '⚡️ Fast response | Clear report | Discounts for regular customers',
        reply_markup=starterClientKeyboard
    )
 
@router.message(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def filter_messages(message: types.Message):
    if not message.text:
        return

    bad_word = await contains_forbidden(message.text)
    if bad_word:
        await message.delete()
        print(f"Deleted message: '{message.text}' (contains '{bad_word}')")
    else:
        print(f"Allowed message: {message.text}") 
    
from keyboards.admin_kb import get_admin_groups_keyboard
@router.message(lambda m: m.text == '🔺 Add/Remove Group')
async def admin_show_groups(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await state.clear()  
        await message.answer('Loading groups...')
        await message.answer('Manage Groups:', reply_markup=await get_admin_groups_keyboard(0))

@router.callback_query(lambda c: c.data.startswith('admin_groups_page_'))
async def admin_groups_pagination(callback: types.CallbackQuery):
    page = int(callback.data.split('_')[-1])
    await callback.message.edit_reply_markup(reply_markup=await get_admin_groups_keyboard(page))
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith('admin_group_'))
async def admin_group_selected(callback: types.CallbackQuery, state: FSMContext):
    group_id = int(callback.data.split('_')[2])
    await delete_group(group_id)
    await callback.message.edit_text('Group successfully deleted!')
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=await get_admin_groups_keyboard(0))

@router.callback_query(lambda c: c.data == 'admin_add_group')
async def admin_add_group_btn(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Send the link to the group/channel:')
    await state.set_state(AddChannelStates.waiting_for_link)
    await callback.answer()

@router.message(AddChannelStates.waiting_for_link)
async def admin_save_group_link(message: types.Message, state: FSMContext):
    link = message.text
    print(link)
    print(link.startswith('https://t.me/'), link.startswith('https://t.me/joinchat/'), link.startswith('@'))
    if link.startswith('https://t.me/') or link.startswith('https://t.me/joinchat/') or link.startswith('@'):
        await state.update_data(group_link=link)
        await message.answer('Enter the group name')
        await state.set_state(AddChannelStates.waiting_for_name)       
    else:
        await message.answer('Please send a valid group link!')
        return
        
@router.message(AddChannelStates.waiting_for_name)
async def admin_save_group_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    link = data.get('group_link')
    real_name = message.text.strip()
    print(real_name, link)
    await add_group(real_name, link)
    await message.answer(f'Group "{real_name}" added!')
    await state.clear()
    
    

@router.callback_query(lambda c: c.data == 'news_tariff')
async def show_groups_tariff(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text('Select a group for advertising:', reply_markup=await get_groups_keyboard(0))
    await state.set_state(AdStates.waiting_for_group)
    
@router.callback_query(lambda c: c.data.startswith('groups_page_'), AdStates.waiting_for_group)
async def groups_pagination(callback: types.CallbackQuery, state: FSMContext):
    page = int(callback.data.split('_')[-1])
    await callback.message.edit_text('Select a group for advertising:', reply_markup=await get_groups_keyboard(page))
    await callback.answer()
@router.callback_query(lambda c: c.data.startswith('group_'))
async def group_chosen(callback: types.CallbackQuery, state: FSMContext):
    group_id = int(callback.data.split('_')[1])
    await state.update_data(group_id=group_id)
    await callback.answer()
    await callback.message.edit_text('Send the advertisement:') 
    await state.set_state(AdStates.waiting_for_post)

@router.message(AdStates.waiting_for_post)
async def post_received(message: types.Message, state: FSMContext):
    photo_file_id = None
    text = ""
    data = await state.get_data()
    text = data.get("text")
    photos = data.get("photos", [])

    if message.photo:
        photos.append(message.photo[-1].file_id)
        text = message.caption or ""  
        await state.update_data(photos=photos, text=text)

    elif message.text:
        text = message.text
        await state.update_data(text=text, photo=photo_file_id)
    if not text and not photo_file_id:
        await message.answer("Please send a post with text or photo.")
        return
    forbidden_word = await contains_forbidden(text)
    if forbidden_word:
        await message.answer("Advertisement not allowed", reply_markup=starterClientKeyboard)
        await state.clear()   
        return
    else:
        await message.answer("Post saved. Now select the currency:", 
                            reply_markup=types.ReplyKeyboardMarkup(
                                keyboard=[
                                    [types.KeyboardButton(text="$"), types.KeyboardButton(text="€"), types.KeyboardButton(text="₴")], 
                                    [types.KeyboardButton(text="⬅️ Back")]
                                ],
                                resize_keyboard=True
                            ))
        await state.set_state(AdStates.waiting_for_value)

    

@router.message(AdStates.waiting_for_value)
async def ad_value_entered(message: types.Message, state: FSMContext):
    if message.text not in ['$', '€', '₴']:
        await message.answer('Please select a currency: $, ₴ or €')
        return
    await state.update_data(value=message.text)
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text='💡 Tariffs', callback_data='tariffs')],
            [types.InlineKeyboardButton(text='🎯 Subscriptions', callback_data='subs')]
        ]
    )
    
    await message.answer('Select a plan:', reply_markup=kb)
    await state.set_state(AdStates.waiting_for_type)
    
  

@router.callback_query(lambda c: c.data == 'tariffs', AdStates.waiting_for_type)
async def show_tariffs(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    value = data.get('value', '€')
    group_id = data.get('group_id')
    groups = await get_groups()
    group_link = next((link for gid, name, link in groups if gid == group_id), None)
    # Here is configuration for specific groups
    if group_link in ['t.me/abcd', 'https://t.me/abcd', '@abcd']:
        tariffs = [
            ('25€', '1 post', 'tariff_berlin_25'),
            ('50€', 'post + pin (3 days)', 'tariff_berlin_50'),
            ('80€', 'week of ads (7 posts) + pin', 'tariff_berlin_80'),
        ]
        subs = [
            ('99€', '10 posts / month', 'sub_berlin_99'),
            ('150€', '30 posts / month', 'sub_berlin_150'),
            ('199€', '30 posts + pin for a month', 'sub_berlin_199'),
        ]
    elif group_link in ['https://t.me/1234', 't.me/1234', '@1234']:
        tariffs = [
            ('15€', '1 post', 'tariff_eur_15'),
            ('30€', 'post + pin for 3 days', 'tariff_eur_30'),
            ('50€', 'week (1 post per day + pin for 3 days)', 'tariff_eur_50'),
        ]
        subs = [
            ('70€', '10 posts within a month', 'sub_eur_70'),
            ('100€', '30 posts within a month', 'sub_eur_100'),
            ('150€', '30 posts + pin for the whole month', 'sub_eur_150'),
        ]
    elif group_link in ['https://t.me/lala', 't.me/lala', '@lala']:
        tariffs = [
            ('30$', '1 post', 'tariff_usd_30'),
            ('60$', 'post + pin for 3 days', 'tariff_usd_60'),
            ('99$', 'week (1 post per day + pin for 3 days)', 'tariff_usd_99'),
        ]
        subs = [
            ('100$', '10 posts within 20 days', 'sub_usd_100'),
            ('150$', '30 posts within a month', 'sub_usd_150'),
        ]
    else:
        if value == '$' or value == '₴':
            tariffs = [
                ('30$', '1 post', 'tariff_usd_30'),
                ('60$', 'post + pin for 3 days', 'tariff_usd_60'),
                ('99$', 'week (1 post per day + pin for 3 days)', 'tariff_usd_99'),
            ]
            subs = [
                ('100$', '10 posts within 20 days', 'sub_usd_100'),
                ('150$', '30 posts within a month', 'sub_usd_150'),
            ]
        else:
            tariffs = [
                ('15€', '1 post', 'tariff_eur_15'),
                ('30€', 'post + pin for 3 days', 'tariff_eur_30'),
                ('50€', 'week (1 post per day + pin for 3 days)', 'tariff_eur_50'),
            ]
            subs = [
                ('70€', '10 posts within a month', 'sub_eur_70'),
                ('100€', '30 posts within a month', 'sub_eur_100'),
                ('150€', '30 posts + pin for the whole month', 'sub_eur_150'),
            ]
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=f'{price} – {desc}', callback_data=cb)] for price, desc, cb in tariffs
        ]
    )
    subs_kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=f'{price} – {desc}', callback_data=cb)] for price, desc, cb in subs
        ]
    )
    await callback.message.edit_text('Choose a plan:', reply_markup=kb)
    await state.set_state(AdStates.waiting_for_tariff)
    await callback.answer()
    await state.update_data(subs_kb=subs_kb)
    



@router.callback_query(lambda c: c.data == 'subs', AdStates.waiting_for_type)
async def show_subs(callback: types.CallbackQuery, state: FSMContext):
    value = (await state.get_data()).get('value', '€')
    if value == '$':
        subs = [
            ('100$', '10 постов в течение 20 дней', 'sub_usd_100'),
            ('150$', '30 постов в течение месяца', 'sub_usd_150'),
        ]
    else:
        subs = [
            ('70€', '10 постов в течение месяца', 'sub_eur_70'),
            ('100€', '30 постов в течение месяца', 'sub_eur_100'),
            ('150€', '30 постов + закреп на весь месяц', 'sub_eur_150'),
        ]
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=f'{price} – {desc}', callback_data=cb)] for price, desc, cb in subs
        ]
    )
    await callback.message.edit_text('Выберите абонемент:', reply_markup=kb)
    await state.set_state(AdStates.waiting_for_tariff)
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith('tariff_') or c.data.startswith('sub_'), AdStates.waiting_for_tariff)
async def tariff_or_sub_selected(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    requisites = await get_setting('requisites')
    await state.update_data(selected_tariff=callback.data)
    payment_text = (
        f'💳 СПОСОБЫ ОПЛАТЫ(Оплачивайте в удобной для себя валюте, взяв актуальный курс✅):\n{requisites}\n\nПосле оплаты нажмите кнопку ниже!'
    )
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text='✅ Я оплатил(а)', callback_data='paid')]
        ]
    )
    await callback.message.edit_text(payment_text, reply_markup=kb)
    await state.set_state(AdStates.waiting_for_payment)
    await callback.answer()





@router.callback_query(lambda c: c.data == 'paid', AdStates.waiting_for_payment)
async def user_paid(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Please send a receipt or screenshot of payment')
    await state.set_state(AdStates.waiting_for_confirm)
    
    
@router.message(AdStates.waiting_for_confirm)
async def confirm_payment(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = message.from_user.id
    group_id = data['group_id']
    text, photos = data['text'], data.get('photos')
    selected_tariff = data.get('selected_tariff', '')
    groups = await get_groups()
    group_name = next((name for gid, name, link in groups if gid == group_id), str(group_id))
    group_link = next((link for gid, name, link in groups if gid == group_id), None)
    if not photos:
        photos = []
    elif isinstance(photos, str):
        photos = [photos]
    forbidden_word = await contains_forbidden(text)
    if forbidden_word:
        await message.answer(f'Forbidden word detected in the ad: "{forbidden_word}". Ad not sent.', reply_markup=None)
        await state.clear()
        return
    await add_ad(user_id, group_id, text or '', ','.join(photos), selected_tariff)
    confirm_kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text='✅ Confirm', callback_data=f'confirm_{user_id}_{group_id}')],
            [types.InlineKeyboardButton(text='❌ Reject', callback_data=f'reject_{user_id}_{group_id}')]
        ]
    )
    msg = f'New ad request!\n\nText: {text}\nTariff: {selected_tariff}\nGroup: {group_name}\nUser: {user_id}\nLink: {group_link}'
    for admin_id in ADMINS:
        if message.photo:
            await message.bot.send_photo(admin_id, message.photo[-1].file_id, caption='Receipt/payment screenshot')
        elif message.document:
            await message.bot.send_document(admin_id, message.document.file_id, caption='Receipt/payment screenshot')
        elif message.text:
            await message.bot.send_message(admin_id, f'Link to receipt/payment screenshot: {message.text}')
        if photos:
            if len(photos) == 1:
                await message.bot.send_photo(admin_id, photos[0], caption=msg, reply_markup=confirm_kb)
            else:
                media = [types.InputMediaPhoto(media=pid) for pid in photos]
                media[0].caption = msg
                await message.bot.send_media_group(admin_id, media)
                await message.bot.send_message(admin_id, msg, reply_markup=confirm_kb)
        else:
            await message.bot.send_message(admin_id, msg, reply_markup=confirm_kb)
    await message.answer('Your ad request has been accepted! Please wait for admin review.')
    await state.clear()


@router.callback_query(lambda c: c.data.startswith('reject_'))
async def admin_reject(callback: types.CallbackQuery):
    _, user_id, group_id = callback.data.split('_')
    user_id = int(user_id)
    await callback.bot.send_message(user_id, 'Your ad was rejected by the admin. Reason: violation of rules or forbidden words detected.')
    await callback.message.edit_text('Ad rejected.')
    await callback.answer('Ad rejected!')

def extract_chat_id(link):
    if not link:
        return link
    if link.startswith('https://t.me/'):
        return '@' + link.split('/')[-1]
    elif link.startswith('t.me/'):
        return '@' + link.split('/')[-1]
    return link


@router.callback_query(lambda c: c.data.startswith('confirm_'))
async def admin_confirm(callback: types.CallbackQuery):
    _, user_id, group_id = callback.data.split('_')
    user_id = int(user_id)
    group_id = int(group_id)
    groups = await get_groups()
    group_link = next((link for gid, name, link in groups if gid == group_id), None)
    chat_id = extract_chat_id(group_link)
    group_display = chat_id if chat_id else group_id
    await callback.bot.send_message(user_id, 'Your ad has been confirmed and will be posted in the channel/group!')
    conn = sqlite3.connect('reklama.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT text, photos, tariff FROM ads WHERE user_id=? AND group_id=? ORDER BY id DESC LIMIT 1',
        (user_id, group_id)
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        text, photos, tariff = row if len(row) == 3 else (row[0], row[1], '')
        text = text or ""
        try:
            if photos:
                photo_ids = photos.split(',')
                media = [types.InputMediaPhoto(media=photo_ids[0], caption=text)]
                for pid in photo_ids[1:]:
                    media.append(types.InputMediaPhoto(media=pid))
                if len(media) == 1:
                    msg = await callback.bot.send_photo(chat_id, media[0].media, caption=media[0].caption)
                else:
                    msgs = await callback.bot.send_media_group(chat_id, media)
                    msg = msgs[0] if msgs else None
            else:
                msg = await callback.bot.send_message(chat_id, text or ' ')
            if tariff in ['tariff_eur_30', 'tariff_usd_60'] and msg:
                try:
                    await callback.bot.pin_chat_message(chat_id, msg.message_id, disable_notification=True)
                except Exception as e:
                    print(f"Pin error: {e}")
        except Exception as e:
            print(f"Error sending ad to group {group_display}: {e}")
            await callback.bot.send_message(callback.from_user.id, f"Error sending: {e}")
    else:
        await callback.bot.send_message(chat_id, 'Ad text goes here...')

    await callback.answer('Ad confirmed and published!')
    try:
        await callback.message.edit_text('Ad confirmed and published!')
    except Exception as e:
        await callback.message.answer('Ad confirmed and published!')
        await callback.message.delete()


@router.message(lambda message: message.text == 'ℹ️ Change instruction')
async def admin_edit_instruction(message: types.Message, state: FSMContext):
    current = await get_setting('instruction')
    kb = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text='⬅️ Back')]],
        resize_keyboard=True
    )
    await message.answer(f'Current instruction:\n\n{current}\n\nSend new instruction text or press "⬅️ Back":', reply_markup=kb)
    await state.set_state(SettingsStates.waiting_for_instruction)

@router.message(lambda m: m.text=='ℹ️ Instruction')
async def client_show_instruction(message: types.Message):
    current = await get_setting('instruction')
    await message.answer(f'Current instruction:\n\n{current}', reply_markup=starterClientKeyboard)


@router.message(lambda m: m.text and ('💸 Requisites' in m.text.lower() or '💸' in m.text))
async def admin_edit_requisites(message: types.Message, state: FSMContext):
    current = await get_setting('requisites')
    kb = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text='⬅️ Back')]],
        resize_keyboard=True
    )
    await message.answer(f'Current requisites:\n\n{current}\n\nSend new requisites or press "⬅️ Back":', reply_markup=kb, parse_mode='Markdown')
    await state.set_state(SettingsStates.waiting_for_requisites)


@router.message(SettingsStates.waiting_for_instruction)
async def save_instruction(message: types.Message, state: FSMContext):
    if message.text == '⬅️ Back':
        await state.clear()
        await message.answer("Cancelled. Returning to menu.", reply_markup=starterAdminKeyboard)
        return
    await set_setting('instruction', message.text)
    await state.clear()
    await message.answer("Instruction successfully updated!", reply_markup=starterAdminKeyboard)


@router.message(SettingsStates.waiting_for_requisites)
async def save_requisites(message: types.Message, state: FSMContext):
    if message.text == '⬅️ Back':
        await state.clear()
        await message.answer("Cancelled. Returning to menu.", reply_markup=starterAdminKeyboard)
        return
    await set_setting('requisites', message.text)
    await state.clear()
    await message.answer("Requisites successfully updated!", reply_markup=starterAdminKeyboard)



@router.message(lambda m: m.text== '🚫 Forbidden words')
async def admin_edit_forbidden_words(message: types.Message, state: FSMContext):
    words = await get_forbidden_words()
    print(words)
    await message.answer('List of forbidden words:', reply_markup=await get_admin_forbidword_keyboard(0))
    await state.clear()

@router.callback_query(lambda c: c.data == 'admin_add_word')
async def add_forbidden_word_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Enter a word to add:')
    await state.set_state(ForbiddenWordsStates.waiting_for_word)
    await callback.answer()
    

@router.message(ForbiddenWordsStates.waiting_for_word)
async def add_forbidden_word_handler(message: types.Message, state: FSMContext):
    await add_forbidden_word(message.text)
    await state.clear()
    await message.answer('Word added!')
    await message.answer('List of forbidden words:', reply_markup=await get_admin_forbidword_keyboard(0))


@router.message(lambda m: m.reply_to_message and m.reply_to_message.text == 'Enter a word to add:')
async def save_forbidden_word(message: types.Message, state: FSMContext):
    await add_forbidden_word(message.text)
    await message.answer('Word added!')


@router.callback_query(lambda c: c.data.startswith('admin_wordforbide_'))
async def delete_forbidden_word_menu(callback: types.CallbackQuery):
    group_id = int(callback.data.split('_')[-1])
    print(group_id)
    await delete_forbidden_word(int(group_id))
    await callback.answer()
    await callback.message.answer('List of forbidden words:', reply_markup=await get_admin_forbidword_keyboard(0))
    await callback.message.delete()


@router.callback_query(lambda c: c.data == 'back_forbidden_menu')
async def back_forbidden_menu(callback: types.CallbackQuery):
    await callback.message.edit_text('Forbidden words menu closed.')
    await callback.answer()


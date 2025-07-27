from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import types, Router
from data_base.db import add_group, get_setting, set_setting
from keyboards.admin_kb import get_admin_groups_keyboard, starterAdminKeyboard

router = Router()

class BroadcastStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_photo = State()

GROUPS_PER_PAGE = 5

print('Admin handlers loaded')

@router.message(lambda m: m.text == '🔺 Add/Remove Group')
async def admin_show_groupss(message: types.Message, state: FSMContext):
    await state.clear()  # Clear state before showing groups
    await message.answer('Loading groups...')
    await message.answer('Manage Groups:', reply_markup=get_admin_groups_keyboard(0))



# --- Button to start broadcast ---
@router.message(lambda m: m.text and m.text.startswith('📢 Broadcast'))
async def start_broadcast(message: types.Message, state: FSMContext):
    await message.answer('Enter broadcast text:')
    await state.set_state(BroadcastStates.waiting_for_text)

@router.message(BroadcastStates.waiting_for_text)
async def broadcast_text_entered(message: types.Message, state: FSMContext):
    await state.update_data(broadcast_text=message.text)
    kb = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text='No photo')]], resize_keyboard=True
    )
    await message.answer('Send a photo for the broadcast (or press "No photo")', reply_markup=kb)
    await state.set_state(BroadcastStates.waiting_for_photo)

@router.message(BroadcastStates.waiting_for_photo)
async def broadcast_photo_entered(message: types.Message, state: FSMContext):
    from handlers.client import broadcast_to_users
    data = await state.get_data()
    text = data.get('broadcast_text', '')
    photo_id = None
    if message.photo:
        photo_id = message.photo[-1].file_id
    elif message.text and message.text.lower() == 'no photo':
        photo_id = None
    else:
        await message.answer('Send a photo or press "No photo"')
        return
    await message.answer('Broadcast started!')
    await broadcast_to_users(message.bot, text, photo_id)
    await state.clear()


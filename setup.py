from config import *
from database import *

import aiogram
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext, filters
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.helper import Helper, HelperMode, ListItem

from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.reply_keyboard import ReplyKeyboardMarkup

import datetime
import time
import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
                    )
logger = logging.getLogger(__name__)


bot = Bot(token=telegram_token)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Distribution_Message(StatesGroup):
    message = State()


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(filters.Text(equals='cancel', ignore_case=True), state='*')
async def cancel_save_message(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return None

    await state.finish()
    await message.reply(ANSWERS['cancel'])


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    database = Database('db.db')
    if not database.select_by_user_id('users', message.from_user.id):
        date = datetime.datetime.now()
        database.inset_into('users', [message.from_user.id, message.from_user.first_name, date])
        await message.answer(ANSWERS['start']['true'])
    elif database.select_by_user_id('stop', message.from_user.id):
        await stop(message, only_true=True)
    else:
        await message.answer(ANSWERS['start']['false'])
    await last_distribution(message)


@dp.message_handler(commands=['stop'])
async def stop(message: types.Message, only_true=False):
    if only_true:
        data = Database('db.db')
        data.inset_into('stop', [message.from_user.id, 1, datetime.datetime.now()])
        print('4')
        await message.answer(ANSWERS['stop']['false'])
        return None


    data = Database('db.db')
    is_stopped = None

    stop_list = [[*i] for i in data.select_by_user_id('stop', message.from_user.id)]

    if len(stop_list) == 0:
        data.inset_into('stop', [message.from_user.id, 1, datetime.datetime.now()])
        is_stopped = True
    else:
        for i in range(len(stop_list) - 1):
            for j in range(len(stop_list) - i - 1):
                # datetime.datetime.strptime(date3, '%Y-%m-%d %H:%M:%S.%f')
                if datetime.datetime.strptime(stop_list[j][-1], '%Y-%m-%d %H:%M:%S.%f') <\
                        datetime.datetime.strptime(stop_list[j+1][-1], '%Y-%m-%d %H:%M:%S.%f'):
                    stop_list[j], stop_list[j+1] = stop_list[j+1], stop_list[j]
        if stop_list[0][1] == 0 or stop_list[0][1] == '0':
            data.inset_into('stop', [message.from_user.id, 1, datetime.datetime.now()])
            is_stopped = True
        elif stop_list[0][1] == 1 or stop_list[0][1] == '1':
            data.inset_into('stop', [message.from_user.id, 0, datetime.datetime.now()])
            is_stopped = False

    if is_stopped:
        print('3')
        await message.answer(ANSWERS['stop']['true'])
    elif is_stopped == False:
        print('3')
        await message.answer(ANSWERS['stop']['false'])


@dp.message_handler(commands=['distribution'])
async def last_distribution(message: types.Message):
    last_distrib = Database('posts/post_db.db')
    post = last_distrib.select('post')[-1]
    await message.answer(f"""{ANSWERS['last_distribution']}{datetime.datetime.strptime(post[3], '%Y-%m-%d %H:%M:%S.%f').strftime("%H:%M (%d-%m-%Y)")}""")
    await message.reply_photo(types.InputFile(post[-1]), caption=post[-2])


@dp.message_handler(commands=['admin'])
async def admin(message: types.Message):
    data = Database('db.db')
    admins = data.select_by_user_id('admin', str(message.from_user.id))
    if len(admins) == 0:
        await message.reply(ANSWERS['admin']['false'])
    elif any([(True if str(i[0]) == str(message.from_user.id) else False) for i in admins]):
        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=j[0], callback_data=j[1]) for j in i]
                for i in ANSWERS['admin']['true']['keyboard']
            ]
        )
        await message.reply(ANSWERS['admin']['true']['message'], reply_markup=reply_markup)
    else:
        await message.reply(ANSWERS['admin']['false'])


@dp.callback_query_handler(text='new_distribution')
async def new_distribution(update: types.Update):
    data = Database('db.db')
    admins = data.select_by_user_id('admin', str(update['from'].id))
    if len(admins) == 0:
        await update.message.reply(ANSWERS['admin']['false'])
    elif any([(True if str(i[0]) == str(update['from'].id) else False) for i in admins]):
        await Distribution_Message.message.set()
        await update.message.answer(ANSWERS['new_distribution'])
        print('state start')
    else:
        await update.message.reply(ANSWERS['admin']['false'])


@dp.message_handler(state=Distribution_Message.message, content_types=['photo'])
async def state_new_distribution(message: types.Message, state: FSMContext):
    data = Database('db.db')
    admins = data.select_by_user_id('admin', str(message.from_user.id))

    if len(admins) == 0:
        await message.reply(ANSWERS['admin']['false'])
    elif any([(True if str(i[0]) == str(message.from_user.id) else False) for i in admins]):
        Posts = Database("posts/post_db.db")
        posts = [i for i in Posts.select('post')]
        
        if posts == []:
            Posts.make_dir("posts/1")
            file_info = await bot.get_file(message.photo[-1].file_id)
            new_photo = (await bot.download_file(file_info.file_path)).read()
            with open("posts/1/image%1.png", 'wb') as f:
                f.write(new_photo)
            Posts.inset_into('post', ['1', f"{message.from_user.id}", f"{message.from_user.username}",
                                      f"{datetime.datetime.now()}", f"{message.caption}",
                                      'posts/1/image%1.png'])
        else:
            num = max([int(i[0]) for i in posts]) + 1
            Posts.make_dir(f"posts/{num}")
            file_info = await bot.get_file(message.photo[-1].file_id)
            new_photo = (await bot.download_file(file_info.file_path)).read()
            image_path = f"posts/{num}/image%{num}.png"
            with open(image_path, 'wb') as f:
                f.write(new_photo)
            Posts.inset_into('post', [f'{num}', f"{message.from_user.id}", f"{message.from_user.username}",
                                      f"{datetime.datetime.now()}", f"{message.caption}",
                                      f"posts/{num}/image%{num}.png"])
            await message.send_copy(chat_id=message.from_user.id)
            message_to_copy = message
            await distribution(message_to_copy)
            # await message.send_copy(text=message.caption, )
    else:
        await message.reply(ANSWERS['admin']['false'])

    # async with state.proxy() as data:
    #     print(data)
    #     data['group_id'] = ''

    await state.finish()


async def distribution(message: types.Message, send_notification=False):
    data = Database('db.db')
    admins = data.select_by_user_id('admin', str(message.from_user.id))
    if any([(True if str(i[0]) == str(message.from_user.id) else False) for i in admins]):
        print(data.select('users'))
        users_to_send = []
        is_stopped = False
        for user in data.select('users'):
            print(user)
            print()
            print(data.select_by_user_id('stop', user[0]))
            stop_list = data.select_by_user_id('stop', user[0])
            if stop_list == []:
                is_stopped = False
            else:
                for i in range(len(stop_list) - 1):
                    for j in range(len(stop_list) - i - 1):
                        # datetime.datetime.strptime(date3, '%Y-%m-%d %H:%M:%S.%f')
                        if datetime.datetime.strptime(stop_list[j][-1], '%Y-%m-%d %H:%M:%S.%f') < \
                                datetime.datetime.strptime(stop_list[j + 1][-1], '%Y-%m-%d %H:%M:%S.%f'):
                            stop_list[j], stop_list[j + 1] = stop_list[j + 1], stop_list[j]
                print(f"stop list {stop_list}")
                if stop_list[0][1] == 0 or stop_list[0][1] == '0':
                    is_stopped = False
                elif stop_list[0][1] == 1 or stop_list[0][1] == '1':
                    is_stopped = True
                else:
                    is_stopped = False
            print(f'is stopped {is_stopped}')
            if not is_stopped:
                logs = Database('log.db')
                logs.inset_into('logs', [f'{user[0]}', f'send distribution', 'nothing', f'{datetime.datetime.now()}'])
                await message.send_copy(user[0], disable_notification=not send_notification)


if __name__ == '__main__':
    executor.start_polling(dp)

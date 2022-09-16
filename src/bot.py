import logging
import random
from asyncio import sleep
from pathlib import Path

from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile, Message
from environs import Env


log = logging.getLogger(__name__)

random.seed()
env = Env()

dp = Dispatcher()
TELEGRAM_BOT_TOKEN = env('TELEGRAM_BOT_TOKEN')
bot = Bot(TELEGRAM_BOT_TOKEN, parse_mode="HTML")

TYPE_SPEED = 20
VOXEL_COLOR = '7d7d7d'


async def answer(message: Message, text: str):
    await bot.send_chat_action(message.chat.id, 'typing')
    await sleep(len(text) / TYPE_SPEED)
    log.debug(f'-> {message.from_user.id} {text}')
    await message.answer(text)


STATIC_DIR = Path('static')

VOXEL = FSInputFile(STATIC_DIR / 'voxel-me.jpg')
KIDNAP = FSInputFile(STATIC_DIR / 'ufo-kidnap.jpg')
ESCAPE = FSInputFile(STATIC_DIR / 'escape.jpg')
DOOR_LOCK = FSInputFile(STATIC_DIR / 'door_lock.db')
TUNNELS = FSInputFile(STATIC_DIR / 'tunnels.jpg')
PHOTO = FSInputFile(STATIC_DIR / 'photo.jpg')
SIGN = FSInputFile(STATIC_DIR / 'sign.png')
CONTROL_PANEL = FSInputFile(STATIC_DIR / 'control-panel.jpg')
RUN_AWAY = FSInputFile(STATIC_DIR / 'run-away.jpg')
FLY_AWAY = FSInputFile(STATIC_DIR / 'fly-away.jpg')
MEDAL = FSInputFile(STATIC_DIR / 'medal-of-voxel.png')


@dp.message(commands={"start"})
async def command_start_handler(message: Message):
    log.debug(f'<- {message.from_user.id} {message.text}')
    # user_id = message.from_user.id

    # async with Session.begin() as session:
    #     stmt = select(User).filter_by(telegram_id=telegram_id)
    #     result = await session.execute(stmt)
    #     user = result.scalars().first()

    await message.answer_photo(VOXEL)

    await answer(message, f"Привет, <b>{message.from_user.full_name}!</b> Я кот Воксель, и я люблю программировать на питоне и есть Шебу. Как ты знаешь, скоро....")

    await sleep(5)
    await message.answer_photo(KIDNAP)

    await answer(message, 'Оооо! Меня засасывает в эту тарелку! Только не сейчас, у меня дедлайн на носу...')

    await sleep(3)
    await message.answer('...')

    await answer(message, 'Я оказался в какой-то комнате. Тут ничего нет, кроме двери и какой-то панели с кнопками. Кажется, нужно ввести пароль.')
    await answer(message, 'Дай-ка я подключусь к этой панели, кажется, тут сбоку USB 1.0...')
    await sleep(3)
    await message.answer_photo(ESCAPE)
    await answer(message, 'Вот, тут какой-то файл в корне... Поможешь?')
    await sleep(3)
    await message.answer_document(DOOR_LOCK)


@dp.message()
async def echo_handler(message: types.Message):
    log.debug(f'<- {message.from_user.id} {message.text}')

    text = message.text.lower()

    if text == 'superpass':
        await answer(message, 'Ого! Дверь открылась! Пойду посмотрю, что там...')
        await answer(message, 'Тут сеть коридоров. Попробую придерживаться левой стены')
        await sleep(3)
        await message.answer_photo(TUNNELS)
        await answer(message, 'Надеюсь, тут нет минотавров...')
        await sleep(3)
        await answer(message, 'О, табличка! На ней ничего нет, но я всё равно пришлю тебе фото. Снимаю на тапок.')
        await message.answer_photo(SIGN)

    elif text == 'центр управления':
        await answer(message, 'Отлично! Думаю, там я найду ответы на все вопросы, ну или на худой конец поуправляю чем-нибудь. Вперёд!')
        await sleep(3)
        await answer(message, '...')
        await answer(message, 'Так-с, тут куча приборов.')
        await sleep(3)
        await message.answer_photo(CONTROL_PANEL)
        await answer(message, 'Кажется, я нашёл Самый Главный Компьютер. Он запаролен, конечно.')
        await answer(message, 'Тут рядом цифровая фоторамка. Сейчас скину фото с неё. А что если название страны - пароль?')
        await sleep(3)
        await message.answer_document(PHOTO)

    elif text == 'исландия':  # 64.0133366,-22.1808206
        await answer(message, 'С тобой не пропадёшь! Я уже зашёл от рута')
        await answer(message, 'Что такое "dont_run_this.sh"? Не люблю я баш...')
        await answer(message, '...')
        await answer(message, 'Ну и что, что всё вокруг мигает, ревёт сирена, и отображается обратный отсчёт. Зато открылся потайной ход')
        await answer(message, 'Я уже бегу')
        await sleep(3)
        await message.answer_photo(RUN_AWAY)
        await answer(message, 'Это очень похоже на спасательную шлюпку, но вот эта надпись меня очень смущает: 破碎了')

    elif text in {'сломанный', 'сломано', 'сломана'}:
        await answer(message, 'Серьёзно? А я уже почти залез в эту шлюпку. Ладно, выберу другую.')
        await answer(message, 'Всё готово, я инициировал эвакуацию')
        await answer(message, '...')
        await answer(message, 'Фух!.. Я выбрался и лечу домой. На сегодня с меня хватит.')
        await sleep(3)
        await message.answer_photo(FLY_AWAY)
        await answer(message, 'Кажется, те странные существа не очень довольны, ну да ладно.')
        await answer(message, 'Спасибо! Без тебя я бы не справился, это точно. В награду я скажу тебе слово, которое только что пришло мне в голову: Румпельштильцхен. Сможешь напечатать?')

    elif text == 'румпельштильцхен':
        user = message.from_user
        log.info(f'! {user.id=} {user.username=} {user.first_name=} {user.last_name=}')
        await bot.forward_message(391679541, message.chat.id, message.message_id)
        await answer(message, 'Ура! Вы прошли эту игру, за что вам вручается медаль:')
        await sleep(3)
        await message.answer_photo(MEDAL)
        await answer(message, 'Подведение итогов ждите <a href="https://t.me/blog_pogromista">на канале</a>. А пока там же можете написать о своих впечатлениях от игры, но просим вас не спойлерить решение, чтобы другим было интересно :) ')

    else:
        msg = random.choice([
            'Нет, что-то не так :(',
            'Не работает',
            'Непонятно',
            'Неть',
            'Увы',
            'Попробуй ещё раз',
            'Не-а'
        ])
        await answer(message, msg)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(message)s',
        level=logging.DEBUG,
    )
    dp.run_polling(bot)

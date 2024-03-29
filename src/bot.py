import logging
import random
from asyncio import sleep
from functools import cache
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.types import FSInputFile, KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from emoji import emojize
from environs import Env

log = logging.getLogger(__name__)

random.seed()
env = Env()

TELEGRAM_BOT_TOKEN = env('TELEGRAM_BOT_TOKEN')
TELEGRAM_ADMIN_ID = env.int('TELEGRAM_ADMIN_ID')
TELEGRAM_HELP_NICKNAME = env('TELEGRAM_HELP_NICKNAME')
TELEGRAM_CHANNEL = env('TELEGRAM_CHANNEL')
TELEGRAM_BLACKLIST = env.list('TELEGRAM_BLACKLIST', subcast=int)

STATIC_DIR = Path('static')
TYPE_SPEED = 40
READ_SPEED = 20
ERROR_MESSAGES = [
    'Нет, что-то не так :(',
    'Не работает',
    'Непонятно',
    'Увы',
    'Попробуй ещё раз',
    'Не-а',
]

dp = Dispatcher()
bot = Bot(TELEGRAM_BOT_TOKEN, parse_mode="HTML")


async def answer(message: Message, text: str, keyboard: ReplyKeyboardMarkup | None = None):
    await bot.send_chat_action(message.chat.id, 'typing')
    await sleep(len(text) / TYPE_SPEED)
    log.debug(f'-> {message.from_user.id} {text}')
    await message.answer(emojize(text), reply_markup=keyboard or ReplyKeyboardRemove())
    await sleep(len(text) / READ_SPEED)


async def answer_batch(message: Message, texts: list[str], keyboard: ReplyKeyboardMarkup | None = None):
    for text in texts[:-1]:
        await answer(message, emojize(text))

    await answer(message, emojize(texts[-1]), keyboard=keyboard)


@cache
def get_file(name: str) -> FSInputFile:
    return FSInputFile(STATIC_DIR / name)


@dp.message(commands={"start"})
async def command_start_handler(message: Message):
    await echo_handler(message)


def has(text: str, tokens: list[str]) -> bool:
    return any(token in text for token in tokens)


async def chapter(message: Message, title: str, number: int, total: int, media: str | None = None):
    await sleep(4)
    await answer(message, f'<b>Глава {number}. {title}</b>\n{"●"*number}{"○"*(total-number)}')
    await sleep(2)
    if media:
        method = message.answer_animation if media.endswith('.mp4') else message.answer_photo
        await method(get_file(media))
        await sleep(2)


@dp.message()
async def echo_handler(message: Message):
    user = message.from_user
    log.debug(f'<- {user.id} @{user.username} {message.text}')
    if not user:
        return

    if user.id != TELEGRAM_ADMIN_ID:
        await bot.forward_message(TELEGRAM_ADMIN_ID, message.chat.id, message.message_id)
    # elif message.reply_to_message:
    #     from pprintpp import pformat
    #     await message.reply_to_message.answer(pformat(message.reply_to_message.__dict__))
    #     return

    if user.id in TELEGRAM_BLACKLIST:
        await answer(message, 'Что-то пошло не так :(')
        return

    text = message.text.lower().strip()

    if has(text, ['start', 'старт']):
        await answer_batch(message, [
            'Добро пожаловать в игру! :slightly_smiling_face: Этот квест - как интерактивная книжка, где время от времени нужно решать головоломки, чтобы двигать сюжет дальше. Так что пригодятся смекалка и знание IT.',
            'Прогресс отмечен точками: ●●○○. Никаких временных рамок нет, можете играть сколько угодно и когда угодно.',
            'Для каждой загадки ответ - это какое-то слово или фраза, регистр для бота не важен. Символ-хантингом заниматься тоже не надо, бот ищет в вашем ответе подстроку, поэтому всякие окончания, как правило, не важны.',
            f'Отвечать нужно только когда бот ждёт от вас ответа. Если застряли, то вот вам подсказки :winking_face:',
        ])
        await message.answer_document(get_file('VoxelQuest help.pdf'))
        await answer_batch(message, [
            'Готовы? Для старта игры напишите слово "поехали" :rocket: :flying_saucer:',
        ])

    elif has(text, ['поехали']):
        await chapter(message, 'Дом', 1, 5, 'room.jpg')

        await answer_batch(message, [
            'Только одно нажатие кнопки.',
            'Тишина.',
            'Активное шумоподавление отсекает всё: шум ночного города, гул пролетающих самолётов, крики на улице и даже безумных соседей. Совсем недавно я придумал их пьяным посиделкам вполне достойное название: "пир во время чумы". Никто на свете не придумал бы название лучше.',
            'Как хорошо, что у меня есть эта кнопка.',
            'Забавно, но у шумоподавления есть интересный эффект: ты начинаешь <i>слышать</i> тишину. Наверно, это можно понять, только попробовав самому. Несколько минут я слушаю тишину.',
            'Привычным движением я включаю ноут. Пароль защитит от кражи ноута, но сильно я не заморачивался: кому надо - дешифрует любые пароли, если вы понимаете, о чём я. Поэтому пароль - прямо тут, на столе, в фоторамке. Как её зовут?',
        ])
        await message.answer_photo(get_file('photo-frame.jpg'))

    elif has(text, ['freya', 'фрея', 'фрейя']):
        await answer_batch(message, [
            'Да... Имя классное. Что-то там из скандинавской мифологии, и Википедия говорит, что "равных ей по красоте не было и нет во всем мире ни среди богов, ни среди людей". Зачем это написано? Я это понял и без википедии, когда впервые с ней встретился.',
            'Как будто это было в другой жизни. Жизни, где светит жаркое солнце <i>другой</i> страны, с океана дует ветер, в кармане ключи от тачки, которая может довезти куда угодно, а рядом сидит лучшая девчонка на свете, и впереди ждёт что-то хорошее...',
            'Конечно, это не сказка, а серая жизнь, так что ничего хорошего меня впереди не ждало. Зато ждало бесконечное самокопание и разочарование.',
            'Все эти отношения - чушь собачья, потому что выбираешь ты одного человека, а спустя время обнаруживаешь, что он другой. А может, другим становишься ты сам. Иногда это вскрывается слишком поздно.',
            'К чёрту людей. "Нахрен общество".',
            'Я открываю специальный поисковик по интернету вещей:',
        ])

    elif has(text, ['shodan']):
        await answer_batch(message, [
            'В последнее время я подсел на просмотр взломанных IP камер - точнее, не взломанных даже, а открытых всему миру. Никаких моральных угрызений совести - они же <i>открыты</i> всем желающим, так что почему бы мне не стать этим желающим? ',
            'Какой-нибудь психолог сказал бы, что этими наблюдениями я компенсирую отсутствие собственной жизни, и даже был бы прав, наверно, но я предпочитаю думать, что это просто развлечение.',
            'Чего я только не видел! Драки, секс, бесконечные поиски закладок, один раз даже покушение - в общем, у меня теперь довольно скверное мнение о человеческой расе, но я всё равно зачем-то смотрю, как будто надеюсь найти что-то...',
            'А вот и первый улов за сегодня! Не веб-камера, но тоже интересный девайс. Я вбиваю логин: pi, пароль: ',
        ])

    elif has(text, ['raspberry']):
        await answer_batch(message, [
            '...и получаю доступ к шеллу. ',
            'Зачем люди стараются, придумывают все эти rsa/ed25519 ключи, когда идиоты просто оставляют прямой доступ всем желающим?..',
            'Сканирую устройство, но не нахожу ничего стоящего, разве что какие-то скрипты. Скачиваю их на всякий случай, потом изучу в песочнице.',
            'Я нажимаю ctrl+d, чтобы завершить ssh сессию и отсоединиться. Но тут случается то, чего я не ожидаю: ничего не происходит! Вбиваю пару команд, чтобы убедиться: всё работает, но человеческими способами сессия закрываться не хочет. Похоже, стоит какой-то обработчик на символ окончания ввода.',
            'Это чертовски интересно! Как они это сделали? Кастомный шелл? Или баг в ssh? Я трачу минут 10, проверяя различные гипотезы, пока не вбиваю безобидную команду journalctl и вижу среди логов:',
            '<code>193.238.131.201</code>',
            'Что это за город?',
        ])

    elif has(text, ['новосиб', 'novosibirsk']):
        await answer_batch(message, [
            'Мой город.',
            'Сердце громко застучало, руки затряслись.',
            'Я узнал его. Это был мой ip!',
            'Мне начало казаться, что я просто в очередной тупом сне. Я сидел из-под защищённой <b>операционной системы</b>...',
        ])

    elif has(text, ['tails', 'kali', 'whonix']):
        await answer_batch(message, [
            'Весь трафик шёл через tor, но тем не менее мой чистый домашний ip прямо тут, в логах!',
            'Стереть! Стереть всю систему к чертям, потому что я понятия не имею, где ещё сохранился мой ip.',
            '<code>Shred</code>...',
            'Я представил, как где-то на другом конце мира блоки флэш-памяти перезаписываются случайными байтами... Поможет ли?',
            'Я вбил последнюю команду и снёс всю файловую систему. Надеюсь, на том конце спишут на проблемы с памятью, космическую радиацию, ктулху или во что они там верят. Главное - никакого хакера там никогда не было.',
            'Я выключил комп, снял гарнитуру. Стояла невиданная тишина! Даже соседи заткнулись, как будто ублюдки тоже осознавали величину моего факапа и замерли в предвкушении.',
            'Надо просто лечь спать, утро вечера мудренее. На удивление, как только моя голова коснулась подушки, я провалился в сон...',
        ])

        await chapter(message, 'Сон', 2, 5, 'car-driving-fast.mp4')
        await sleep(5)

        await answer_batch(message, [
            'Мне снится, что я еду в машине куда-то далеко-далеко. На дороге пусто, вокруг темно, и только тусклые фонари и фары освещают кусочек дороги впереди. Даже звёзд на небе нет. Дорога среди пустоты. Флоатинг.',
            'Я не вижу ни одного указателя, но, как и бывает во снах, отчётливо понимаю, куда еду. Вернее, <i>откуда</i>.',
            'Прочь из города.',
            'Из динамиков доносится',
        ])
        await message.answer_audio(get_file('music.mp3'))

    elif has(text, ['find me', 'when you', 'wake up', 'edge of tomorrow', 'грань будущего']):
        await answer_batch(message, [
            'Эта мелодия, фары, разгоняющие тьму, урчание двигателя... Дежавю во сне.',
            'Я понимаю, что вижу всё это не впервые. Всё это повторялось много раз, но я не могу никак вспомнить, что же было дальше. Я выехал из города и куда-то приехал или кого-то встретил... Кого-то... Кого? Или что?..',
            'И тут, словно в ответ на мой вопрос, у вдруг увидел нечто, поднимающееся впереди. Я встретил <b>это</b>!',
        ])
        await message.answer_animation(get_file('colossus-appear.mp4'))
        await sleep(17)
        await answer_batch(message, [
            'Удар по тормозам. Мозг отказывается верить в происходящее, но вот оно, передо мной, гиперреальное, даже более настоящее, чем в жизни!',
            'И, кажется, оно не очень дружелюбное.',
            'Я разворачиваю тачку, вдавливаю педаль газа и сваливаю оттуда. Должен быть другой путь.',
            'Я пробую другие дороги. Как мышь в лабиринте. На одной из дорог машина попадает в яму и застревает. Бросаю машину.',
            'Существ уже несколько. Они идут за мной.',
        ])
        await message.answer_animation(get_file('road-colossus-many.mp4'))
        await sleep(3)
        await answer_batch(message, [
            'Я бегу, но они настигают меня. Земля дрожит.',
            'Я умираю...',
            'и просыпаюсь.',
        ])

        await chapter(message, 'Утро', 3, 5, None)
        await answer_batch(message, [
            'Паршивое утро.',
            'Всю ночь мне снилось тревожные сны, но, как и бывает со снами, я не помню нечего, что там происходило. Осталось только чувство опасности. Спасибо, можно подумать, в жизни мне этого не хватает.',
            'От безысходности я решаю посмотреть скрипты, которые я раздобыл вчера. Этот, кажется, вообще нерабочий. Это мусор. Неужели вчера всё было зря?.. Так, а вот тут что-то есть...',
        ])

        await message.answer_document(get_file('locator-api.py'))

    elif has(text, ['94.228.125.235']):
        await answer_batch(message, [
            'Нашёл вот этот ip. Что там?',
        ])

    elif has(text, ['68.94', '94.50']):
        await answer_batch(message, [
            'Что это за место?',
        ])

    elif has(text, ['путоран']):
        await answer_batch(message, [
            'Что там? Что за девайсы раскиданы по всей России? Метеорологические станции? Ретрансляторы? И почему почти все уничтожены?',
            'Я езжу по гугл-картам в надежде увидеть в полученных координатах какую-нибудь вышку и успокоиться, но ничего не нахожу.',
            'Чем я вообще занимаюсь?!',
            'Уже наступил полдень, а я как дурак пытаюсь найти какой-то смысл в криво написанном api. Может, это вообще staging с тестовым данными, или api по геолокации коров и тракторов. Кто, блин, будет передавать что-то ценное по незащищённому http? К чёрту эти карты, девайсы и сервисы!',
            'Я одеваюсь и выхожу на улицу. Иду туда же, куда и вчера. И позавчера. И позапозавчера.',
        ])

        await chapter(message, 'Амстердам', 4, 5, 'bar.jpg')
        await answer_batch(message, [
            'В "Амстердаме" меня уже знают. Наливают без спроса. Не за 119,53 секунды, но всё равно долго.',
        ])

    elif has(text, ['guinness', 'guines', 'гинес', 'гиннес']):
        await answer_batch(message, [
            'Он самый! Я пью, пока пружина внутри меня не разогнётся. Пока хватка собственных комплексов не ослабнет. Пока социофобия не отступит.',
            'Я почти нормальный. Почти как все. Как там? "Ровно по стандарту, строго по закону, жёстко по лекалу, чётко по канону".',
        ])

    elif has(text, ['окси', 'oxxxy', 'цунами', 'tsunami']):
        await answer_batch(message, [
            'Точно! Как я его понимаю!',
            'Мир покачивается, руки и ноги будто не мои, а я всё пью и надеюсь, что случится что-то новое. Не вчера, так сегодня. Не сегодня, так завтра. Некто по имени Вас сказал бы, что я безумец. Очень может быть.',
            'Я становлюсь весёлым и глупым. Проблемы уже не кажутся проблемами, мнение немногочисленных людей вокруг перестаёт меня волновать, и на миг мне даже кажется, что всё снова хорошо, как раньше...',
            'За стойку рядом со мной садится девушка. Симпатичная, а на руке <b>татуировка</b>',
        ])

    elif has(text, ['кролик', 'rabbit']):
        await answer_batch(message, [
            'Я хмыкаю. Всё по канону, сейчас отовсюду набегут агенты Смиты и начнется кунг-фу, а потом я спасу Зион и научусь включать комп силой мысли.',
            'Девушка смотрит на меня и видит мой взгляд.',
            '<i>"Это не тату, а штамп из клуба - для входа. Меняют каждый раз, вчера вот был кролик. Теперь все думают, что за мной нужно идти, и я должна их куда-то привести."</i>',
            'Она мило улыбается, а я и не знаю, что ответить. Дебил.',
        ], keyboard=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text='Отшить')],
                [KeyboardButton(text='Сказать комплимент')],
            ],
            one_time_keyboard=True,
            resize_keyboard=True,
        ))

    elif has(text, ['отшить']):
        await answer_batch(message, [
            '"Меня не надо вести, я сам дойду куда надо"',
            '<i>"Ты себя видел? Судя по твоему виду, ты и ходить-то не можешь уже."</i>',
        ], keyboard=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text='Спорить')],
                [KeyboardButton(text='Промолчать')],
            ],
            one_time_keyboard=True,
            resize_keyboard=True,
        ))

    elif has(text, ['спорить']):
        await answer_batch(message, [
            'Я встаю. То-то же! Пусть знает, что программистов так просто не победить! Я стою секунд 5, а потом земля начинает кружиться с такой силой, что мне приходится плюхнуться обратно на стул. Во избежание.',
            '<i>"Не видела в жизни ничего более героического!"</i> Ее голос полон сарказма, но не злого.',
        ])

        message.__dict__['text'] = '>>taxi'
        await echo_handler(message)

    elif has(text, ['промолчать']):
        await answer_batch(message, [
            'Я молчу. Не в моей ситуации что-то говорить, когда мир вертится волчком, а ноги не держат.',
            '<i>"И часто он так?"</i> - спрашивает она бармена. Тот вздыхает. Вот скотина!',
        ])

        message.__dict__['text'] = '>>taxi'
        await echo_handler(message)

    elif has(text, ['сказать комплимент']):
        await answer_batch(message, [
            '"Если бы Нео встретил тебя, к Тринити он бы уже не пошёл"',
            'Моему алко-мозгу кажется, что после такого толстого комплимента мне будут готовы отдаться все женщины мира.',
            '<i>"Мне никогда не нравился Нео. Такой наивный!"</i>'
        ], keyboard=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text='Возразить')],
                [KeyboardButton(text='Согласиться')],
            ],
            one_time_keyboard=True,
            resize_keyboard=True,
        ))

    elif has(text, ['возразить']):
        await answer_batch(message, [
            '"Дамочка, он вообще-то человечество спас. И он Киану Ривз!"',
            'Похоже, это не произвело на неё никакого впечатления, но спорить она не стала.',
        ])

        message.__dict__['text'] = '>>taxi'
        await echo_handler(message)

    elif has(text, ['согласиться']):
        await answer_batch(message, [
            '"Если честно, мне тоже"',
            'Хочешь понравиться девушке - соглашайся с ней. Это сработало, и она с интересом смотрит на меня.',
            '<i>"А ты забавный. Обсудим это в другом месте?"</i>',
        ])

        message.__dict__['text'] = '>>taxi'
        await echo_handler(message)

    elif has(text, ['>>taxi']):
        await answer_batch(message, [
            'Кажется, мы ещё болтали о всяком. Вроде я рассказывал ей о том, почему декорировать классы - плохо, и о пришельцах на тракторах в глубине Путораны. Может, что-то ещё.',
            'Последнее, что я помню - мы садимся в такси. Я уже говорил вам, что я мастер пикапа?',
        ])

        await chapter(message, 'Подвал', 5, 5, None)
        await answer_batch(message, [
            'Холодно.',
            'Я открываю глаза. Меня мутит.',
            'Вечер. Я лежу на полу в каком-то подвале. Если возникнет вопрос, где пережидать похмелье - не выбирайте подвал. Мне, во всяком случае, не понравилось.',
            'Пока я прихожу в себя, я пытаюсь вспомнить последние события. Геолокация, бар, девчонка, такси... Дальше пусто.',
            'Я, конечно, не эксперт, но, по-моему, свидания не заканчиваются в подвале с запертой дверью. Или это так принято сейчас?',
            'Место смутно знакомое, из моего диггерского прошлого. Где я?',
        ])
        await message.answer_photo(get_file('basement.jpg'))

    elif has(text, ['сибсельмаш']):
        await answer_batch(message, [
            'Как хорошо, что я знаю Новосиб! Щас наберу корешу...',
            'Так. У меня забрали телефон.',
            'Без телефона я чувствую себя странно. Как будто у меня нет руки - вроде жив, но процентов на 70%.',
            'Кто бы это ни был, он кое-что упустил. Мой Flipper zero.',
            'И да, на нём нет wifi. Успех. Но зато есть...',
        ])

    elif has(text, ['bluetooth']):
        await answer_batch(message, [
            'Я включаю bluetooth и... и, собственно, что? Мой план был назвать девайс в стиле "pomogite, ya v podvale" и начать коннектиться ко всему вокруг, но, внезапно, я не могу переименовать мой флиппер. Никто не пойдет спасать чувака, у которого bluetooth называется <code>L4pi0b</code>.',
            'Придется по старинке.',
            'Дверь должна открываться наружу. Я толкаю ее плечом, сначала робко, потом всё смелее и смелее. Вот я уже колочу со всей силой. Дверь медленно поддается, вот только непонятно, кто из нас выдохнется быстрее.',
            '...',
            'Дверь падает. Следом падаю я и лежу. Просто дышу. Плечо я уже не чувствую, похоже, у меня будет классный синяк. ',
            'Как хорошо, что я айтишник. Был бы каким-нибудь борцухой - вынес бы дверь за раз, и было бы скучно.',
            'Я встаю и осматриваюсь. Самое обычное заброшенное здание. Никаких следов вчерашнего свидания. Я думал, будут хотя бы лепестки роз повсюду.',
            'Разочарованный, выбираюсь на улицу, ловлю такси и добираюсь до дома, благо кошелёк у меня не забрали. Странно, кстати.',
            'Дом встречает меня тишиной и уютом. На сегодня приключений хватит.',
            'Есть только что-то, что не даёт мне покоя. Как будто что-то важное, что я не должен был забыть. Я думаю, думаю, думаю... И среди обрывков алкогольных воспоминаний припоминаю момент, как я пытаюсь рассмешить девушку рассказом про геодатчики, а она не смеётся. ',
            'Пьяный мозг списал это на неудачную шутку, но сейчас мне кажется, что причина совсем другая. Похоже, со мной познакомились не потому что я пьяный мачо...',
            'Включаю комп, линукс радуется мне, и я открываю ту самую картинку, которая на самом деле скрывает в себе кое-что. И да, я знаю, что использовать одно и то же - имя девушки - для входа в систему и для шифрования - плохо. Но тут расчет на то, что никто вообще не будет искать что-то в картинке.',
            '<code>steghide</code>... А в картинке-то спрятаны интересные слова...',
        ])
        await message.answer_document(get_file('kitty.jpg'))

    elif has(text, [
        'mosquito', 'diagram', 'now', 'carbon', 'fault', 'record', 'genius', 'allow', 'quick', 'animal', 'milk', 'twice',
    ]):
        await answer_batch(message, [
            'Я добавляю ключ в криптокошелёк, и на экране высвечивается круглая сумма. Вообще я хотел потратить ее на отдых где-нибудь в Гренландии, но теперь планы поменялись.',
            'Потому что пора наконец съездить на Путорану и разыскать эту чёртову корову с gps! Ну или трактор.',
        ])
        await sleep(3)

        await answer_batch(message, [
            f'<i>Вот и всё! Поздравляю с успешным прохождением квеста. Надеюсь, вам понравилось, но даже если нет - всё равно буду рад вашему отзыву. Его можно оставить (без спойлеров) <a href="https://t.me/{TELEGRAM_CHANNEL}">на моём канале</a>, а если у вас есть идеи для будущих заданий - можете кидать в личку. </i>',
        ])

    else:
        msg = random.choice(ERROR_MESSAGES)
        await answer(message, msg)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(message)s',
        level=logging.DEBUG,
    )
    dp.run_polling(bot)

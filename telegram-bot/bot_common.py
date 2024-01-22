"Общие команды бота"
import os
import json
from urllib.parse import urljoin

import pandas as pd
import requests
from aiogram import Router, types
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder


BASE_URL = os.environ['FAST_API_ADDR']
TIMEOUT = 30
CONNECT_ERROR = 'Не удалось подключиться к сервису. Повторите попытку позже'
CREATE_DATA_EXAMPLE = """{
    "name": "Mila",
    "pk": 888,
    "kind": "terrier"
}"""
UPDATE_DATA_EXAMPLE = """{
    "name": "Mila",
    "old_pk": 888,
    "pk": 777,
    "kind": "terrier"
}"""

router = Router()


class DogsAction(StatesGroup):
    """Класс состояний запросов"""
    dog_creating = State()
    dog_getting = State()
    dog_updating = State()


@router.message(Command("start"))
async def cmd_inline_url(message: types.Message):
    """
    Хэндлер для команды start.
    Список доступных команд
    """
    text = (
        "Здравствуйте!\n\n"
        "Я бот <b>ветеринарной клиники</b> 🐩.\n"
        "Выберите команду:",
    )
    builder = InlineKeyboardBuilder()
    commands = [
        'get_description',
        'post_timestamp',
        'get_dogs',
        'create_dog',
        'get_dog',
        'update_dog'
    ]
    for command in commands:
        builder.row(types.InlineKeyboardButton(
            text=command, callback_data=command)
        )

    await message.answer(
        ''.join(text),
        parse_mode=ParseMode.HTML,
        reply_markup=builder.as_markup(),
    )


def get_response(url, method='GET', **kwargs):
    "Формирует запрос к сервису на fastapi"
    if method.upper() == 'PATCH':
        response = requests.patch(url, timeout=TIMEOUT, **kwargs)
    elif method.upper() == 'POST':
        response = requests.post(url, timeout=TIMEOUT, **kwargs)
    else:
        response = requests.get(url, timeout=TIMEOUT, **kwargs)

    try:
        response_data = response.json()
    except json.JSONDecodeError:
        response_data = response.text
    return response.status_code, response_data


@router.callback_query(lambda c: c.data == 'get_description')
async def get_description_click(callback_query: types.CallbackQuery):
    """
    Хэндлер для команды get_description.
    Возвращает описание сервиса на fastapi
    """
    url = BASE_URL
    status, response_text = get_response(url, 'GET')
    if status//100 != 2:
        await callback_query.message.answer(CONNECT_ERROR)
        return

    await callback_query.message.answer(
        f'<b>Описание сервиса:</b>\n{response_text}',
        parse_mode=ParseMode.HTML
    )


@router.callback_query(lambda c: c.data == 'post_timestamp')
async def post_timestamp_click(callback_query: types.CallbackQuery):
    """
    Хэндлер для команды post_timestamp.
    Возвращает текущее время
    """
    url = urljoin(BASE_URL, 'post')
    status, response_json = get_response(url, 'POST')
    if status//100 != 2:
        await callback_query.message.answer(CONNECT_ERROR)
        return
    dumped_json = json.dumps(response_json, indent=4)
    await callback_query.message.answer(
        f'<b>Добавлен timestamp:</b>\n<code>{dumped_json}</code>',
        parse_mode=ParseMode.HTML
    )


@router.callback_query(lambda c: c.data == 'get_dogs')
async def get_dogs_click(callback_query: types.CallbackQuery):
    """
    Хэндлер для команды get_dogs.
    Возвращает список всех собак в базе
    """
    url = urljoin(BASE_URL, 'dog')
    status, response_json = get_response(url, 'GET')
    if status//100 != 2:
        await callback_query.message.answer(CONNECT_ERROR)
        return
    dog_df = pd.DataFrame(response_json)
    await callback_query.message.answer(
        f"<b>Список собак</b>:\n<pre>{dog_df}</pre>",
        parse_mode='HTML'
    )


@router.callback_query(lambda c: c.data == 'get_dog')
async def get_dog_click(
    callback_query: types.CallbackQuery,
    state: FSMContext
):
    """
    Хэндлер для команды get_dog.
    Просит ввести pk собаки, данные которой нужно получить
    """
    await state.set_state(getattr(DogsAction, 'dog_getting'))
    await callback_query.message.answer(
        '<b>Добавление собаки</b>:\nВведите pk',
        parse_mode='HTML'
    )


@router.callback_query(lambda c: c.data == 'create_dog')
async def create_dog_click(
    callback_query: types.CallbackQuery,
    state: FSMContext
):
    """
    Хэндлер для команды create_dog.
    Просит ввести информацию о собаке для добавления в базу
    """
    await state.set_state(getattr(DogsAction, 'dog_creating'))
    text = (
        '<b>Добавление собаки</b>',
        'Введите данные собаки в формате:',
        f'<code>{CREATE_DATA_EXAMPLE}</code>'
    )
    await callback_query.message.answer(
        '\n'.join(text),
        parse_mode='HTML'
    )


@router.callback_query(lambda c: c.data == 'update_dog')
async def update_dog_click(
    callback_query: types.CallbackQuery,
    state: FSMContext
):
    """
    Хэндлер для команды update_dog.
    Просит ввести информацию о собаке для обновления
    """
    await state.set_state(getattr(DogsAction, 'dog_updating'))
    text = (
        '<b>Обновление собаки</b>',
        'Введите данные собаки в формате:',
        f'<code>{UPDATE_DATA_EXAMPLE}</code>'
    )
    await callback_query.message.answer('\n'.join(text), parse_mode='HTML')


@router.message(DogsAction.dog_creating)
async def create_dog(message: types.Message, state: FSMContext):
    """
    Создание новой собаки
    """
    await state.clear()
    try:
        dog_data = json.loads(message.text)
    except json.JSONDecodeError:
        await message.answer(
            'Указан некорректный json'
        )
        return
    url = urljoin(BASE_URL, 'dog')
    status, response_json = get_response(url, 'POST', json=dog_data)
    if status//100 != 2 and status//100 != 4:
        await message.answer(CONNECT_ERROR)
        return
    dumped_json = json.dumps(response_json, ensure_ascii=False)
    if status//100 == 4:
        await message.answer(
            f'Ошибка при создании собаки:\n<code>{dumped_json}</code>',
            parse_mode='HTML'
        )
        return
    await message.answer(
        f'<b>Создана собака:</b>\n<code>{dumped_json}</code>',
        parse_mode='HTML'
    )


@router.message(DogsAction.dog_updating)
async def update_dog(message: types.Message, state: FSMContext):
    """
    Обновление информации о собаке
    """
    await state.clear()
    try:
        dog_data = json.loads(message.text)
    except json.JSONDecodeError:
        await message.answer(
            'Указан некорректный json'
        )
        return
    if 'old_pk' not in dog_data:
        await message.answer(
            'Не указан текущий pk собаки'
        )
        return
    pk = dog_data["old_pk"]
    url = urljoin(BASE_URL, f'dog/{pk}')
    status, response_json = get_response(url, 'PACH', json=dog_data)
    if status//100 != 2 and status//100 != 4:
        await message.answer(CONNECT_ERROR)
        return
    dumped_json = json.dumps(response_json, ensure_ascii=False)
    if status//100 == 4:
        await message.answer(
            f'Ошибка при обновлении данных:\n<code>{dumped_json}</code>',
            parse_mode='HTML'
        )
        return
    await message.answer(
        f'<b>Обновлены данные собаки {pk}:</b>\n<code>{dumped_json}</code>',
        parse_mode='HTML'
    )


@router.message(DogsAction.dog_getting)
async def get_dog(message: types.Message, state: FSMContext):
    """
    Получение данных собаки
    """
    await state.clear()
    pk = message.text
    if not pk.isdigit():
        await message.answer(
            'pk должен быть числовым'
        )
        return
    url = urljoin(BASE_URL, f'dog/{pk}')
    status, response_json = get_response(url, 'GET')
    if status//100 != 2 and status//100 != 4:
        await message.answer(CONNECT_ERROR)
        return
    dumped_json = json.dumps(response_json, ensure_ascii=False)
    if status//100 == 4:
        await message.answer(
            f'Ошибка при получении данных:\n<code>{dumped_json}</code>',
            parse_mode='HTML'
        )
        return
    await message.answer(
        f'<b>Информация о собаке {pk}:</b>\n<code>{dumped_json}</code>',
        parse_mode='HTML'
    )

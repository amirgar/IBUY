import logging
import asyncio
import sqlite3 as sql3
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from dotenv import load_dotenv
import os


class Product(StatesGroup):
    name = ""
    description = ""
    size = ""
    condition = ""
    price = 0
    st_name = State()
    st_description = State()
    st_size = State()
    st_condition = State()
    st_price = State()
    st_photo = State()


class DeleteProduct(StatesGroup):
    id = 0
    st_delete = State()


class EditProduct(StatesGroup):
    id = 0
    name = ""
    description = ""
    size = ""
    condition = ""
    price = ""
    st_name = State()
    st_description = State()
    st_size = State()
    st_condition = State()
    st_price = State()
    st_photo = State()
    st_id = State()


KEYBOARD_START = [
    [
        types.KeyboardButton(text="ДОБАВИТЬ ТОВАР"),
        types.KeyboardButton(text="РЕДАКТИРОВАТЬ ТОВАР"),
        types.KeyboardButton(text="УДАЛИТЬ ТОВАР"),
    ],
]
KEYBOARD_BACK = [
    [
        types.KeyboardButton(text="ВЕРНУТЬСЯ В НАЧАЛО"),
    ]
]
current_product = Product()
current_delete = DeleteProduct()
current_edit = EditProduct()

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
API_TOKEN = os.environ.get("API_TOKEN")
ADMINS = list(map(int, os.environ.get("ADMINS").split(",")))
logging.basicConfig(level=logging.WARNING)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message(Command("start", "help"))
async def send_start(message: types.Message):
    if message.from_user.id not in ADMINS:
        return
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=KEYBOARD_START,
        resize_keyboard=True,
        input_field_placeholder="Нажмите на необходимую кнопку",
    )
    await message.reply("Выберите необходимый тип операции", reply_markup=keyboard)


@dp.message(F.text.lower() == "вернуться в начало")
async def send_start(message: types.Message):
    if message.from_user.id not in ADMINS:
        return
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=KEYBOARD_START,
        resize_keyboard=True,
        input_field_placeholder="Нажмите на необходимую кнопку",
    )
    await message.reply("Выберите необходимый тип операции", reply_markup=keyboard)


@dp.message(F.text.lower() == "добавить товар")
async def create_product(message: types.Message, state: FSMContext):
    global current_product
    if message.from_user.id not in ADMINS:
        return
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=KEYBOARD_BACK,
        resize_keyboard=True,
    )
    await state.clear()
    await message.reply("Введите название товара:", reply_markup=keyboard)
    await state.set_state(current_product.st_name)


@dp.message(Product.st_name)
async def get_data(message: types.Message, state: FSMContext):
    global current_product
    if message.from_user.id not in ADMINS:
        return
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=KEYBOARD_BACK,
        resize_keyboard=True,
    )
    current_product.name = message.text
    await message.reply("Введите описание товара:", reply_markup=keyboard)
    await state.set_state(current_product.st_description)


@dp.message(Product.st_description)
async def get_data(message: types.Message, state: FSMContext):
    global current_product
    if message.from_user.id not in ADMINS:
        return
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=KEYBOARD_BACK,
        resize_keyboard=True,
    )
    current_product.description = message.text
    await message.reply(
        "Введите размер товара (если нет поставьте -): ", reply_markup=keyboard
    )
    await state.set_state(current_product.st_size)


@dp.message(Product.st_size)
async def get_data(message: types.Message, state: FSMContext):
    global current_product
    if message.from_user.id not in ADMINS:
        return
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=KEYBOARD_BACK,
        resize_keyboard=True,
    )
    current_product.size = message.text
    await message.reply(
        "Введите состояние товара (если нет поставьте -): ", reply_markup=keyboard
    )
    await state.set_state(current_product.st_condition)


@dp.message(Product.st_condition)
async def get_data(message: types.Message, state: FSMContext):
    global current_product
    if message.from_user.id not in ADMINS:
        return
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=KEYBOARD_BACK,
        resize_keyboard=True,
    )
    current_product.condition = message.text
    await message.reply("Введите цену товара: ", reply_markup=keyboard)
    await state.set_state(current_product.st_price)


@dp.message(Product.st_price)
async def get_data(message: types.Message, state: FSMContext):
    global current_product
    if message.from_user.id not in ADMINS:
        return
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=KEYBOARD_BACK,
        resize_keyboard=True,
    )
    current_product.price = message.text
    try:
        data = (
            current_product.name,
            current_product.description,
            current_product.size,
            current_product.condition,
            current_product.price,
        )
        conn = sql3.connect("product_list.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO product_list (name, description, size, condition, price) VALUES (?, ?, ?, ?, ?)",
            data,
        )
        conn.commit()
        cursor.execute("SELECT * FROM product_list")
        product_id = cursor.fetchall()[-1][0]
        answer = f"Данные о товаре\nНазвание: {current_product.name}\nОписание: {current_product.description}\nРазмер: {current_product.size}\nСостояние: {current_product.condition}\nЦена: {current_product.price}\nТовар успешно добавлен! Выдан уникальный id товара - {product_id}"
        await message.reply(answer)
        await message.reply(
            "Если необходимо, чтобы у товара были фотографии на сайте, то создайте в Яндекс Диске папку с данным id, и закиньте туда фотографии",
            reply_markup=keyboard,
        )
    except Exception as e:
        await message.reply(
            "Произошла ошибка, возможно введены неправильно данные. Попробуйте добавить товар снова",
            reply_markup=keyboard,
        )
        logging.warning(e)
    finally:
        await state.clear()


@dp.message(F.text.lower() == "удалить товар")
async def get_id(message: types.Message, state: FSMContext):
    global current_delete
    if message.from_user.id not in ADMINS:
        return
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=KEYBOARD_BACK,
        resize_keyboard=True,
    )
    await state.clear()
    await message.reply(
        "Введите уникальный id товара, который вам необходимо удалить: ",
        reply_markup=keyboard,
    )
    await state.set_state(current_delete.st_delete)


@dp.message(DeleteProduct.st_delete)
async def delete_product(message: types.Message, state: FSMContext):
    global current_delete
    if message.from_user.id not in ADMINS:
        return
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=KEYBOARD_BACK,
        resize_keyboard=True,
    )
    current_delete.id = int(message.text)
    try:
        conn = sql3.connect("product_list.db")
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM product_list WHERE id={current_delete.id}")
        conn.commit()
        await message.reply(
            "Товар с данным id успешно удален. Для корректной работы бота необходимо также удалить папку с таким id на Яндекс Диске",
            reply_markup=keyboard,
        )
    except Exception as e:
        await message.reply(
            "Произошла ошибка, возможно введены неправильно данные. Попробуйте добавить товар снова",
            reply_markup=keyboard,
        )
        logging.warning(e)
    finally:
        await state.clear()


@dp.message(F.text.lower() == "редактировать товар")
async def create_product(message: types.Message, state: FSMContext):
    global current_edit
    if message.from_user.id not in ADMINS:
        return
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=KEYBOARD_BACK,
        resize_keyboard=True,
    )
    await state.clear()
    await message.reply("Введите id товара:", reply_markup=keyboard)
    await state.set_state(current_edit.st_id)


@dp.message(EditProduct.st_id)
async def get_data(message: types.Message, state: FSMContext):
    global current_edit
    if message.from_user.id not in ADMINS:
        return
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=KEYBOARD_BACK,
        resize_keyboard=True,
    )
    current_edit.id = int(message.text)
    await message.reply("Введите новое название товара:", reply_markup=keyboard)
    await state.set_state(current_edit.st_name)


@dp.message(EditProduct.st_name)
async def get_data(message: types.Message, state: FSMContext):
    global current_edit
    if message.from_user.id not in ADMINS:
        return
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=KEYBOARD_BACK,
        resize_keyboard=True,
    )
    current_edit.name = message.text
    await message.reply("Введите новое описание товара: ", reply_markup=keyboard)
    await state.set_state(current_edit.st_description)


@dp.message(EditProduct.st_description)
async def get_data(message: types.Message, state: FSMContext):
    global current_edit
    if message.from_user.id not in ADMINS:
        return
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=KEYBOARD_BACK,
        resize_keyboard=True,
    )
    current_edit.description = message.text
    await message.reply(
        "Введите новый размер товара (если нет поставьте -): ", reply_markup=keyboard
    )
    await state.set_state(current_edit.st_size)


@dp.message(EditProduct.st_size)
async def get_data(message: types.Message, state: FSMContext):
    global current_edit
    if message.from_user.id not in ADMINS:
        return
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=KEYBOARD_BACK,
        resize_keyboard=True,
    )
    current_edit.size = message.text
    await message.reply("Введите новое состояние товара: ", reply_markup=keyboard)
    await state.set_state(current_edit.st_condition)


@dp.message(EditProduct.st_condition)
async def get_data(message: types.Message, state: FSMContext):
    global current_edit
    if message.from_user.id not in ADMINS:
        return
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=KEYBOARD_BACK,
        resize_keyboard=True,
    )
    current_edit.condition = message.text
    await message.reply("Введите новую цену товара: ", reply_markup=keyboard)
    await state.set_state(current_edit.st_price)


@dp.message(EditProduct.st_price)
async def get_data(message: types.Message, state: FSMContext):
    global current_edit
    if message.from_user.id not in ADMINS:
        return
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=KEYBOARD_BACK,
        resize_keyboard=True,
    )
    current_edit.price = message.text
    try:
        conn = sql3.connect("product_list.db")
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE product_list SET name = ? WHERE id=?",
            (
                current_edit.name,
                current_edit.id,
            ),
        )
        cursor.execute(
            f"UPDATE product_list SET description = ? WHERE id=?",
            (
                current_edit.description,
                current_edit.id,
            ),
        )
        cursor.execute(
            f"UPDATE product_list SET size = ? WHERE id=?",
            (
                current_edit.size,
                current_edit.id,
            ),
        )
        cursor.execute(
            f"UPDATE product_list SET condition = ? WHERE id=?",
            (
                current_edit.condition,
                current_edit.id,
            ),
        )
        cursor.execute(
            f"UPDATE product_list SET price = ? WHERE id=?",
            (
                current_edit.price,
                current_edit.id,
            ),
        )
        conn.commit()
        await message.reply("Данные успешно изменены", reply_markup=keyboard)
    except Exception as e:
        await message.reply(
            "Произошла ошибка, возможно введены неправильно данные. Попробуйте добавить товар снова",
            reply_markup=keyboard,
        )
        logging.warning(e)
    finally:
        await state.clear()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        logging.warning("Bot got started")
        asyncio.run(main())
    except Exception as e:
        logging.error(e)

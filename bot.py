import telebot
import os
import pickle
from dotenv import load_dotenv
from datetime import datetime, timedelta
import time

load_dotenv()

TOKEN = os.getenv("TOKEN")
MEMBERSHIP_FEE = float(os.getenv("MEMBERSHIP_FEE"))
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
RECALCULATION_DAY = int(os.getenv("RECALCULATION_DAY"))
recalculation_done = False

bot = telebot.TeleBot(TOKEN)

class User:
    def __init__(self, username, balance=0, last_payment=None, last_update=None):
        self.username = username
        self.balance = balance
        self.last_payment = last_payment
        self.last_update = last_update

def save_users(users):
    with open("db.dat", "wb") as f:
        pickle.dump(users, f)

def load_users():
    if os.path.exists("db.dat") and os.path.getsize("db.dat") > 0:
        with open("db.dat", "rb") as f:
            return pickle.load(f)
    else:
        return {}

def is_admin(chat_id):
    admin_chat_ids = ADMIN_CHAT_ID.split(',')
    return str(chat_id) in admin_chat_ids

def generate_user_id(users):
    max_id = max(users.keys()) if users else 0
    return max_id + 1

def decrease_balance(users, amount):
    for user in users.values():
        user.balance -= amount
    save_users(users)

def get_current_month():
    return datetime.now().month

def recalculate_monthly_fee(users):
    global recalculation_done
    current_day = datetime.now().day
    current_date = datetime.now().date()
    if current_day == RECALCULATION_DAY and not recalculation_done:
        for user in users.values():
            if user.balance > 0:  # Проверяем, что у пользователя есть средства на счету
                user.balance -= MEMBERSHIP_FEE
        save_users(users)
        recalculation_done = True
        # Добавляем текущую дату в качестве даты последнего пересчета для всех пользователей
        for user in users.values():
            user.last_update = current_date
    elif current_day != RECALCULATION_DAY:
        recalculation_done = False



def check_recalculation():
    global recalculation_done
    current_day = datetime.now().day
    current_date = datetime.now().date()
    if current_day == RECALCULATION_DAY and not recalculation_done:
        users = load_users()
        for user in users.values():
            if user.last_update != current_date:  # Проверяем, что последний пересчет не был сегодня
                recalculate_monthly_fee(users)
                recalculation_done = True
                break  # Прерываем цикл после первого пересчета
    elif current_day != RECALCULATION_DAY:
        recalculation_done = False


@bot.message_handler(commands=['get_chat_id'])
def get_chat_id(message):
    chat_id = message.chat.id
    bot.reply_to(message, f"Ваш chat ID: {chat_id}")

@bot.message_handler(commands=['updateusername'])
def update_username(message):
    chat_id = message.chat.id
    if is_admin(chat_id):
        try:
            user_id = int(message.text.split()[1])
            new_username = message.text.split(maxsplit=2)[2]
            users = load_users()
            if user_id in users:
                users[user_id].username = new_username
                save_users(users)
                bot.reply_to(message, f"Имя пользователя с id {user_id} успешно изменено на {new_username}.")
            else:
                bot.reply_to(message, "Пользователь с таким id не найден.")
        except (IndexError, ValueError):
            bot.reply_to(message, "Используйте команду в следующем формате: /updateusername [user_id] [new_username]")
    else:
        bot.reply_to(message, "Эта команда доступна только администраторам.")

@bot.message_handler(commands=['deleteuser'])
def delete_user(message):
    chat_id = message.chat.id
    if is_admin(chat_id):
        try:
            user_id = int(message.text.split()[1])
            users = load_users()
            if user_id in users:
                del users[user_id]
                save_users(users)
                bot.reply_to(message, f"Пользователь с id {user_id} успешно удален.")
            else:
                bot.reply_to(message, "Пользователь с таким id не найден.")
        except (IndexError, ValueError):
            bot.reply_to(message, "Используйте команду в следующем формате: /deleteuser [user_id]")
    else:
        bot.reply_to(message, "Эта команда доступна только администраторам.")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    if is_admin(chat_id):
        bot.reply_to(message, "Привет! Вы администратор клуба. Используйте команды /adduser для добавления нового пользователя, /pay для внесения членского взноса пользовател, /balance для проверки баланса пользователей, /updateusername для изменения имени пользователя, /deleteuser для удаления пользователя.")
    else:
        bot.reply_to(message, "Привет! Я бот клуба. Для использования бота обратитесь к администратору.")

@bot.message_handler(commands=['adduser'])
def add_user(message):
    chat_id = message.chat.id
    if is_admin(chat_id):
        try:
            username = message.text.split()[1]
            users = load_users()
            existing_usernames = [user.username for user in users.values()]
            if username not in existing_usernames:
                user_id = generate_user_id(users)
                users[user_id] = User(username)
                save_users(users)
                bot.reply_to(message, f"Пользователь '{username}' с id {user_id} добавлен в базу данных клуба.")
            else:
                bot.reply_to(message, "Пользователь с таким именем уже существует.")
        except IndexError:
            bot.reply_to(message, "Используйте команду в следующем формате: /adduser [username]")
    else:
        bot.reply_to(message, "Эта команда доступна только администраторам.")

@bot.message_handler(commands=['pay'])
def pay_membership_fee(message):
    chat_id = message.chat.id
    if is_admin(chat_id):
        try:
            user_id = int(message.text.split()[1])
            payment_amount = float(message.text.split()[2])
            users = load_users()
            if user_id in users:
                username = users[user_id].username
                users[user_id].balance += payment_amount
                users[user_id].last_payment = datetime.now()
                users[user_id].last_update = datetime.now()
                save_users(users)

                # Отправляем сообщение каждому администратору
                for admin_chat_id in ADMIN_CHAT_ID.split(','):
                    bot.send_message(admin_chat_id, f"Пользователь {username} с id {user_id} внес сумму в размере {payment_amount}.")

                bot.reply_to(message, f"Сумма в размере {payment_amount} успешно внесена пользователю {username} с id {user_id}.")
            else:
                bot.reply_to(message, "Пользователь с таким id не найден.")
        except (IndexError, ValueError):
            bot.reply_to(message, "Используйте команду в следующем формате: /pay [user_id] [amount]")
    else:
        bot.reply_to(message, "Эта команда доступна только администраторам.")

@bot.message_handler(commands=['balance'])
def check_balance(message):
    chat_id = message.chat.id
    if is_admin(chat_id):
        users = load_users()
        response = "Баланс пользователей:\n"
        for user_id, user in users.items():
            last_payment_date = user.last_payment.strftime("%Y-%m-%d") if user.last_payment else "Никогда"
            response += f"ID: {user_id}, Имя: {user.username}, Баланс: {user.balance}, Дата оплаты: {last_payment_date}\n"
        bot.reply_to(message, response)
    else:
        bot.reply_to(message, "Эта команда доступна только администраторам.")

while True:
    check_recalculation()
    bot.polling()
    time.sleep(360)  # Проверка каждую минуту

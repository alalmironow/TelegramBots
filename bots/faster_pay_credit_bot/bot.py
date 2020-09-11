import threading
import traceback
import telebot

bot = telebot.TeleBot("1375711921:AAHkv6C1n2LO7_IJSKlZAWfE7gltlv4R5y4", parse_mode=None)

HI_MESSAGE = "Привет! Я CreditBot. Я расскажу как быстро ты выплатишь кредит, если будешь платить чуть больше ежемесячного платежа!"
ERROR_MESSAGE = "Укажи корректное значение, пожалуйста"

HOW_MUCH_CREDIT = "Сколько осталось кредита??? (Укажи сумму в рублях)"
HOW_MANY_PERCENT = "Какой процент?"
HOW_MUCH_PAYMENT_SIZE = "По сколько планируешь платить? (с суммой ежемесячного платежа)"

CREDIT_INFO_CLIENTS = {}
CLIENT_LOCKS = {}
GLOBAL_CLIENT_LOCK = threading.Lock()

def lock_client(chat_id):
	client_lock = None
	if not chat_id in CLIENT_LOCKS:
		GLOBAL_CLIENT_LOCK.acquire()
		if not chat_id in CLIENT_LOCKS:
			CLIENT_LOCKS[chat_id] = threading.Lock()
		GLOBAL_CLIENT_LOCK.release()
	client_lock = CLIENT_LOCKS[chat_id] 
	if not client_lock.acquire(False):
		return None	
	return client_lock

def end_stage(chat_id, message_text):
	client_lock = CLIENT_LOCKS[chat_id]

	credit_info = CREDIT_INFO_CLIENTS[chat_id]

	try:
		pay_size = int(message_text)
		if pay_size < 0:
			raise Exception()
	except:
		bot.send_message(chat_id, ERROR_MESSAGE)
		end_stage_1_and_start_stage_2(chat_id)
		return

	credit_size = credit_info['credit_size']
	percent_size = credit_info['percent_size']

	ostatok = credit_size
	count_monthes = 0
	last_pay = 0
	over_pay = 0

	RESULT_MESSAGE = "Получились следующие результаты:\n"
	RESULT_MESSAGE += "Сумма кредита: {} Руб.\n".format(credit_info['credit_size'])
	RESULT_MESSAGE += "Процент: {} %\n".format(credit_info['percent_size'])
	RESULT_MESSAGE += "Платеж: {} Руб/мес\n".format(pay_size)
	bot.send_message(chat_id, RESULT_MESSAGE)
	RESULT_MESSAGE = ""

	while ostatok > 0:
		percents = 30.5 * percent_size / (100 * 365) * ostatok
		over_pay += percents
		ostatok = ostatok + percents - pay_size
		count_monthes += 1

		if ostatok <= 0:
			last_pay = pay_size + ostatok
			ostatok = 0

		if ostatok < credit_size:
			RESULT_MESSAGE += """Месяц {0}: \nпроценты - {1},
			остаток после платежа - {2}, 
			общая переплата - {3}""".format(count_monthes, round(percents, 2), round(ostatok, 2), round(over_pay, 2))
			bot.send_message(chat_id, RESULT_MESSAGE)
			RESULT_MESSAGE = ""

		if ostatok >= credit_size:
			RESULT_MESSAGE += "Такой кредит погасить не успеешь) Либо высокий процент, либо маленький платеж. Долг копится быстрее, чем ты его гасишь"
			bot.send_message(chat_id, RESULT_MESSAGE)
			break

	if ostatok <= 0:
		RESULT_MESSAGE += "Количество месяцев: {0}\n".format(str(count_monthes))
		RESULT_MESSAGE += "Размер последнего платежа: {}\n".format(round(last_pay, 2))
		RESULT_MESSAGE += "Переплата: {}\n".format(round(over_pay, 2))

	bot.send_message(chat_id, RESULT_MESSAGE)
	del CREDIT_INFO_CLIENTS[chat_id]
	del CLIENT_LOCKS[chat_id]
	client_lock.release()


def start_stage_0(chat_id):
	bot.send_message(chat_id, HOW_MUCH_CREDIT)
	CREDIT_INFO_CLIENTS[chat_id] = { 'stage' : 0 }

def end_stage_0_and_start_stage_1(message):
	chat_id = message.chat.id
	message_text = message.text

	try:
		credit_size = int(message_text)
		if credit_size < 0:
			raise Exception()
	except:
		bot.reply_to(message, ERROR_MESSAGE)
		start_stage_0(chat_id)
		return

	CREDIT_INFO_CLIENTS[chat_id]['credit_size'] = credit_size
	CREDIT_INFO_CLIENTS[chat_id]['stage'] = 1
	bot.send_message(chat_id, HOW_MANY_PERCENT)

def end_stage_1_and_start_stage_2(message):
	chat_id = message.chat.id
	message_text = message.text
	credit_info = CREDIT_INFO_CLIENTS[message.chat.id]

	try:
		percent_size = float(message_text)
		if percent_size < 0:
			raise Exception()
	except:
		bot.reply_to(message, ERROR_MESSAGE)
		end_stage_0_and_start_stage_1(message)
		return

	bot.send_message(chat_id, HOW_MUCH_PAYMENT_SIZE)
	credit_info['percent_size'] = percent_size
	credit_info['stage'] = 2

@bot.message_handler(commands=['help'])
def send_welcome(message):
	chat_id = message.chat.id
	client_lock = lock_client(chat_id)
	if not client_lock:
		return

	bot.send_message(chat_id, HI_MESSAGE)
	client_lock.release()

@bot.message_handler(commands=['start'])
def start(message):
	client_lock = lock_client(message.chat.id)
	if not client_lock:
		return

	bot.send_message(message.chat.id, HI_MESSAGE)
	start_stage_0(message.chat.id)
	client_lock.release()

@bot.message_handler(func=lambda m: True)
def handle_message(message):
	chat_id = message.chat.id

	client_lock = lock_client(chat_id)
	if not client_lock:
		return

	if chat_id in CREDIT_INFO_CLIENTS:
		credit_info = CREDIT_INFO_CLIENTS[chat_id]
		stage = credit_info['stage']
		if stage == 0:
			end_stage_0_and_start_stage_1(message)
		elif stage == 1:
			end_stage_1_and_start_stage_2(message)
		elif stage == 2:
			threading.Thread(target = end_stage, args = (chat_id, message.text)).start()
			return
	else:
		start_stage_0(chat_id)
	client_lock.release()


def main():
	print("starting")
	bot.polling()

if __name__ == "__main__":
	main()
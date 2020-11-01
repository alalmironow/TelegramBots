import telebot
import traceback
import pyaudio
import wave
import soundfile as sf
import subprocess
import audioop
import time
import threading
import os

LOCK = threading.Lock()
API_KEY = os.environ["API_TOKEN_2"]

def convert_audio(old_file_name, new_file_name):
	process = subprocess.run(['ffmpeg', '-i', old_file_name, new_file_name])

def send_voice_file(bot, chat_id, file_name):
	voice = None
	try:
		voice = open(file_name, 'rb')
		bot.send_voice(chat_id, voice)
	finally:
		if voice:
			voice.close()


def reverse_audio(old_file_name, new_file_name):
	with wave.open(old_file_name) as fd:
	    params = fd.getparams()
	    frames = fd.readframes(1000000) 

	frames = audioop.reverse(frames, params.sampwidth)

	with wave.open(new_file_name, 'wb') as fd:
	    fd.setparams(params)
	    fd.writeframes(frames)															

bot = telebot.TeleBot(API_KEY, parse_mode=None)

@bot.message_handler(content_types=['voice',])
def handle_message(message):
	global LOCK
	if not LOCK.acquire(False):
		bot.send_message(message.chat.id, "Sorry!!! I am busy...")
		return
	try:
		file_info = bot.get_file(message.voice.file_id)
		downloaded_file = bot.download_file(file_info.file_path)

		file_name = str(time.time())

		with open(file_name + ".ogg", 'wb') as new_file:
			new_file.write(downloaded_file)

		convert_audio(file_name + '.ogg', file_name + '.wav')
		reverse_audio(file_name + '.wav', file_name + "_reverse.wav")
		convert_audio(file_name + "_reverse.wav", file_name + "_reverse.ogg")

		send_voice_file(bot, message.chat.id, file_name + "_reverse.ogg")
		os.remove(file_name + ".ogg")
		os.remove(file_name + ".wav")
		os.remove(file_name + "_reverse.wav")
		os.remove(file_name + "_reverse.ogg")
	except:
		traceback.print_exc()
	finally:
		LOCK.release()

def main():
	print("Starting bot")
	bot.polling()

main()

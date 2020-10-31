#!/bin/bash

python3 /daemon.py /bots/faster_pay_credit_bot/bot.py >> /var/log/telegram_bots.log &
python3 /daemon.py /bots/tennet_audio_bot/bot.py >> /var/log/telegram_bots.log &
tail -f /var/log/telegram_bots.log

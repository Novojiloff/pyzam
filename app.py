import telebot
import schedule
from loguru import logger
import sys
import subprocess
from config import token, chat_id

logger.remove(0)
logger.add(sys.stderr, format="{time:D MMMM YYYY > HH:mm:ss} | {level} | {message}")
bot = telebot.TeleBot(token)
prev_artist = ''
prev_track = ''


def check(artist, track):
    global prev_artist
    global prev_track
    if artist != prev_artist and track != prev_track:
        prev_artist = artist
        prev_track = track
        return True
    return False


def job():
    try:
        text = subprocess.run("pyzam --speaker -j", capture_output=True)
        if text.stdout.decode("windows-1251").split('\r\n')[1] != 'No matches found.':
            artist = eval(text.stdout.decode("windows-1251").split('\r\n')[1]).get('track').get('subtitle')
            track = eval(text.stdout.decode("windows-1251").split('\r\n')[1]).get('track').get('title')
            photo = eval(text.stdout.decode("windows-1251").split('\r\n')[1]).get('track').get('images').get('background')

            if check(artist=artist, track=track):
                caption = f'Исполнитель: <b>{artist}</b>\n\nНазвание трэка: <b>{track}</b>'
                logger.info(f'{artist} - {track}')
                bot.send_photo(chat_id, photo=photo, caption=caption, parse_mode="html")
            else:
                logger.info(f'{artist} - {track}')
        else:
            logger.info('No matches found')
            
    except Exception:
        logger.info('Somthing wrong...')
        pass
    

def main():
    schedule.every(45).seconds.do(job)
    while True:
        schedule.run_pending()


if __name__ == "__main__":
    try:
        logger.info('Started...')
        main()
    except Exception as e:
        logger.error('The program was completed incorrectly')
        logger.error(e)
    except KeyboardInterrupt:
        logger.warning('The program is completed by the user')

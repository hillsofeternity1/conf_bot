#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import os
import urllib.request
import requests
import json
import settings
import re
import time
import threading
import random

from string import punctuation
from urllib.parse import urlencode
from database import DataBase

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.lexers import guess_lexer, get_lexer_by_name
from pygments.styles import get_style_by_name
from pygments.formatters import ImageFormatter


class MessageWorker:
    def __init__(self, db, stop_words='assets/stop-word.ru', settings=settings):
        self.stop_words = stop_words
        self.db = db
        self.telegram_key = settings.parser.get('bot', 'telegram_key')
        self.telegram_api = settings.parser.get('bot', 'telegram_api')
        self.me = self.getMe()
        self.cron_timer()
        print("My name is %s" % self.me['result']['username'])

    def getMe(self):
        url = self.telegram_api + 'bot' + self.telegram_key + '/getMe'
        print(url)
        urllib.request.Request(url)
        request = urllib.request.Request(url)
        raw = urllib.request.urlopen(request).read().decode()
        return json.loads(raw)

    def isTime(self, string):
        try:
            time.strptime(string, '%H%M')
            return string
        except ValueError:
            pass
        try:
            if (int(string[1:]) > 0) and (string[0] == '+') and (len(string[1:]) < 3):
              return string
        except:
            pass
        return False


    def colorize(self, code):
        code_tag = code[code.rfind('#') + 1:]
        try:
            lexer = get_lexer_by_name(code_tag)
            code = code[:code.rfind('#')]
        except:
            lexer = guess_lexer(code)
        print("Lexer is defined as %s" % lexer)
        if lexer.name == 'Text only':
            lexer = get_lexer_by_name('python')
        try:
            highlight(code, lexer, ImageFormatter(
                font_size=16,
                line_number_bg="#242e0c",
                line_number_fg="#faddf2",
                line_number_bold=True,
                font_name='DejaVuSansMono',
                style=get_style_by_name('monokai')), outfile="code.png")
        except Exception as e:
            print(e)
            return e

    def handleUpdate(self, msg):
        try:
            try:
                input_message = msg['message']['text']
                if ('@here' in input_message) or (' @'+self.me['result']['username'] in input_message):
                    if str(msg['message']['chat']['id']) != "-1001233797421":
                        print("@here isn't available for '%s' (%s)" % (msg['message']['chat']['title'], msg['message']['chat']['id']))
                        return
                    conf_id = msg['message']['chat']['id']
                    user_id = msg['message']['from']['id']
                    chat_title = msg['message']['chat']['title']
                    self.db.add_conf(conf_id, chat_title)
                    if msg['message']['text'] != '@here':
                        message = msg['message']['text'].replace('@here', '\n').replace(' @'+self.me['result']['username'], '\n')
                    else:
                        message = """I summon you!\n"""

                    users = self.db.here(
                        user_id=user_id,
                        conf_id=conf_id
                    )
                    for user in users:
                        message += ' [%s](tg://user?id=%s)' % (user[2], user[1])
                    self.send(id=conf_id, msg=message)
                    return True
            
                input_message = msg['message']['text'].replace(
                    '@' + self.me['result']['username'], '')
            except:
                input_message = msg['message']['text']
            if str(msg['message']['chat']['id']) == "-1001233797421":
                if random.randint(0,300) == 1:
                    conf_id = msg['message']['chat']['id']
                    user_id = msg['message']['from']['id']
                    chat_title = msg['message']['chat']['title']
                    self.db.add_conf(conf_id, chat_title)
                    word_aya = self.db.get_random_word(count=1, like="%ая")
                    word_da = self.db.get_random_word(count=1, like="%да")
                    msg = "Ты %s %s." % (word_aya[0][0], word_da[0][0])
                    self.send(id=conf_id, msg=msg)
                if (input_message[0] == 'я') or (input_message[0] == 'Я'):
                    if len(input_message) > 3:
                        conf_id = msg['message']['chat']['id']
                        user_id = msg['message']['from']['id']
                        chat_title = msg['message']['chat']['title']
                        self.db.add_conf(conf_id, chat_title)
                        answers = ['И чо бля?','Да и похуй.','Ну и хуй с тобой.','Нет я.']
                        if random.randint(0,100) > 80:
                            msg = answers[random.randint(0,len(answers)-1)]
                            self.send(id=conf_id, msg=msg)
                if (input_message[0:1] == 'Ты') or (input_message[0:1] == 'ты'):
                    if len(input_message) > 5:
                        conf_id = msg['message']['chat']['id']
                        user_id = msg['message']['from']['id']
                        chat_title = msg['message']['chat']['title']
                        self.db.add_conf(conf_id, chat_title)
                        answers = ['Двачую.','Да.', 'А я покакал.', "Винда лучше."]
                        if random.randint(0,100) > 70:
                            msg = answers[random.randint(0,len(answers)-1)]
                            self.send(id=conf_id, msg=msg)
            if input_message == '/scheme':
                conf_id = msg['message']['chat']['id']
                user_id = msg['message']['from']['id']
                chat_title = msg['message']['chat']['title']
                self.db.add_conf(conf_id, chat_title)
                self.send(id=conf_id, msg='```\n' + self.db.scheme + '\n```')
                return True

            if input_message == '/stat':
                conf_id = msg['message']['chat']['id']
                user_id = msg['message']['from']['id']
                chat_title = msg['message']['chat']['title']
                self.db.add_conf(conf_id, chat_title)

                message = """Here is your top:\n"""
                top = self.db.get_top(
                    user_id=user_id,
                    conf_id=conf_id
                )
                for word in top:
                    message += '*%s*: %s\n' % (word[1], word[0])
                self.send(id=conf_id, msg=message)
                return True

            if input_message == '/reset':
                conf_id = msg['message']['chat']['id']
                user_id = msg['message']['from']['id']
                chat_title = msg['message']['chat']['title']
                self.db.add_conf(conf_id, chat_title)

                message = """Your stat has been resetted."""
                self.db.reset(
                    conf_id=conf_id,
                    user_id=user_id)
                return True

            if input_message[:4] == '/sql':
                conf_id = msg['message']['chat']['id']
                user_id = msg['message']['from']['id']
                chat_title = msg['message']['chat']['title']
                self.db.add_conf(conf_id, chat_title)
                sql = msg['message']['text'][5:]

                res = self.db.command(sql)
                if 'syntax' in str(res) \
                        or 'ambiguous' in str(res):
                    self.send(id=conf_id, msg=str(res))
                    return False
                try:
                    msg = '```\n'
                    for z in res:
                        for i in z:
                            msg = msg + str(i) + '\t'
                        msg = msg + '\n'
                except:
                    msg = res
                self.send(id=conf_id, msg=msg + ' ```')
                return True

            if input_message[:6] == '/alert':
                conf_id = msg['message']['chat']['id']
                user_id = msg['message']['from']['id']
                chat_title = msg['message']['chat']['title']
                self.db.add_conf(conf_id, chat_title)
                msg = msg['message']['text'].split()[1:]
                alert_time = msg[-1].replace(':', '').replace('.', '').replace(' ', '')
                if self.isTime(alert_time):
                    message = " ".join(msg[0:-1])
                    self.db.add_alert(user_id, conf_id, alert_time, message)
                    self.send(id=conf_id, msg='Alert created.')
                return True

            if input_message[:5] == '/code':
# codefunc
                conf_id = msg['message']['chat']['id']
                user_id = msg['message']['from']['id']
                chat_title = msg['message']['chat']['title']
                self.db.add_conf(conf_id, chat_title)
                if len(msg['message']['text'][6:]) < 10000:
                    try:
                        self.colorize(msg['message']['text'][6:])
                    except Exception as e:
                        print(e)
                self.send_img(conf_id)
                return True
        except:
            return False
        try:
            text = msg['message']['text']
            try:
                username = msg['message']['from']['username']
            except:
                username = "_null"
            try:
                last_name = msg['message']['from']['last_name']
            except:
                last_name = '_null'
            try:
                first_name = msg['message']['from']['first_name']
            except:
                first_name = '_null'
            user_id = msg['message']['from']['id']
            chat_id = msg['message']['chat']['id']
            chat_title = msg['message']['chat']['title']
        except:
            return False
        print("[%s] (%s) %s %s %s: %s" % (chat_title, user_id, username, first_name, last_name, text))
        collection = self.clean_text(text)

        self.db.add_user(username,
                         user_id,
                         first_name,
                         last_name)

        self.db.add_conf(chat_id, chat_title)

        for word in collection:
            self.db.add_relation(word=word, user_id=user_id, conf_id=chat_id, text=text)

    def clean_text(self, s):
        file = open(self.stop_words, 'rt')
        sw = file.read().split('\n')
        file.close()
        s = re.sub(
            r'(https?:\/\/)?([\da-z\.-]+)\.([\/\w\.-]*)*\/?\S', '', s, flags=re.MULTILINE)
        # dirty hack with dat fucking file
        fh = open("tmp.txt", "w")
        fh.write(s)
        fh.close()
        cmd = "./assets/mystem -nlwd < tmp.txt"
        ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        output = ps.communicate()[0]
        os.remove("tmp.txt")
        # end of the fuckin' dirty hack
        s = output.decode('utf8')
        s = s.replace('?', '')
        s = s.split('\n')
        collection = []
        for word in s:
            if len(word) > 2:
                if word not in sw:
                    collection.append(word)
                else:
                    pass
            else:
                pass
        return collection

    def send(self, id, msg, parse_mode='Markdown'):
        # print(msg)
        url = self.telegram_api + 'bot' + self.telegram_key + '/sendMessage'
        post_fields = {
            'text': msg,
            'chat_id': id,
            'parse_mode': parse_mode,
            'disable_web_page_preview': 1
        }
        urllib.request.Request(url, urlencode(post_fields).encode())
        request = urllib.request.Request(url, urlencode(post_fields).encode())
        json = urllib.request.urlopen(request).read().decode()
        return json

    def send_img(self, id):
      print('Going to send code.png to %s' % id)
      try:
        url = self.telegram_api + 'bot' + self.telegram_key + '/sendPhoto'
        data = {'chat_id': id}
        files = {'photo': open('code.png', 'rb')}
        r = requests.post(url, files=files, data=data)
        print(r)
      except Exception as e:
        print(e)

    def cron_timer(self):
        alerts = self.db.get_alert()
        for alert in alerts:
            users = self.db.all_conf_users(conf_id=alert[0])
            msg = ""
            for user in users:
                msg += ' [%s](tg://user?id=%s) ' % (user[1], user[2])
            msg += "\nHey all!\n%s" % alert[4]
            self.send(id=alert[0], msg=msg)
        threading.Timer(30, self.cron_timer).start()

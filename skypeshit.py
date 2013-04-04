#!/usr/bin/env python

from datetime import datetime
import random
import settings
import Skype4Py
import sys
import time


class Daemon(object):

    def __init__(self):
        self.log('Hello!')
        self.setup_skype()
        self.my_last_message = 0
        self.target_chats = [self.skype.Chat(name) for name in settings.TARGET_CHATS]

    def random_line(self, filename):
        lines = [line.strip() for line in open(filename).readlines()]
        return random.choice(lines)

    def run(self):
        while True:
            time.sleep(1)
            if self.target_chats:
                message_chance = int(60 * 60 * 24 / len(self.target_chats))
                if random.randint(1, message_chance) == 1:
                    self.send_skype(self.random_line(settings.MESSAGES_FILE), random.choice(self.target_chats))

    def stop(self):
        pass

    def log(self, message, level=0):
        log_levels = {
            0: 'INFO',
            1: 'WARNING',
            2: 'ERROR'
        }
        print '%s [%s] %s' % (
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            log_levels[level],
            message
        )
        sys.stdout.flush()

    def setup_skype(self):
        self.skype = Skype4Py.Skype()
        self.skype.Attach()
        self.skype.OnMessageStatus = lambda *a, **kw: self.on_skype_message(*a, **kw)
        self.log('Attached to Skype')

    def on_skype_message(self, msg, status):
        if status != 'RECEIVED':
            return
        reply_chance = 70
        if time.time() - self.my_last_message < 120:
            reply_chance = 10
        if any([(i in msg.Body.lower()) for i in settings.IRRITATORS]):
            reply_chance = 1
        if random.randint(1, reply_chance) != 1:
            return
        time.sleep(random.randint(0, 20))
        self.send_skype(self.random_line(settings.REPLIES_FILE), msg.Chat)

    def send_skype(self, msg, chat):
        chat.SendMessage(msg)
        self.my_last_message = time.time()
        self.log('Sent: %s' % msg)

if __name__ == '__main__':
    d = Daemon()
    try:
        d.run()
    except KeyboardInterrupt, e:
        d.stop()

import sys
import time
import os
import datetime
import asyncio
from discord_webhook import DiscordWebhook

now = datetime.datetime.now()
date = f"{now.year}-{now.month}-{now.day}_{now.hour}-{now.minute}-{now.second}"

def printlogs():
    logspath = f"logs/{date}.log"
    if not os.path.exists("logs"):
        os.mkdir("logs")
    return open(logspath, "w")

def errorlogs():
    errorspath = f"errors/{date}.log"
    if not os.path.exists("errors"):
        os.mkdir("errors")
    return open(errorspath, "w")

webhook = False # Sends webhooks
printwebhook = 'https://discord.com/api/webhooks/876882825461256233/IV8KxMCVloYK6PlEmfZGUxh45JYCNC5AYgFWGdbgINKTWCPybSh8zEilkkGRqEn_e40R' # Where do you want console prints to be sent to in discord (webhook url)
errorwebhook = '' # Where do you want error prints to be sent in discord (webhook url) | If you wantthe same webhook set errorwebhook = printwebhook
printwebhook_url = 'https://discord.com/api/webhooks/876882825461256233/IV8KxMCVloYK6PlEmfZGUxh45JYCNC5AYgFWGdbgINKTWCPybSh8zEilkkGRqEn_e40R'

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = printlogs()
        self.webhook = webhook
        self.webhook_url = printwebhook_url

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  
        self.log.flush()

        if self.webhook and str(message) != "\n":
            message = str(message)
            content = [message[i:i+2000] for i in range(0, len(message), 2000)]
            for mes in content:
                webhook = DiscordWebhook(url=self.webhook_url, content=mes, username=f"Ham5teak Bot 3.0 | Run {date}")
                webhook.execute()
                time.sleep(1)

    def flush(self):
        self.terminal.flush()
        self.log.flush()
        os.fsync(self.log.fileno())

    def close(self):
        if self.terminal != None:
            sys.stdout = self.terminal
            self.terminal = None

        if self.log != None:
            self.log.close()
            self.log = None

class ErrorLogger(object):
    def __init__(self):
        self.terminal = sys.stderr
        self.log = errorlogs()
        self.webhook = webhook
        self.webhook_url = errorwebhook

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  
        self.log.flush()

        #if self.webhook and str(message) != "\n":
        #  asyncio.sleep(1)
        #  now = datetime.datetime.now()
        #  message = f"**Error in Console** \n```py\n{message}```"
        #  webhook = DiscordWebhook(url=self.webhook_url, content=str(message))
        #  webhook.execute()

    def flush(self):
        self.terminal.flush()
        self.log.flush()
        os.fsync(self.log.fileno())

    def close(self):
        if self.terminal != None:
            sys.stdout = self.terminal
            self.terminal = None

        if self.log != None:
            self.log.close()
            self.log = None

sys.stdout = Logger()
sys.stderr = ErrorLogger()

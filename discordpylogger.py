import sys
import time
import os
import datetime
import asyncio

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
printwebhook = '' # Where do you want console prints to be sent to in discord (webhook url)
errorwebhook = '' # Where do you want error prints to be sent in discord (webhook url) | If you wantthe same webhook set errorwebhook = printwebhook
printwebhook_url = None

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

        #if self.webhook and str(message) != "\n":
        #  sleep(1)
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

        if self.webhook and str(message) != "\n":
          asyncio.sleep(1)
          now = datetime.datetime.now()
          message = f"**Error in Console** \n```py\n{message}```"
          #webhook = DiscordWebhook(url=self.webhook_url, content=str(message))
          #webhook.execute()

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

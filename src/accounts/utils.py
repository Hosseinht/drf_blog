import threading


class SendEmailThread(threading.Thread):
    def __init__(self, email):
        threading.Thread.__init__(self)
        self.email = email

    def run(self):
        self.email.send()

import smtpd 
import asyncore


class TestSMTPServer(smtpd.SMTPServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print('starting server...')

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        pass
        #return super().process_message(peer, mailfrom, rcpttos, data, **kwargs)

if __name__ == "__main__":
    server = TestSMTPServer(('localhost', 25), None)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        print('stopping server')
        server.close()

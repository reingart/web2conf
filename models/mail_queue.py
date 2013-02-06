# coding: utf8

#scheduler = Scheduler(db)

# background mailer, based on:
# http://web2py.com/books/default/chapter/29/8#Sending-messages-using-a-background-task

if MAIL_QUEUE:
    db.define_table('mail_queue',
        Field('status'),
        Field('email'),
        Field('cc', 'list:string'),
        Field('bcc', 'list:string'),
        Field('subject'),
        Field('message', 'text'),
        Field('ts', 'datetime'),
        migrate=migrate, fake_migrate=fake_migrate,
    )
    
    def send(to, subject, message, attachments=None,
             cc=None, bcc=None, reply_to=None, encoding='utf-8', 
             raw=True, headers=None):
         db.mail_queue.insert(
                    status='pending',
                    email=to,
                    cc=cc,
                    bcc=bcc,
                    subject=subject,
                    message=message,
                    )

    # monkey-patch Mail
    mail._send = mail.send
    mail.send = send

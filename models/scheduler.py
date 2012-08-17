# coding: utf8

#scheduler = Scheduler(db)

# background mailer, based on:
# http://web2py.com/books/default/chapter/29/8#Sending-messages-using-a-background-task

if True:
    db.define_table('mail_queue',
        Field('status'),
        Field('email'),
        Field('cc', 'list:string'),
        Field('bcc', 'list:string'),
        Field('subject'),
        Field('message', 'text'),
        Field('ts', 'datetime'),
        migrate=True,
    )

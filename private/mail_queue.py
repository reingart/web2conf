## in file /app/private/mail_queue.py
import time
import datetime
while True:
    rows = db(db.mail_queue.status=='pending').select()
    for row in rows:
        now = datetime.datetime.now()
        if not row.email:
            print now, "UNKNOWN", row.id, row.email
            row.update_record(status='error',ts=now)
        elif mail._send(to=row.email,
            cc=row.cc, bcc=row.bcc,
            subject=row.subject,
            message=row.message):
            print now, "SENT", row.id, row.email
            row.update_record(status='sent',ts=now)
        else:
            print now, "FAILED", row.id, row.email
            row.update_record(status='failed',ts=now)
        db.commit()
    #print "sleeping..."
    time.sleep(60) # check every minute

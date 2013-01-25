# email notification
def notify(subject, text, to=None, cc=None):
    if to is None:
        to = auth.user.email
    info = response.title
    
    # Address person
    addressing = T("Dear attendee")
   
    message = T("""%s:\n%s\n\nPlease do not respond this automated message\n%s""")
    body = message % (addressing, text, info)
    
    result = mail.send(to, subject, body, cc=cc)

    if result:
        return True
    else:
        return False

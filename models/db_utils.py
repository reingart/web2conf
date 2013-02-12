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


def client_side_validate(form, table):
    "Helper to add js validation to forms at browser, based on model table def"
    # add required files:
    response.files.append(URL(r=request,c='static',f='js/jquery.validate.js'))
    response.files.append(URL(r=request,c='static',f='js/jquery.validate.bootstrap.js'))
    # find form fields and check if they are mandatory:
    for tag in form.elements('input, select, textarea'):
        if tag['_name']:
            field = getattr(table, tag['_name'], None)
            # check if the field allows empty values:
            if field and field.requires:
                validators = field.requires if isinstance(field.requires, (list, tuple)) else [field.requires]
                for validator in validators:
                    (value, errors) = validator("")
                    if errors:
                        tag["_class"] = "required"
    # customize submit button (forcing client side validation)
    submit = form.element('input[type=submit]')
    submit["_class"] = "btn btn-primary"
    submit["_onsubmit"] = """$("form").valid()"""
    

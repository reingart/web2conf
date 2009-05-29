def build_invoice(person,donations,fees):
    message=''
    a=' + '.join(['(donation by %s #%s) $%.2f' % item for item in donations if item[2]>0.0])
    b=' + '.join(['(fees&tutorials for %s #%s) $%.2f' % item for item in fees if item[2]>0.0])
    if a and b: message=a+' + '+b
    elif a: message=a
    else: message=b
    try: message=message.decode('latin1').encode('utf8', 'xmlcharrefreplace')
    except: pass
    return message

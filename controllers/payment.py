# -*- coding: utf-8 -*-

#############################################
# Submit payment
#############################################

@auth.requires_login()
def pay():
    rate = request.vars.rate
    if rate:
        cost = ATTENDEE_TYPE_COST[rate]
        db(db.auth_user.id==auth.user.id).update(attendee_type=rate)
        person=db(db.auth_user.id==auth.user.id).select()[0]
        balance=cost
        
        # Not really a payment, it just records the data for further update
        payment_id = db.payment.insert(from_person=auth.user_id,
                                       method="dineromail",
                                       status="new",
                                       invoice=rate,
                                       amount=cost)
    
    payments = db(db.payment.from_person==auth.user_id).select()
    pay=H2(T('No payment due at this time'))
    return dict(person=person,transfers_in=[],
                transfers_out=[],payments=payments,
                pay=pay,balance=balance)


@auth.requires_login()
def invoice():
    return dict(balance=session.balance)

@auth.requires_login()
def dineromail():
    """ Compose a DineroMail purchase request
    and redirect to DineroMail shop feature."""

    payment_id = request.args[0]
    payment = db(db.payment.id==payment_id).select().first()
    
    import uuid
    import urllib

    check_in= \
        PLUGIN_DINEROMAIL_SHOP_CHECK_IN[PLUGIN_DINEROMAIL_COUNTRY]

##https://argentina.dineromail.com/Shop/Shop_Ingreso.asp?NombreItem=Patrocinio+Oro+PyCon+Argentina+2012&TipoMoneda=1&PrecioItem=7500%2E00&E_Comercio=1415311&
##NroItem=PyConAr2012&image_url=http%3A%2F%2Far%2Epycon%2Eorg%2F2012%2Fstatic%2Fimg%2Flogo%5Fdineromail%2Ejpg&
##DireccionExito=http%3A%2F%2F&DireccionFracaso=http%3A%2F%2F&DireccionEnvio=0&Mensaje=1

    arguments= {"NombreItem": payment.invoice,
               "TipoMoneda": "1",
               "PrecioItem": str(payment.amount),
               "E_Comercio": "1415311",
               "NroItem": "PyConAr2012",
               "image_url": "http://ar.pycon.org/2012/static/img/logo_dineromail.jpg",
               "DireccionExito": "http://ar.pycon.org/2012/payment/sucess",
               "DireccionFracaso": "http://ar.pycon.org/2012/payment/failure",
               "DireccionEnvio": "0",
               "Mensaje": "1"}

    url = "%s?" % check_in
    for x, (argument, value) in enumerate(arguments.items()):
        if x == 0:
            url += "%s=%s" % (argument,
                             urllib.quote(value))
        else:
            url += "&%s=%s" % (argument,
                              urllib.quote(value))
    url += "&TRX_ID=%s" % payment_id

    redirect(url)

@auth.requires_login()
def dineromail_update():
    raise HTTP(200, T("Not implemented"))
    form = SQLFORM.factory(Field("starts", "date", default=request.now.date()), Field("ends", "date", default=request.now.date()))
    if form.process().accepted:
        payments = db(db.payment).select()
        for payment in payments:
            # check status and update if needed
            pass
        response.flash = T("Done!")
    return dict(form=form)

@auth.requires_membership("manager")
def checkpayment():
    response.generic_patterns = ["*",]
    payment = request.args[0]
    result = plugin_dineromail_check_status(payment, update=True)
    return dict(result=result)

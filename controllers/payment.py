# -*- coding: utf-8 -*-

class IS_VALID_COUPON(object):
    def __call__(self, value):
        # In development (DEV_TEST), there is no need (and no way) to lock the coupon update
        coupon = db(db.coupon.code==value).select(for_update=not DEV_TEST, limitby=(0, 1)).first()
        if not coupon:
            error_message = T("Coupon does not exist!")
        elif coupon.used_by:
            error_message = T("Coupon is already used!")
        else:
            error_message = None
        return (value, error_message)
    def formatter(self, value):
        return value


@auth.requires_login()
def index():
    "List payment and pay methods"
    q = (db.payment.from_person==auth.user_id) 
    q &= (db.payment.status != "cancelled")

    payments = db(q).select()
    previous_payments = db((db.payment.from_person==auth.user_id) & \
    (db.payment.status != "new")).select()
    return dict(payments=payments,)

        
@auth.requires_login()
def pay():
    "Submit payment"

    if TODAY_DATE<EARLYBIRD_DATE:  ### early registration!
       if auth.user.speaker:
           cost = 'speaker'
       else:
           cost = 'earlybird'
    elif TODAY_DATE<PRECONF_DATE:  ### pre-conference registration!:
        cost = 'preconf'
    else:
        cost = 'general'

    rates = [(rate, "%s (%s): $ %s" % (T(rate), T(cost), prices[cost]))
             for rate, prices
             in sorted(ATTENDEE_TYPE_COST.items(), key=lambda x: x[1][cost])
             if rate is not None
             ]
    form = SQLFORM.factory(
         Field("attendee_type", label=T("Type"), 
                 requires=IS_IN_SET(rates), default=request.vars.rate or "gratis"),
         Field("donation", type="double", 
                 label=T("Additional Donation"), comment=T("(optional)")),
         Field("coupon_code", type="string", length=8,
                 label=T("Coupon code"), comment=T("(discounts)"), 
                 requires=IS_EMPTY_OR(IS_VALID_COUPON())),
         submit_button=T("Confirm"),
         )
    if form.accepts(request.vars, session):
        # book coupon
        if form.vars.coupon_code:
            db(db.coupon.code==form.vars.coupon_code).update(used_by=auth.user_id)
            coupon = db(db.coupon.code==form.vars.coupon_code).select().first()
        else:
            coupon = None
        # calculate payment amount
        rate = form.vars.attendee_type
        amount = ATTENDEE_TYPE_COST[rate][cost]
        if coupon:
            amount -= coupon.discount * amount / 100.00
            amount -= coupon.amount
        if amount <= 0:
            amount = 0
        if form.vars.donation:
            amount += form.vars.donation
        # update user data:
        db(db.auth_user.id==auth.user_id).update(
            attendee_type=rate,           
            donation=form.vars.donation,
            )
        # cancel any pending payment
        q = db.payment.from_person==auth.user_id
        q &= db.payment.status=="new"
        db(q).update(status="cancelled")
        if amount>2:
            status = "new"
        else:
            status = "done"
        # create the payment record
        # Not really a payment, it just records the data for further update
        payment_id = db.payment.insert(from_person=auth.user_id,
                                       rate=rate,
                                       status=status,
                                       invoice="Bono Contribucion PyCon %s (%s)" % (rate, cost),
                                       amount=amount)
    
        # for payment lookup on dineromail notification
        db.payment[payment_id].update_record(order_id=payment_id)
        
        session.flash = T("Your payment has been generated!")
        redirect(URL("index"))
    return dict(form=form)




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

    arguments= {"NombreItem": payment.invoice or '',
               "TipoMoneda": "1",
               "PrecioItem": str(payment.amount),
               "E_Comercio": PLUGIN_DINEROMAIL_ACCOUNT, #"1415311",
               "NroItem": "PyConAr2012",
               "image_url": "http://ar.pycon.org/2012/static/img/logo_dineromail.jpg",
               "DireccionExito": "http://ar.pycon.org/2012/payment/success",
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
    result = None
    def myformat(row):
        try:
            person = db.auth_user[row.from_person]
            from_person = "%s %s" % \
            (person.first_name, person.last_name)
        except (AttributeError, KeyError, ValueError):
            from_person = "?"
        status = row.status
        order = row.order_id
        amount = row.amount
        return "%s - %s (%s) - %s" % \
        (from_person, amount, order, status)
        
    dbset = db((db.payment.status!="Credited")&\
               (db.payment.method=="dineromail")&\
               (db.payment.status!="cancelled")&\
               (db.payment.status!="Cancelled"))
               
    form = SQLFORM.factory(Field("payment",
                                 "reference payment",
                                 requires=IS_IN_DB(dbset,
                                                   db.payment.id,
                                                   myformat)))
    if form.process().accepted:
        payment = form.vars.payment
        result = plugin_dineromail_check_status(payment,
                                                update=True)
    fields = [db.payment.order_id,
              db.payment.from_person,
              db.payment.amount,
              db.payment.invoice]
              
    payments = db(db.payment.status=="Credited").select(*fields)
    return dict(result=result,form=form,payments=payments)

def success():
    session.flash = T("You have successfully finished the payment process. Thanks you.")
    redirect(URL("index"))

def failure():
    session.flash = T("The payment process has failed.")
    redirect(URL("index"))

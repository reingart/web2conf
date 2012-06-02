#############################################
# Submit payment
#############################################

@auth.requires_login()
def pay():
    person=db(db.auth_user.id==auth.user.id).select()[0]
    balance=session.balance
    pay=H2(T('No payment due at this time'))
    return dict(person=person,transfers_in=[],
                transfers_out=[],payments=[],
                pay=pay,balance=balance)

@auth.requires_login()
def cancel_transfer():
    try:
         db((db.money_transfer.id==request.args[0])&(db.money_transfer.to_person==auth.user.id)&(db.money_transfer.approved==False)).delete()
         session.flash=T('Transfer cancelled')
         redirect(URL(r=request,f='pay'))
    except Exception:
         session.flash=T('Invalid operation')
         redirect(URL(r=request,f='pay'))

@auth.requires_login()
def register_other():
    transfers_in=db(db.money_transfer.to_person==auth.user.id).select()
    form=SQLFORM(db.auth_user,fields=['first_name','last_name','email','attendee_type','tutorials','discount_coupon'])
    errors=[]
    due=0.0
    if form.accepts(request.vars,session):
        amount=update_person(form)
        db.money_transfer.insert(from_person=form.vars.id,
                   to_person=auth.user.id,amount=amount,approved=False,
                   description="%s %s (%s) 's Fees transferred to %s %s (%s)" % (form.vars.first_name, form.vars.last_name, form.vars.id, auth.user.first_name,auth.user.last_name,auth.user.id))
        transfers_in=db(db.money_transfer.to_person==auth.user.id).select()
        session.flash=T('Attendee registered and balance transferred')
        redirect(URL(r=request,f='pay'))
    return dict(form=form,transfers_in=transfers_in)

@auth.requires_login()
def pay_check(): return dict()

@auth.requires_login()
def pay_other():
    transfers_in=db(db.money_transfer.to_person==auth.user.id).select()
    form=FORM('Tokens: ',INPUT(_name='codes',requires=IS_NOT_EMPTY()),INPUT(_type='submit'))
    errors=[]
    due=0.0
    if form.accepts(request.vars,session):
        for code in request.vars.codes.split(','):
            try:
                id,pay_token=code.strip().split('-')
                if id==auth.user.id: raise Exception
                if int(id) in [r.from_person for r in transfers_in]: raise Exception
                row=db(db.auth_user.id==id).select()[0]
                if not row.pay_token.upper()==pay_token.upper(): raise Exception                
                amount=max(0.0,row.amount_billed-row.amount_paid)
                db.money_transfer.insert(from_person=row.id,
                        to_person=auth.user.id,amount=amount,approved=False,
                        description="%s %s (%s)'s Fees transferred to %s %s (%s)" % (row.first_name, row.last-name, row.id, auth.user.first_name, auth.user.last_name, auth.user.id))
                transfers_in=db(db.money_transfer.to_person==auth.user.id).select()
            except:
                errors.append(code.strip())
        if not errors:
            session.flash=T('Balance transferred')
            redirect(URL(r=request,f='pay'))
        else:
            response.flash='Invalid Tokens: '+', '.join(errors)
    return dict(form=form,transfers_in=transfers_in)

@auth.requires_login()
def pay_other_info():
    return dict(person=db(db.auth_user.id==auth.user.id).select()[0])

@auth.requires_login()
def invoice():
    return dict(balance=session.balance)

@auth.requires_login()
def dineromail():
    """ Compose a DineroMail purchase request
    and redirect to DineroMail shop feature."""

    import uuid
    import urllib
    
    check_in= \
        PLUGIN_DINEROMAIL_SHOP_CHECK_IN[PLUGIN_DINEROMAIL_COUNTRY]
    
    # Not really a payment, it just records the data for further update
    payment_id = db.payment.insert(from_person=auth.user_id,
                                   method="dineromail",
                                   status="new",
                                   invoice=\
                                   request.vars.NombreItem,
                                   amount=\
                                   float(request.vars.PrecioItem))

    arguments=["NombreItem",
               "TipoMoneda",
               "PrecioItem",
               "E_Comercio",
               "NroItem",
               "image_url",
               "DireccionExito",
               "DireccionFracaso",
               "DireccionEnvio",
               "Mensaje"]

    url = "%s?" % check_in
    for x, argument in enumerate(arguments):
        if x == 0:
            url += "%s=%s" % (argument, 
                             urllib.quote(request.vars[argument]))
        else:
            url += "&%s=%s" % (argument, 
                              urllib.quote(request.vars[argument]))
    url += "&trx_id=%s" % payment_id
    
    redirect(url)

@auth.requires_login()
def dineromail_update():
    form = SQLFORM.factory(Field("starts", "date", default=request.now.date()), Field("ends", "date", default=request.now.date()))
    if form.process().accept:
        payments = db(db.payment).select()
        for payment in payments:
            # check status and update if needed
            pass
        response.flash = T("Done!")
    return dict(form=form)

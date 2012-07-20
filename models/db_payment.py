# -*- coding: utf-8 -*-

if ENABLE_PAYMENTS:
    from gluon.tools import *
    import uuid, datetime, re, os, time, stat
    now=datetime.datetime.now()
    
    ######################################
    ### MANAGE BALANCE TRANSFER
    ######################################
    
    db.define_table('payment',
       db.Field('from_person',db.auth_user),
       db.Field('method',default='Google Checkout'),
       db.Field('amount','double',default=0.0),
       db.Field('order_id',length=64),
       db.Field('status',length=64),
       db.Field('invoice','text'),
       db.Field('created_on','datetime',default=now),
       db.Field('modified_on','datetime',default=now),
        migrate=migrate, fake_migrate=fake_migrate)
    
    db.payment.from_person.requires=IS_IN_DB(db,'auth_user.id','%(first_name)s %(last_name)s [%(id)s]')
    
    db.define_table('money_transfer',
       db.Field('from_person',db.auth_user),
       db.Field('to_person',db.auth_user),
       db.Field('description','text'),
       db.Field('amount','double'),
       db.Field('approved','boolean',default=False),
       db.Field('created_on','datetime',default=now),
       db.Field('modified_on','datetime',default=now),
       db.Field('created_by',db.auth_user),
       migrate=migrate, fake_migrate=fake_migrate)

    db.money_transfer.from_person.requires=IS_IN_DB(db,'auth_user.id','%(first_name)s %(last_name)s [%(id)s]')
    db.money_transfer.to_person.requires=IS_IN_DB(db,'auth_user.id','%(first_name)s %(last_name)s [%(id)s]')

    ######################################
    ### MANAGE COUPONS
    ######################################
    
    db.define_table('coupon',
        db.Field('name', length=64, unique=True, requires=IS_NOT_EMPTY(), default=str(uuid.uuid4())), # yarko;
        db.Field('person','integer',default=None),
        db.Field('comment','text', default='#--- Change this when you distribute: ---#\n To Who:  \nPurpose:  '),
        db.Field('discount','double',default=100.0),
        db.Field('auto_match_registration', 'boolean', default=True),
        migrate=migrate, fake_migrate=fake_migrate)
        
    db.coupon.person.requires=IS_NULL_OR(IS_IN_DB(db,'auth_user.id','%(first_name)s %(last_name)s [%(id)s]'))

    #db.coupon.represent=lambda row: SPAN(row.id,row.name,row.amount,row.description)
    
    ## cleanup:
    ##db(db.payment.created_on<t2.now-datetime.timedelta(1))(db.payment.status.lower()=='pre-processing').delete()
    
    
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


    # Callback: Called when any DineroMail record is updated
    def update_dineromail_payment(data):
    
        payment_data = dict()
        payment_data["id"] = data["client_code"]
        payment_data["from_person"] = db(db.auth_user.email == data["customer_email"]).select().first().id
        payment_data["order_id"] = data["code"]
        payment_data["status"] = PLUGIN_DINEROMAIL_STATUSES[data["status"]]
        payment_data["method"] = "dineromail"
        
        payment = db(db.payment.id == int(payment_data["id"])).select().first()
        
        if payment is not None:
            payment_data["modified_on"] = request.now
            payment.update_record(**payment_data)
        else:
            db.payment.insert(**payment_data)

    # Set dineromail callback on payment notification
    PLUGIN_DINEROMAIL_ON_UPDATE = update_dineromail_payment

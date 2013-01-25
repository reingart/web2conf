# -*- coding: utf-8 -*-

if ENABLE_PAYMENTS:
    from gluon.tools import *
    import uuid, datetime, re, os, time, stat
    now=datetime.datetime.now()

    ######################################
    ### MANAGE BALANCE TRANSFER
    ######################################

    db.define_table('payment',
       db.Field('from_person', db.auth_user, default=auth.user_id),
       db.Field('rate', length=64),
       db.Field('method',default='dineromail'),
       db.Field('amount','double',default=0.0),
       db.Field('order_id',length=64),
       db.Field('status',length=64),
       db.Field('invoice','text'),
       db.Field('created_on','datetime',default=now),
       db.Field('modified_on','datetime',default=now),
        migrate=migrate)

    db.payment.from_person.requires=IS_IN_DB(db,'auth_user.id','%(first_name)s %(last_name)s [%(id)s]')

    ######################################
    ### MANAGE COUPONS
    ######################################

    db.define_table('coupon',
                Field('code',default=str(uuid.uuid4()), unique=True),
                Field('description','text'),
                Field('amount','double'),
                Field('discount','double',default=100.0),
                Field('created_by',db.auth_user,default=auth.user_id, writable=False,),
                Field('created_on','datetime',default=request.now, writable=False,),
                Field('used','boolean',default=False,writable=False,),
                Field('used_by',db.auth_user,default=None, writable=False,),
                Field('used_on','datetime',default=request.now,writable=False,),
                 migrate=migrate)

    ##db.coupon.person.requires=IS_NULL_OR(IS_IN_DB(db,'auth_user.id','%(first_name)s %(last_name)s [%(id)s]'))

    #db.coupon.represent=lambda row: SPAN(row.id,row.name,row.amount,row.description)

    ## cleanup:
    ##db(db.payment.created_on<t2.now-datetime.timedelta(1))(db.payment.status.lower()=='pre-processing').delete()


    # Callback: Called when any DineroMail record is updated
    def update_dineromail_payment(data):
        payment_data = dict()
        payer = db(db.auth_user.email == data["customer_email"]).select().first()
        if payer is not None:
            payment_data["from_person"] = payer.id
        payment_data["order_id"] = data["code"]
        payment_data["status"] = PLUGIN_DINEROMAIL_STATUSES[int(data["status"])]
        payment_data["method"] = "dineromail"
        payment_data["amount"] = data["amount"]

        payment = db(db.payment.order_id == payment_data["order_id"]).select().first()

        if payment is not None:
            payment_data["modified_on"] = request.now
            payment.update_record(**payment_data)
        else:
            db.payment.insert(**payment_data)

    # Set dineromail callback on payment notification
    PLUGIN_DINEROMAIL_ON_UPDATE = update_dineromail_payment

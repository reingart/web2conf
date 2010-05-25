def email_invoice(payment_id,order_id,timestamp,total,person,invoice):
    body=INVOICE_HEADER+"""

    payment_id:  %s
    order_id:    %s
    timestamp:   %s
    total:       %s
    name:        %s %s [#%s]
    address:     %s 
                 %s
                 %s, %s %s (%s)
    email:       %s
    description: %s

""" % (person.first_name,person.last_name,payment_id,order_id,timestamp,total,person.first_name,person.last_name,person.id,person.address1,person.address2,person.city,person.state,person.zip_code,person.country,person.email,invoice)
    mail.send(to=[EMAIL_SENDER,person.email],
              subject='Payment Invoice [%s]' % order_id,
              message=body)

if False and request.function in ['notify','pay']:
    import uuid

    class Level2Controller(gcontroller.Controller):
        def __init__(self,merchant_id,merchant_key,is_sandbox=True,currency='USD'):
            gcontroller.Controller.__init__(self,merchant_id,merchant_key,
                                        is_sandbox,currency)
        def handle_new_order(self, message, order_id, order, context):
            id=int(message.shopping_cart.items[0].merchant_item_id)
            db(db.payment.id==id).update(order_id=order_id,status='SUBMITTED',modified_on=now)
            return gmodel.ok_t()
        def handle_order_state_change(self, message, order_id, order, context):
            if str(message.new_financial_order_state).lower()!='shipped':
                db(db.payment.order_id==order_id).update(status=message.new_financial_order_state,modified_on=now)
            return gmodel.ok_t()
        def handle_charge_amount(self, message, order_id, order, context):
            import datetime
            payment=db(db.payment.order_id==order_id).select()[0]
            payment.update_record(status='CHARGED')
            db((db.money_transfer.to_person==payment.from_person)&\
               (db.money_transfer.created_on<=payment.created_on)).update(approved=True,modified_on=now)
            person=db(db.auth_user.id==payment.from_person).select()[0]
            update_pay(person)
            for other in db(db.money_transfer.to_person==payment.from_person)(db.auth_user.id==db.money_transfer.from_person).select(db.auth_user.ALL): update_pay(other)
            email_invoice(payment.id,order_id,datetime.datetime.now(),payment.amount,person,payment.invoice)
            return gmodel.ok_t()

    l2controller=Level2Controller(GOOGLE_MERCHANT_ID,GOOGLE_MERCHANT_KEY,is_sandbox=GOOGLE_SANDBOX)

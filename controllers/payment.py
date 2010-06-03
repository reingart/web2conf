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
         t2.redirect('pay',flash=T('Transfer cancelled'))
    except Exception:
         t2.redirect('pay',flash=T('Invalid operation'))

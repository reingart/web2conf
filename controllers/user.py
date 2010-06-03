#############################################
# Manage Authentication
#############################################

def login():
    return dict(form=auth.login(next='index',
                                onaccept=lambda form:update_pay(auth.user)))

def verify():
    return auth.verify_email(next=URL(r=request,f='login'))

def register():
    form=auth.register(next='index',
                       onaccept=update_person)
    return dict(form=form)
                
def password():
    return dict(form=auth.retrieve_password(next='login'))
        

@auth.requires_login()
def logout(): auth.logout(next='index')

@auth.requires_login()
def profile():
    you=db.auth_user.id==auth.user.id
    person=db(you).select()[0]
    require_address(person)
    if person.amount_paid>0 or person.amount_subtracted>0:
        db.auth_user.donation_to_PSF.writable=False
        db.auth_user.attendee_type.writable=False
        db.auth_user.discount_coupon.writable=False
    form=crud.update(db.auth_user,auth.user.id,
                     onaccept=update_person,
                     next='index')
    return dict(form=form)

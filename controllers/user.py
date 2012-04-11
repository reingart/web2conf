#############################################
# Manage Authentication
#############################################

crud=Crud(globals(),db)

def index():
    # URL rewrite for backward compatibility (navbar)
    f = request.args[0]
    args = request.args and request.args[1:]
    if f == 'request_reset_password':
        f = 'password'
    redirect(URL(f=f, args=args))

def login():
    return dict(form=auth.login(#next=URL(r=request,c='user',f='profile'),
                                onaccept=lambda form:update_pay(auth.user)))

def janrain():
    from gluon.contrib.login_methods.rpx_account import RPXAccount
    auth.settings.login_form = RPXAccount(request,
        api_key=JANRAIN_API_KEY,
        domain=JANRAIN_DOMAIN,
        language=JANRAIN_LANGUAGE,
        embed=True,
        url = "%s://%s/%s/user/janrain" % (request.env.wsgi_url_scheme, request.env.http_host, request.application))
        
    return dict(form=auth.login(#next=URL(r=request,c='user',f='profile'),
                                onaccept=lambda form:update_pay(auth.user)))

def verify():
    return auth.verify_email(next=URL(r=request,f='login'))

def register():
    form=auth.register(next=URL(r=request,c='default',f='index'),
                       onaccept=update_person)
    return dict(form=form)
                
def change_password():
    redirect(URL(f="password"))
    
def password():
    return dict(form=auth.retrieve_password(next='login'))

def retrieve_username():
    return dict(form=auth.retrieve_username(next='login'))
        

@auth.requires_login()
def logout(): auth.logout(next=URL(r=request,c='default',f='index', args="nocache"))

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
                     next='profile')
    return dict(form=form)


def confirm():
    if len(request.args)==2:
        user_id = request.args[0]
        received_hash = request.args[1]
        q = db.auth_user.id==user_id
        u = db(q).select()[0]
        s= "%s-%s-%s-%s-%s" % (u.last_name, u.first_name, u.email, u.created_by_ip, u.created_on)
        import hashlib
        computed_hash = hashlib.md5(s).hexdigest()
        if computed_hash == received_hash:
            db(q).update(confirmed=True)
            session.flash = T("Confirmed!")
            redirect(URL(c="default", f="index", args="nocache"))
    session.flash = T("Not Confirmed, please enter into your profile and check '%s' field") % T("Confirm attendance")
    redirect(URL(c="user", f="profile"))

#############################################
# Manage Authentication
#############################################

crud=Crud(globals(),db)

def coords_by_address(person):
    import re, urllib
    try:
        address=urllib.quote("%s, %s %s, %s" % (person.city,person.state,person.zip_code,person.country))
        t=urllib.urlopen('http://maps.google.com/maps/geo?q=%s&output=xml'%address).read()
        item=re.compile('\<coordinates\>(?P<la>[^,]*),(?P<lo>[^,]*).*?\</coordinates\>').search(t)
        la,lo=float(item.group('la')),float(item.group('lo'))
        return la,lo
    except Exception, e: 
        #raise RuntimeError(str(e))
        pass
    #raise RuntimeError(str("%s = %s" % (address, t)))
    return 0.0,0.0

def update_zip(person):    
    ### compute zip code
    import shelve,os
    ##if not person.zip_code: return
    """
    code=person.zip_code.strip()[:5]
    if not is_gae:
       zips=shelve.open(os.path.join(request.folder,'private/zips.shelve'))
    if not is_gae and person.country=='United States' and zips.has_key(code):
        la,lo,city,state=zips[code]
    else:
        la,lo=0.0,0.0
    """
    lo,la=coords_by_address(person)
    db(db.auth_user.id==person.id).update(latitude=la, longitude=lo)
    return lo,la

def update_person(form):
    update_zip(form.vars)
    return


# set required field for speakers
if request.function in ('register', 'profile') and 'speaker' in request.args:
    db.auth_user.resume.requires = IS_NOT_EMPTY(T("(required for speakers)"))
    db.auth_user.photo.requires = IS_NOT_EMPTY(T("(required for speakers)"))
    db.auth_user.city.requires = IS_NOT_EMPTY(T("(required for speakers)"))
    db.auth_user.state.requires = IS_NOT_EMPTY(T("(required for speakers)"))
    db.auth_user.country.requires = IS_NOT_EMPTY(T("(required for speakers)"))
    db.auth_user.phone_number.requires = IS_NOT_EMPTY(T("(required for speakers)"))


def index():
    # URL rewrite for backward compatibility (navbar)
    f = request.args and request.args[0] or 'profile'
    args = request.args and request.args[1:]
    if f == 'request_reset_password':
        f = 'password'
    redirect(URL(f=f, args=args))

def create_rpx_login_form(c="user", f="login", embed=False):
    if JANRAIN:
        from gluon.contrib.login_methods.rpx_account import RPXAccount
        return RPXAccount(request,
            api_key=JANRAIN_API_KEY,
            domain=JANRAIN_DOMAIN,
            language=JANRAIN_LANGUAGE,
            embed=embed,
            url="%s://%s/%s/%s/%s" % (
                request.env.wsgi_url_scheme,
                request.env.http_host,
                request.application,
                c, f)), ['token']
    else:
        return None, []

def login():
    from gluon.contrib.login_methods.extended_login_form import ExtendedLoginForm

    alt_login_form, signals = create_rpx_login_form()
            
    if alt_login_form:
        extended_login_form = ExtendedLoginForm(auth, alt_login_form, signals=signals)
        auth.settings.login_form = extended_login_form
    return dict(form=auth.login(#next=URL(r=request,c='user',f='profile'),
                                #onaccept=lambda form:update_pay(auth.user)
                                ))

def janrain():
    alt_login_form, signals = create_rpx_login_form()
    auth.settings.login_form = alt_login_form
    return dict(form=auth.login(next=URL(r=request,c='user',f='profile'),
                                ##onaccept=lambda form:update_pay(auth.user),
                                ))

def verify():
    return auth.verify_email(next=URL(r=request,f='login'))

def register():
    # request captcha only in the registration form:
    if RECAPTCHA_PUBLIC_KEY:
        auth.settings.captcha=Recaptcha(request, RECAPTCHA_PUBLIC_KEY, RECAPTCHA_PRIVATE_KEY)
        # disable email verification (if using captcha)
        auth.settings.registration_requires_verification = False
    
    # don't show janrain if user is filling the form manually:
    if not request.vars:
        alt_login_form, signals = create_rpx_login_form(f="janrain")
    else:
        alt_login_form = signals = None
        
    if (signals and
        any([True for signal in signals if request.vars.has_key(signal)])
       ):
        return alt_login_form.login_form()

    #auth.settings.login_form = self.auth
    form=auth.register(next=URL(r=request,c='default',f='index'),
                       onaccept=update_person)
    #form = DIV(auth())
    if alt_login_form:
        form.components.append(alt_login_form.login_form())
    return dict(form=form)

def change_password():
    redirect(URL(f="password"))

def password():
    return dict(form=auth.retrieve_password(next='login'))

def reset_password():
    response.view="user/password.html"
    return dict(form=auth.reset_password(next=URL(f='profile')))

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


def impersonate():
    user = auth.impersonate(user_id=request.args[0])
    redirect(URL(f="profile"))

@auth.requires_login()
def join_reviewers():
    import datetime
    group_id = auth.id_group('reviewer')
    deadline = REVIEW_DEADLINE_DATE - datetime.timedelta(days=31)
    if TODAY_DATE>deadline:
        session.flash = T("Deadline to join reviewers group was %s" % deadline)
    elif not auth.has_membership(group_id, auth.user_id):
        auth.add_membership(group_id, auth.user_id)
        session.flash = T("Added to Reviewer Group!")
    else:
        session.flash = T("Already in the Reviewer Group!")
    redirect(URL(c='activity', f='proposed'))

from gluon.tools import *
import uuid, datetime, re, os, time, stat
now=datetime.datetime.now()

migrate = True

if is_gae:
    db=GQLDB()
    session.connect(request,response,db=db)
else:
    db=DAL(DBURI)

PAST=datetime.datetime.today()-datetime.timedelta(minutes=1)

#### cleanup sessions
##ps=os.path.join(request.folder,'sessions')
##try: [os.unlink(os.path.join(ps,f)) for f in os.listdir(ps) if os.stat(os.path.join(ps,f))[stat.ST_MTIME]<time.time()-3600]
##except: pass
#### end cleanup sessions

def wysiwyg(field,value):
    return DIV(field.name,TEXTAREA(_name=field.name, _cols="60", value=value, _id="wysiwyg"))


######################################
### PERSON
######################################

db.define_table('auth_user',
    db.Field('first_name',length=128,label=T('First Name')),
    db.Field('last_name',length=128,label=T('Last Name')),
    db.Field('email',length=128),
    db.Field('password','password',default='',label=T('Password'),readable=False),
    db.Field('level','text',label=T('Level'),requires=IS_IN_SET(('principiante','intermedio','avanzado'))),
    db.Field('tutorials','list:string',label=T('Tutorials'),readable=False,writable=False),
    #db.Field('dni','integer'),
    db.Field('certificate','boolean',default=False,label=T('I want a certificate of attendance'),readable=False,writable=False),
    db.Field('address',length=255,label=T('Mailing Address'),default=''),
    db.Field('city',label=T('City'),default=''),
    db.Field('state',label=T('State'),default='Buenos Aires'),
    db.Field('country',label=T('Country'),default='Argentina'),
    db.Field('zip_code',label=T('Zip/Postal Code'),default=''),    
    db.Field('phone_number',label=T('Phone Number')),
    db.Field('include_in_delegate_listing','boolean',default=True,label=T('Include in Delegates List')),
    db.Field('sponsors','boolean',default=True,label=T('Contacto con Auspiciantes'),readable=True,writable=True),
    db.Field('personal_home_page',length=128,label=T('Personal Home Page'),default=''),
    db.Field('company_name',label=T('Company Name'),default=''),
    db.Field('company_home_page',length=128,label=T('Company Home Page'),default=''),
    db.Field('t_shirt_size',label=T('T-shirt Size')),
    db.Field('attendee_type',label=T('Registration Type'),default=ATTENDEE_TYPES[0][0],readable=False,writable=False),
    db.Field('discount_coupon',length=64,label=T('Discount Coupon'), readable=False,writable=False),
    db.Field('donation','double',default=0.0,label=T('Donation to PSF'),readable=False,writable=False),
    db.Field('amount_billed','double',default=0.0,readable=False,writable=False),
    db.Field('amount_added','double',default=0.0,readable=False,writable=False),
    db.Field('amount_subtracted','double',default=0.0,readable=False,writable=False),
    db.Field('amount_paid','double',default=0.0,readable=False,writable=False),
    db.Field('amount_due','double',default=0.0,readable=False,writable=False),
    db.Field('resume','text',label=T('Resume (Bio)'),readable=True,writable=True),
    db.Field('photo','upload',label=T('Photo'),readable=True,writable=True),
    db.Field('cv','upload',label=T('CV'),readable=True,writable=True),
    db.Field('speaker','boolean',default=False,readable=False,writable=False),
    db.Field('session_chair','boolean',default=False,readable=False,writable=False),
    db.Field('manager','boolean',default=False,readable=False,writable=False),
    db.Field('reviewer','boolean',default=True,readable=False,writable=False),
    db.Field('latitude','double',default=0.0,readable=False,writable=False),
    db.Field('longitude','double',default=0.0,readable=False,writable=False),
    db.Field('confirmed','boolean',default=False,writable=True,readable=True),
    db.Field('registration_key',length=64,default='',readable=False,writable=False),
    db.Field('created_by_ip',readable=False,writable=False,default=request.client),
    db.Field('created_on','datetime',readable=False,writable=False,default=request.now),
    db.Field('cena_viernes','boolean', comment="-con cargo-"),
    db.Field('cena_sabado','boolean', comment="sin cargo para los disertantes + organizadores"),
    db.Field('cena_obs','string', comment="indique si quiere invitar a la cena a familiares o amigos (cant. de reservas) -con cargo-"),
    format="%(last_name)s, %(first_name)s (%(id)s)",
    migrate=migrate)

db.auth_user.first_name.comment=T('(required)')
db.auth_user.last_name.comment=T('(required)')
db.auth_user.email.comment=T('(required)')
db.auth_user.password.comment=T('(required)')
db.auth_user.resume.widget=lambda field,value: SQLFORM.widgets.text.widget(field,value,_cols="10",_rows="8")
db.auth_user.photo.comment=T('Your picture (for authors)')
#db.auth_user.dni.comment=T('(required if you need a certificate)')
#db.auth_user.certificate.comment=XML(A(str(T('El Costo de Certificado es $x.-')) + '[2]',_href='#footnote2'))
db.auth_user.t_shirt_size.requires=IS_IN_SET(T_SHIRT_SIZES,T_SHIRT_SIZES_LABELS)
db.auth_user.t_shirt_size.comment='Si desea remera, seleccione tamaño (el precio es $ 50.)'

db.auth_user.level.comment="Conocimiento de Python, para organización"

db.auth_user.zip_code.comment=T('(also used for attendee mapping)')

db.auth_user.company_name.comment=T('corporation, university, user group, etc.')

db.auth_user.sponsors.comment=XML(A(str(T('Desmarcar si no desea que los Auspiciantes de la conferencia tengan acceso a sus datos de contacto')) + '[1]',_href='#footnote1'))
#db.auth_user.include_in_delegate_listing.comment=T('If checked, your Name, Company and Location will be displayed publicly')
db.auth_user.include_in_delegate_listing.comment=XML(A(str(T('If checked, your Name, Company and Location will be displayed publicly')) + '[1]',_href='#footnote1'))
db.auth_user.resume.comment=T('Short Biography and references (for authors)')

db.auth_user.cv.comment=T('If you want you can upload your CV to be available to our Sponsors in further laboral searchs:')

db.auth_user.first_name.requires=[IS_LENGTH(128),IS_NOT_EMPTY()]
db.auth_user.last_name.requires=[IS_LENGTH(128),IS_NOT_EMPTY()]

auth=Auth(globals(),db)                      # authentication/authorization

db.auth_user.password.requires=CRYPT(auth.settings.hmac_key)

auth.settings.table_user=db.auth_user
auth.define_tables()
auth.settings.login_url=URL(r=request,c='user',f='login')
auth.settings.on_failed_authorization=URL(r=request,c='user',f='login')
auth.settings.logout_next=URL(r=request,c='default',f='index')
auth.settings.register_next=URL(r=request,c='default',f='index')
auth.settings.verify_email_next=URL(r=request,c='default',f='index')
auth.settings.profile_next=URL(r=request,c='user',f='profile')
auth.settings.retrieve_password_next=URL(r=request,c='user',f='login')
auth.settings.change_password_next=URL(r=request,c='default',f='index')
auth.settings.logged_url=URL(r=request,c='user',f='profile')
auth.settings.create_user_groups = False

if EMAIL_SERVER:
    mail=Mail()                                  # mailer
    mail.settings.server=EMAIL_SERVER
    mail.settings.sender=EMAIL_SENDER
    mail.settings.login=EMAIL_AUTH
    auth.settings.mailer=mail                    # for user email verification
    auth.settings.registration_requires_verification = EMAIL_VERIFICATION
    auth.messages.verify_email_subject = EMAIL_VERIFY_SUBJECT
    auth.messages.verify_email = EMAIL_VERIFY_BODY
    
if RECAPTCHA_PUBLIC_KEY:
    auth.setting.captcha=Recaptcha(request,RECAPTCHA_PUBLIC_KEY,RECAPTCHA_PRIVATE_KEY)
auth.define_tables()

db.auth_membership.user_id.represent=lambda v: "%(last_name)s, %(first_name)s (%(id)s)" % db.auth_user[v]

def require_address(person=None):
    try:
        if (request.vars.donation_to_PSF \
           and float(request.vars.donation_to_PSF)!=0.0)\
           or (person and person.donation_to_PSF):
            db.auth_user.address1.requires.append(IS_NOT_EMPTY())
            db.auth_user.city.requires.append(IS_NOT_EMPTY())
            db.auth_user.state.requires.append(IS_NOT_EMPTY())
            db.auth_user.zip_code.requires.append(IS_NOT_EMPTY())
    except: pass
require_address()

db.auth_user.email.requires=[IS_LENGTH(128),IS_EMAIL(),IS_NOT_IN_DB(db,'auth_user.email')]
db.auth_user.password.requires=[IS_NOT_EMPTY(),CRYPT()]
db.auth_user.personal_home_page.requires=[IS_LENGTH(128),IS_NULL_OR(IS_URL())]
db.auth_user.company_home_page.requires=[IS_LENGTH(128),IS_NULL_OR(IS_URL())]
db.auth_user.country.requires=IS_IN_SET(COUNTRIES)
db.auth_user.created_by_ip.requires=\
    IS_NOT_IN_DB(db(db.auth_user.created_on>PAST),'auth_user.created_by_ip')
db.auth_user.registration_key.default=str(uuid.uuid4())

db.auth_user.reviewer.writable=db.auth_user.reviewer.readable=auth.has_membership('manager')
db.auth_user.speaker.writable=db.auth_user.speaker.readable=auth.has_membership('manager')

# Enable tutorial selection after proposal deadline
db.auth_user.tutorials.writable = db.auth_user.tutorials.readable = TODAY_DATE>PROPOSALS_DEADLINE_DATE
db.auth_user.tutorials.label = "Charlas Preferidas"

# Enable simplified registration (no password asked)
if SIMPLIFIED_REGISTRATION and TODAY_DATE>REVIEW_DEADLINE_DATE and request.controller=='user' and request.function=='register':
    db.auth_user.password.readable = False
    db.auth_user.password.writable = False
    db.auth_user.confirmed.default = True
else:
    db.auth_user.confirmed.default = False
    db.auth_user.confirmed.readable = True
    db.auth_user.confirmed.writable = True
    
db.auth_user.confirmed.label = T("Confirm attendance")

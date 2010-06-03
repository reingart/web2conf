from gluon.tools import *
import uuid, datetime, re, os, time, stat
now=datetime.datetime.now()
exec('from applications.%s.modules.t2 import T2, COUNTRIES' % request.application)

migrate = True

if is_gae:
    db=GQLDB()
    session.connect(request,response,db=db)
else:
    db=SQLDB(DBURI)

PAST=datetime.datetime.today()-datetime.timedelta(minutes=1)

#### cleanup sessions
ps=os.path.join(request.folder,'sessions')
try: [os.unlink(os.path.join(ps,f)) for f in os.listdir(ps) if os.stat(os.path.join(ps,f))[stat.ST_MTIME]<time.time()-3600]
except: pass
#### end cleanup sessions

def wysiwyg(field,value):
    return DIV(field.name,TEXTAREA(_name=field.name, _cols="70", value=value, _id="wysiwyg"))


######################################
### PERSON
######################################

db.define_table('auth_user',
    db.Field('first_name',length=128,label=T('First Name')),
    db.Field('last_name',length=128,label=T('Last Name')),
    db.Field('email',length=128),
    db.Field('password','password',default='',label=T('Password'),readable=False,writable=True),
    db.Field('dni','integer'),
    db.Field('certificate','boolean',default=False,label=T('I want a certificate of attendance')),
    db.Field('address',length=255,label=T('Mailing Address'),default=''),
    db.Field('city',label=T('City'),default='San Luis'),
    db.Field('state',label=T('State'),default='San Luis'),
    db.Field('country',label=T('Country'),default='Argentina'),
    db.Field('zip_code',label=T('Zip/Postal Code'),default=''),    
    db.Field('phone_number',label=T('Phone Number')),
    db.Field('include_in_delegate_listing','boolean',default=True,label=T('Include in Delegates List')),
    db.Field('personal_home_page',length=128,label=T('Personal Home Page'),default=''),
    db.Field('company_name',label=T('Company Name'),default=''),
    db.Field('company_home_page',length=128,label=T('Company Home Page'),default=''),
    db.Field('attendee_type',label=T('Registration Type'),default=ATTENDEE_TYPES[0][0],readable=False,writable=False),
    db.Field('discount_coupon',length=64,label=T('Discount Coupon'), readable=False,writable=False),
    db.Field('donation','double',default=0.0,label=T('Donation to PSF'),readable=False,writable=False),
    db.Field('tutorials','text',label=T('Tutorials'),readable=False,writable=False),
    db.Field('amount_billed','double',default=0.0,readable=False,writable=False),
    db.Field('amount_added','double',default=0.0,readable=False,writable=False),
    db.Field('amount_subtracted','double',default=0.0,readable=False,writable=False),
    db.Field('amount_paid','double',default=0.0,readable=False,writable=False),
    db.Field('amount_due','double',default=0.0,readable=False,writable=False),
    db.Field('resume','text',label=T('Resume (Bio)'),readable=True,writable=True),
    db.Field('cv','upload',label=T('CV'),readable=True,writable=True),
    db.Field('speaker','boolean',default=False,readable=False,writable=False),
    db.Field('session_chair','boolean',default=False,readable=False,writable=False),
    db.Field('manager','boolean',default=False,readable=False,writable=False),
    db.Field('reviewer','boolean',default=True,readable=False,writable=False),
    db.Field('latitude','double',default=0.0,readable=False,writable=False),
    db.Field('longitude','double',default=0.0,readable=False,writable=False),
    db.Field('registration_key',length=64,default='',readable=False,writable=False),
    db.Field('created_by_ip',readable=False,writable=False,default=request.client),
    db.Field('created_on','datetime',readable=False,writable=False,default=request.now),
    migrate=migrate)

db.auth_user.first_name.comment=T('(required)')
db.auth_user.last_name.comment=T('(required)')
db.auth_user.email.comment=T('(required)')
db.auth_user.password.comment=T('(required)')

db.auth_user.dni.comment=T('(required if you need a certificate)')
db.auth_user.certificate.comment=XML(A(str(T('El Costo de Certificado es $x.-')) + '[2]',_href='#footnote2'))

db.auth_user.zip_code.comment=T('(also used for attendee mapping)')

db.auth_user.company_name.comment=T('corporation, university, user group, etc.')

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
auth.settings.profile_next=URL(r=request,c='default',f='index')
auth.settings.retrieve_password_next=URL(r=request,c='user',f='login')
auth.settings.change_password_next=URL(r=request,c='default',f='index')

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


t2=T2(request,response,session,cache,T,db)

crud=Crud(globals(),db)

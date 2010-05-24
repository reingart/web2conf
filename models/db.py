from gluon.tools import *
import uuid, datetime, re, os, time, stat
now=datetime.datetime.now()
exec('from applications.%s.modules.t2 import T2, COUNTRIES' % request.application)
##exec('import applications.%s.modules.gchecky.model as gmodel' % request.application)
##exec('import applications.%s.modules.gchecky.controller as gcontroller' % request.application)

migrate = False

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


######################################
### PERSON
######################################

db.define_table('auth_user',
    db.Field('first_name',length=128,label=T('First Name')),
    db.Field('last_name',length=128,label=T('Last Name')),
    db.Field('email',length=128),
    db.Field('password','password',default=REGISTRATION_PASSWORD,label=T('Password'),writable=(REGISTRATION_PASSWORD==""),readable=False),
    db.Field('address',length=255,label=T('Mailing Address'),default=''),
    db.Field('city',label=T('City'),default=''),
    db.Field('state',label=T('State'),default='Buenos Aires'),
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
    db.Field('installfest_os','string',label=T('InstallFest Operating System'),default="(no necesito instalación)"),
    db.Field('installfest_hardware','text',label=T('InstallFest Hardware')),
    db.Field('resume','text',label=T('Resume (CV)'),readable=False,writable=False),
    db.Field('speaker','boolean',default=False,readable=False,writable=False),
    db.Field('session_chair','boolean',default=False,readable=False,writable=False),
    db.Field('manager','boolean',default=True,readable=False,writable=False),
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
db.auth_user.password.comment=T('new for this site (required)')

db.auth_user.zip_code.comment=T('(also used for attendee mapping)')

db.auth_user.company_name.comment=T('corporation, university, user group, etc.')

db.auth_user.include_in_delegate_listing.comment=T('If checked, your Name, Company and Location will be displayed publicly')
db.auth_user.resume.comment=T('Short Biography and references (for authors)')

db.auth_user.installfest_os.requires=IS_IN_SET(['(no necesito instalación)', 'Ubuntu','Debian','ArchLinux','OpenSolaris'])
db.auth_user.installfest_os.comment=XML(str(T('Seleccionar la distribución que desea instalar (ver %s)',A('[1]',_href='#footnote1'))))
db.auth_user.installfest_hardware.comment=T('Detallar un inventario del equipo, a efectos del ingreso al recinto y facilitar la instalación. Incluir: Placa de red, video, sonido, módem (marcas, modelos, configuración); CPU (Procesador); Memoria RAM')

db.auth_user.first_name.requires=[IS_LENGTH(128),IS_NOT_EMPTY()]
db.auth_user.last_name.requires=[IS_LENGTH(128),IS_NOT_EMPTY()]

##db.auth_user.accept_conditions.comment=XML(str(T('(see %s)',A('[1]',_href='#footnote1'))))
db.auth_user.city.comment=XML(str(T('(see %s)',A('[2]',_href='#footnote2'))))

auth=Auth(globals(),db)                      # authentication/authorization

auth.settings.table_user=db.auth_user
auth.define_tables()
auth.settings.login_url=URL(r=request,c='default', f='login')
auth.settings.verify_email_next = URL(r=request,c='default', f='index')
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
    migrate=migrate)

db.payment.from_person.requires=IS_IN_DB(db,'auth_user.id','%(name)s [%(id)s]')

db.define_table('money_transfer',
   db.Field('from_person',db.auth_user),
   db.Field('to_person',db.auth_user),
   db.Field('description','text'),
   db.Field('amount','double'),
   db.Field('approved','boolean',default=False),
   db.Field('created_on','datetime',default=now),
   db.Field('modified_on','datetime',default=now),
   db.Field('created_by',db.auth_user),
   migrate=migrate)

db.money_transfer.from_person.requires=IS_IN_DB(db,'auth_user.id','%(name)s [%(id)s]')
db.money_transfer.to_person.requires=IS_IN_DB(db,'auth_user.id','%(name)s [%(id)s]')

######################################
### MANAGE COUPONS
######################################

db.define_table('coupon',
    db.Field('name', length=64, unique=True, requires=IS_NOT_EMPTY(), default=str(uuid.uuid4())), # yarko;
    db.Field('person','integer',default=None),
    db.Field('comment','text', default='#--- Change this when you distribute: ---#\n To Who:  \nPurpose:  '),
    db.Field('discount','double',default=100.0),
    db.Field('auto_match_registration', 'boolean', default=True),
    migrate=migrate)
db.coupon.person.requires=IS_NULL_OR(IS_IN_DB(db,'auth_user.id','%(name)s [%(id)s]'))

#db.coupon.represent=lambda row: SPAN(row.id,row.name,row.amount,row.description)

def wysiwyg(field,value):
    return DIV(field.name,TEXTAREA(_name=field.name, _cols="70", value=value, _id="wysiwyg"))


######################################
### MANAGE TALKS
######################################

db.define_table('talk',
    db.Field('authors',label=T("Authors"),default=('%s %s' %(auth.user.first_name, auth.user.last_name)) if auth.user else None),
    db.Field('title',label=T("Title")),
    db.Field('duration','integer',label=T("Duration"),default=60),
    db.Field('cc',label=T("cc"),length=512),
    db.Field('abstract','text',label=T("Abstract")),
    db.Field('description','text',label=T("Description"),widget=wysiwyg),
    db.Field('categories','text',label=T("Categories")),
    db.Field('level','text',label=T("Level")),
    db.Field('scheduled_datetime','datetime',label=T("Scheduled Datetime"),writable=False,readable=False),
    db.Field('status',default='pending',label=T("Status"),writable=False,readable=False),
    db.Field('score','double',label=T("Score"),default=None,writable=False),
    db.Field('created_by','integer',label=T("Created By"),writable=False,default=auth.user.id if auth.user else 0),
    db.Field('created_on','datetime',label=T("Created On"),writable=False,default=request.now),
    db.Field('created_signature',label=T("Created Signature"),writable=False,
             default=('%s %s' % (auth.user.first_name,auth.user.last_name)) if auth.user else ''),
    db.Field('modified_by','integer',label=T("Modified By"),writable=False,default=auth.user.id if auth.user else 0),
    db.Field('modified_on','datetime',label=T("Modified On"),writable=False,default=request.now,update=request.now),
    migrate=migrate)

db.talk.description.display=lambda value: XML(value)
db.talk.title.requires=IS_NOT_IN_DB(db,'talk.title')
db.talk.authors.requires=IS_NOT_EMPTY()
db.talk.status.requires=IS_IN_SET(['pending','accepted','rejected'])
db.talk.level.requires=IS_IN_SET(TALK_LEVELS)
db.talk.abstract.requires=IS_NOT_EMPTY()
db.talk.description.requires=IS_NOT_EMPTY()
db.talk.categories.widget=lambda s,v:T2.tag_widget(s,v,TALK_CATEGORIES)
db.talk.displays=db.talk.fields
db.talk.represent=lambda talk: \
   A('[%s] %s' % (talk.status,talk.title),
     _href=URL(r=request,f='display_talk',args=[talk.id]))

db.define_table('talk_archived',db.talk,db.Field('parent_talk',db.talk), migrate=migrate)

#### yarko ---< F/A (financial aid) forms >----
db.define_table( 'fa',
   # Idendtification:
   # - Legal name => fa.person.first_name + fa.person.last_name
   # - Address => fa.person.{address1,address2,city,state,country,zip_code}
   # - email address => fa.person.email
   # Registration:
   # - registration type => fa.percon.attendee_type
   db.Field( 'person', db.auth_user ),
   db.Field('created_on','datetime'),
   db.Field('modified_on','datetime',default=now),
   db.Field( 'registration_amount', 'double', default='0.00'),
   # Hotel Cost:
   # - number of nights of assitance requested;
   db.Field( 'hotel_nights', 'integer', default=0 ),
   # - total amount requested; label:  "Max 50% of room rate at Crowne Plaza x # nights;" labeled; validated if easy to update room rates.
   db.Field( 'total_lodging_amount', 'double', default='0.00'),
   db.Field( 'roommates', 'string', length=128, default=''),
   # Transportation:
   # - method of transportation / details;
   # db.Field( 'method_of_transportation', 'string', default=''),
   db.Field( 'transportation_details', 'text', default=''),
   # - total amount requested; label: "If you want assistance with your transportation costs, please provide a rough estimate (to nearest US$100)
   #       of how much a round-trip will cost.  Please update your request once final cost is known."
   db.Field( 'transportation_amount', 'double', default='0.00', ),
   # Total:  - read-only field calculated from above 3 sections
   # - registration dollar amount requested; (let applicant specify, as they can ask for just a portion)
   db.Field( 'total_amount_requested', 'double', default='0.0'), # default = ATTENDEE_TYPE_COST[person.attendee_type]),
   #
   # Additional fileds:
   # - minimum at. requested; label "In addition to the desired amount, state the minimum amount of aid you require, below
   #  which you will not be able to attend PyCon.  If we are unable to allocate this minumum amount, we will decline your application
   #  and allocate the funds to others."
   db.Field( 'minimum_amount_requested', 'double', default='0.00', ),
   # - Rational " State why you should come to PyCon, and what you will be doing.
   #    We don't need an essay, but please provide a few sentences of explanation.
   #   Priority will be given to people who make significant contributions to PyCon
   #   and the Python community (e.g. students working on a task, conference speakers,
   #   sprint leaders, developers critical to a sprint, super-enthusiastic sprint newbies
   #   who will give 110% for their project, or people doing public service work with Python)."
   db.Field( 'rationale', 'text', default='' ),
   migrate=migrate)

db.fa.person.requires=IS_IN_DB(db,'auth_user.id','%(name)s [%(id)s]')

db.fa.registration_amount.comment= XML(str(T('(%s)',A('instructions',_href='#registration_amount'))))
db.fa.hotel_nights.comment= XML(str(T('(%s)',A('instructions',_href='#hotel_nights'))))
db.fa.total_lodging_amount.comment= XML(str(T('(%s)',A('instructions',_href='#total_lodging'))))
db.fa.roommates.comment= XML(str(T('(%s)',A('instructions',_href='#roommates'))))
db.fa.transportation_details.comment= XML(str(T('(%s)',A('instructions',_href='#transportation'))))
db.fa.transportation_amount.comment= XML(str(T('(%s)',A('instructions',_href='#transportation_amt'))))
db.fa.total_amount_requested.comment= XML(str(T('(%s)',A('instructions',_href='#total_amt'))))
db.fa.minimum_amount_requested.comment= XML(str(T('(%s)',A('instructions',_href='#min_amt'))))
db.fa.rationale.comment= XML(str(T('(%s)',A('instructions',_href='#rationale'))))
#### ---< END: F/A forms >---

#### end fixup
######
# include and customize t2
######

t2=T2(request,response,session,cache,T,db)

db.define_table( 'expense_form',
    db.Field( 'person', db.auth_user ),
    db.Field( 'event','string', length=20, default='PyCon 09'),
    db.Field( 'created_on','datetime'),
    migrate=migrate,
)

db.expense_form.person.requires=IS_IN_DB(db,'auth_user.id','%(name)s [%(id)s]')

db.define_table( 'expense_item',
    db.Field( 'exp_form', db.expense_form ),
    db.Field( 'seq', 'integer', ),
    db.Field( 'receipt_no', 'integer', default=1 ),
    db.Field( 'receipt_item', 'integer', default=1 ),
    db.Field( 'acct_code','string', length=20, default='video'),
    db.Field( 'description', 'text', default='' ),
    db.Field( 'serial_no', 'string', length=30, default='' ),
    db.Field( 'location', 'text', default='' ),
    db.Field( 'amount', 'double', default='0.00'),
    migrate=migrate)

db.expense_item.exp_form.requires=IS_IN_DB(db,'expense_form.person','%(id)s')

crud=Crud(globals(),db)

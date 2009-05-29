from gluon.tools import *
import uuid, datetime, re, os, time, stat
now=datetime.datetime.now()
exec('from applications.%s.modules.t2 import T2, COUNTRIES' % request.application)
exec('import applications.%s.modules.gchecky.model as gmodel' % request.application)
exec('import applications.%s.modules.gchecky.controller as gcontroller' % request.application)

if is_gae:
    db=GQLDB()
    session.connect(request,response,db=db)
else:
    db=SQLDB(DBURI,pools=DBPOOLS)

PAST=datetime.datetime.today()-datetime.timedelta(minutes=1)

#### cleanup sessions
ps=os.path.join(request.folder,'sessions')
try: [os.unlink(os.path.join(ps,f)) for f in os.listdir(ps) if os.stat(os.path.join(ps,f))[stat.ST_MTIME]<time.time()-3600]
except: pass
#### end cleanup sessions


#### redefine IS_IN_SET to make many2many work with version 1.55.3, not required in trunk and 1.56
class IS_IN_SET3:
    def __init__(self, theset, labels=None, error_message='value not allowed!',multiple=False,person_id=0):
        self.multiple=multiple
        self.theset = [str(item) for item in theset]
        if isinstance(theset,dict): self.labels=theset.values()
        else: self.labels=labels
        self.error_message = error_message
        self.person_id=person_id
    def options(self):
        if not self.labels:
            return [(k, k) for i, k in enumerate(self.theset)]
        return [(k, self.labels[i]) for i, k in enumerate(self.theset)]
    def __call__(self, value):
        if self.multiple:
            values=re.compile("[\w\-:]+").findall(str(value))
            if len([x[0] for x in values if x[0]=='1'])>1 or \
               len([x[0] for x in values if x[0]=='2'])>1 or \
               len([x[0] for x in values if x[0]=='3'])>1 or \
               len([x[0] for x in values if x[0]=='4'])>1:
                return (value,T('You can only choose one tutorial per each session'))
        else: values=[value]
        for item in values:
            m=db(db.auth_user.id!=self.person_id)(db.auth_user.tutorials.like('%%|%s|%%'%item)).count()
            if m>=TUTORIALS_CAPS[item]: return (value, "%s is full" % TUTORIALS[item])
        failures=[x for x in values if not x in self.theset]
        if failures: return (value, self.error_message)
        if self.multiple: return ('|%s|'%'|'.join(values),None)
        return (value, None)
### end redefine IS_IN_DB

### workaroud a bug in 1.55.2
def password_widget(field,value):
    id='%s_%s' % (field._tablename,field.name)
    if value: value='********'
    return INPUT(_type='password', _id=id,
                      _name=field.name,_value=value,_class=field.type,
                      requires=field.requires)
###

######################################
### PERSON
######################################

db.define_table('auth_user',
    db.Field('first_name',length=128,label=T('First Name')),
    db.Field('last_name',length=128,label=T('Last Name')),
    db.Field('email',length=128),
    db.Field('password','password',default='',widget=password_widget,readable=False),
    db.Field('address1',length=128,label=T('Mailing Address Line 1'),default=''),
    db.Field('address2',length=128,label=T('Mailing Address Line 2'),default=''),
    db.Field('city',label=T('City'),default=''),
    db.Field('state',label=T('State'),default=''),
    db.Field('country',default=''),
    db.Field('zip_code',label=T('Zip/Postal Code'),default=''),
    db.Field('phone_number',label=T('Phone Number')),
    db.Field('badge_line1',label=T('Badge Line 1'),default=''),
    db.Field('badge_line2',label=T('Badge Line 2'),default=''),
    db.Field('personal_home_page',length=128,label=T('Personal Home Page'),default=''),
    db.Field('company_name',label=T('Company Name'),default=''),
    db.Field('company_home_page',length=128,label=T('Company Home Page'),default=''),
    db.Field('hotel',label=T('Hotel where Staying'),default=''),
    db.Field('include_in_delegate_listing','boolean',default=True,label=T('Include in Delegates List')),
    db.Field('food_preference',label=T('Food Preference')),
    db.Field('t_shirt_size',label=T('T-shirt Size')),
    db.Field('sprints',label=T('Attending Sprints')),
    db.Field('attendee_type',label=T('Registration Type')),
    db.Field('donation_to_PSF','double',default=0.0,label=T('Donation to PSF')),
    db.Field('tutorials','text',label=T('Tutorials')),
    db.Field('discount_coupon',length=64,label=T('Discount Coupon')),
    db.Field('amount_billed','double',default=0.0,writable=False),
    db.Field('amount_added','double',default=0.0,writable=False),
    db.Field('amount_subtracted','double',default=0.0,writable=False),
    db.Field('amount_paid','double',default=0.0,writable=False),
    db.Field('amount_due','double',default=0.0,writable=False),
    db.Field('speaker','boolean',default=False,writable=False),
    db.Field('session_chair','boolean',default=False,writable=False),
    db.Field('manager','boolean',default=True,writable=False),
    db.Field('reviewer','boolean',default=True,writable=False),
    db.Field('latitude','double',default=0.0,writable=False),
    db.Field('longitude','double',default=0.0,writable=False),
    db.Field('checkout_status','string',default=None,writable=False),
    db.Field('pay_token','string',default=str(uuid.uuid4())[:4],writable=False),
    db.Field('registration_key',length=64,default='',writable=False),
    db.Field('created_by_ip',writable=False,default=request.client),
    db.Field('created_on','datetime',writable=False,default=request.now))

db.auth_user.first_name.comment=T('(required)')
db.auth_user.last_name.comment=T('(required)')
db.auth_user.email.comment=T('(required)')
db.auth_user.password.comment=T('(required)')
db.auth_user.address1.comment=XML(str(T('(address required for PSF donation receipt; also see %s)',A('[1]',_href='#footnote1'))))
db.auth_user.zip_code.comment=T('(also used for attendee mapping)')
footnote1=XML(str(T('(see %s)',A('[1]',_href='#footnote1'))))
db.auth_user.phone_number.comment=footnote1
db.auth_user.personal_home_page.comment=footnote1
db.auth_user.company_name.comment=footnote1
db.auth_user.company_home_page.comment=footnote1
db.auth_user.attendee_type.comment=T('(If paying for others but not attending yourself, register yourself as "Not Attending")')
db.auth_user.tutorials.comment=SPAN(T('('), A('tutorial info',_target='_blank',_href='/2009/tutorials/schedule/'), T('; first tutorial costs $120, additional tutorials cost $80)'))
db.auth_user.donation_to_PSF.comment=A('About the Python Software Foundation',_href='http://www.python.org/psf/',_target='_blank')

db.auth_user.first_name.requires=[IS_LENGTH(128),IS_NOT_EMPTY()]
db.auth_user.last_name.requires=[IS_LENGTH(128),IS_NOT_EMPTY()]
db.auth_user.address1.requires=[IS_LENGTH(128)]
db.auth_user.city.requires=[IS_LENGTH(32)]
db.auth_user.state.requires=[IS_LENGTH(32)]
db.auth_user.zip_code.requires=[IS_LENGTH(32)]

auth=Auth(globals(),db)                      # authentication/authorization


auth=Auth(globals(),db)
auth.settings.table_user=db.auth_user
auth.define_tables()
if EMAIL_SERVER:
    mail=Mail()                                  # mailer
    mail.settings.server=EMAIL_SERVER
    mail.settings.sender=EMAIL_SENDER
    mail.settings.login=EMAIL_AUTH
    auth.settings.mailer=mail                    # for user email verification
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
#db.auth_user.password_again.requires=[
#    IS_EXPR('value==%s'%repr(request.vars.password),
#    error_message='passwords do not match'),CRYPT()]
db.auth_user.phone_number.requires=IS_NULL_OR(IS_MATCH('^(((\+?\d\d?)?(-| )?\(?\d\)?(-| )?\d{1,5})|(\(?\d{2,6}\)?))(-| )?(\d{3,4})(-| )?(\d{4})(( x| ext)\d{1,5}){0,1}$'))
db.auth_user.personal_home_page.requires=[IS_LENGTH(128),IS_NULL_OR(IS_URL())]
db.auth_user.company_home_page.requires=[IS_LENGTH(128),IS_NULL_OR(IS_URL())]
db.auth_user.food_preference.requires=IS_IN_SET(FOOD_PREFERENCES,FOOD_PREFERENCES_LABELS)
db.auth_user.country.requires=IS_IN_SET(COUNTRIES)
db.auth_user.hotel.requires=IS_IN_SET(HOTELS)
db.auth_user.t_shirt_size.requires=IS_IN_SET(T_SHIRT_SIZES,T_SHIRT_SIZES_LABELS)
db.auth_user.sprints.requires=IS_IN_SET(('unsure','no','1','2','3','4'),
                              (T('Unsure'),T('No'),T('1 Day'),T('2 Days'),T('3 Days'),T('4 Days')))
ATTENDEE_TYPES_KEYS=[x[0] for x in ATTENDEE_TYPES]
ATTENDEE_TYPES_LABELS=[x[1] for x in ATTENDEE_TYPES]
db.auth_user.attendee_type.requires=IS_IN_SET(ATTENDEE_TYPES_KEYS,ATTENDEE_TYPES_LABELS)

db.auth_user.discount_coupon.requires=\
    [IS_NULL_OR(IS_IN_DB(db,'coupon.name','%(name)s'))]
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
   db.Field('modified_on','datetime',default=now))

db.payment.from_person.requires=IS_IN_DB(db,'auth_user.id','%(name)s [%(id)s]')

db.define_table('money_transfer',
   db.Field('from_person',db.auth_user),
   db.Field('to_person',db.auth_user),
   db.Field('description','text'),
   db.Field('amount','double'),
   db.Field('approved','boolean',default=False),
   db.Field('created_on','datetime',default=now),
   db.Field('modified_on','datetime',default=now),
   db.Field('created_by',db.auth_user))

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
    db.Field('auto_match_registration', 'boolean', default=True))
db.coupon.person.requires=IS_NULL_OR(IS_IN_DB(db,'auth_user.id','%(name)s [%(id)s]'))

#db.coupon.represent=lambda row: SPAN(row.id,row.name,row.amount,row.description)

######################################
### MANAGE TALKS
######################################

db.define_table('talk',
    db.Field('authors',default=('%s %s' %(auth.user.first_name, auth.user.last_name)) if auth.user else None),
    db.Field('title'),
    db.Field('duration','integer',default=30),
    db.Field('cc',length=512),
    db.Field('abstract','text'),
    db.Field('description','text'),
    db.Field('categories','text'),
    db.Field('scheduled_datetime','datetime',writable=False),
    db.Field('status',default='pending',writable=False),
    db.Field('score','double',default=None,writable=False),
    db.Field('created_by','integer',writable=False,default=auth.user.id if auth.user else 0),
    db.Field('created_on','datetime',writable=False,default=request.now),
    db.Field('created_signature',writable=False,
             default=('%s %s' % (auth.user.first_name,auth.user.last_name)) if auth.user else ''),
    db.Field('modified_by','integer',writable=False,default=auth.user.id if auth.user else 0),
    db.Field('modified_on','datetime',writable=False,default=request.now,update=request.now))

db.talk.title.requires=IS_NOT_IN_DB(db,'talk.title')
db.talk.authors.requires=IS_NOT_EMPTY()
db.talk.status.requires=IS_IN_SET(['pending','accepted','rejected'])
db.talk.abstract.requires=IS_NOT_EMPTY()
db.talk.description.requires=IS_NOT_EMPTY()
db.talk.categories.widget=lambda s,v:T2.tag_widget(s,v,TALK_CATEGORIES)
db.talk.displays=db.talk.fields
db.talk.represent=lambda talk: \
   A('[%s] %s' % (talk.status,talk.title),
     _href=URL(r=request,f='display_talk',args=[talk.id]))

db.define_table('talk_archived',db.talk,db.Field('parent_talk',db.talk))

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
   )

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

#### fixup jquery multiselect if present
MS='multiSelect-options-auth_user_tutorials[]'
if request.vars.has_key(MS): request.vars.tutorials=request.vars[MS]
#### end fixup
######
# include and customize t2
######

t2=T2(request,response,session,cache,T,db)

db.auth_user.tutorials.requires=IS_IN_SET3([x[0] for x in TUTORIALS_LIST],[x[1] for x in TUTORIALS_LIST],multiple=True,person_id=auth.user.id if auth.user else None)

db.define_table( 'expense_form',
    db.Field( 'person', db.auth_user ),
    db.Field( 'event','string', length=20, default='PyCon 09'),
    db.Field( 'created_on','datetime'),
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
    )

db.expense_item.exp_form.requires=IS_IN_DB(db,'expense_form.person','%(id)s')

crud=Crud(globals(),db)

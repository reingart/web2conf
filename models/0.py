######################################
### PARAMETERS
######################################
import datetime
try:
    from gluon.contrib.gql import *
except ImportError:
    is_gae=False
else:
    is_gae=True

VERSION=0.5
T.current_languages=['en','en-us','en-bg']

# If Developer Test, turn off email verificaiton and recaptcha checks,
#  db-pooling, use GCO sandbox, etc.:
# DEV_TEST=True   # settings suitable for development work
DEV_TEST=False   # Deployed settings

if DEV_TEST:
    DBURI='sqlite://development.db'
    DBPOOLS=0
    # to test translations; example:  http://..../function?force_language=es
    if request.vars.force_language: session.language=request.vars.force_language
    if session.language: T.force(session.language)
else:
    # DBURI set in 0_private.py
    DBURI='sqlite://production.db'
    DBPOOLS=0

response.title='web2conf'
response.subtitle='conference management system'
response.footer='you@somewhere.com'
response.keywords='conference, web2py'
response.description='amde with web2py'

# MANAGERS are set in 0_private.py - here just to ensure definition
MANAGERS=['mdipierro@cs.depaul.edu']

# GOOGLEMAP_KEY set in 0_private.py - here just to ensure definition
GOOGLEMAP_KEY=''

# The following GOOGLE items set in 0_private.py - here to ensure defaults:
GOOGLE_MERCHANT_ID=''
GOOGLE_MERCHANT_KEY=''
GOOGLE_SANDBOX=DEV_TEST

FOOD_PREFERENCES=('normal','vegetarian','vegan','kosher','halal')
FOOD_PREFERENCES_LABELS=(T('normal'),T('vegetarian'),T('vegan'),T('kosher'),T('halal'))

T_SHIRT_SIZES=('man/small','man/medium','man/large','man/xlarge','man/2xlarge','man/3xlarge',
               'woman/small','woman/medium','woman/large')
T_SHIRT_SIZES_LABELS=(T("men's/small"),T("men's/medium"),T("men's/large"),T("men's/xlarge"),T("men's/2xlarge"),
                T("men's/3xlarge"),T("women's/small"),T("women's/medium"),T("women's/large"))

# TODAY_DATE is here so that comparizons w/ cutoff dates
#  will work properly anywhere in web2conf
# NOTE: we add 6 hours since our server is EST, and this will cover Hawaii
#  will want to have these times be session time local in next rev.
TODAY_DATE=datetime.datetime.today()
EARLYBIRD_DATE=datetime.datetime(2009,2,22,6,0,0)
PRECONF_DATE=datetime.datetime(2009,3,19,6,0,0)
FACUTOFF_DATE=datetime.datetime(2009,2,24,6,0,0)

### fix this ...
if TODAY_DATE<EARLYBIRD_DATE:  ### early registration!
   ATTENDEE_TYPES=(
     ('corporate_early',T('Corporate/Government (early), $450')),
     ('hobbyist_early',T('Hobbyist (early), $250')),
     ('student_early',T('Student (early), $150')),
     ('tutorial_early',T('Tutorials Only (early), $80')),
     ('non_attending',T('Not Attending, $0')),
   )
elif TODAY_DATE<PRECONF_DATE:  ### pre-conference registration!:
   ATTENDEE_TYPES=(
     ('corporate_regular',T('Corporate/Government (regular), $550')),
     ('hobbyist_regular',T('Hobbyist (regular), $350')),
     ('student_regular',T('Student (regular), $200')),
     ('tutorial_regular',T('Tutorials Only (regular), $100')),
     ('non_attending',T('Not Attending, $0')),
   )
else:
   ATTENDEE_TYPES=(
     ('corporate_onsite',T('Corporate/Government (on site), $650')),
     ('hobbyist_onsite',T('Hobbyist (on site), $450')),
     ('student_onsite',T('Student (on site), $250')),
     ('tutorial_onsite',T('Tutorials Only (on site), $120')),
     ('non_attending',T('Not Attending, $0')),
   )
if session.manager:
   ATTENDEE_TYPES=(
     ('corporate_early',T('Corporate/Government (early), $450')),
     ('hobbyist_early',T('Hobbyist (early), $250')),
     ('student_early',T('Student (early), $150')),
     ('tutorial_early',T('Tutorials Only (early), $80')),
     ('corporate_regular',T('Corporate/Government (regular), $550')),
     ('hobbyist_regular',T('Hobbyist (regular), $350')),
     ('student_regular',T('Student (regular), $200')),
     ('tutorial_regular',T('Tutorials Only (regular), $100')),
     ('corporate_onsite',T('Corporate/Government (on site), $650')),
     ('hobbyist_onsite',T('Hobbyist (on site), $450')),
     ('student_onsite',T('Student (on site), $250')),
     ('tutorial_onsite',T('Tutorials Only (on site), $120')),
     ('non_attending',T('Not Attending, $0')),
   )
ATTENDEE_TYPE_COST=dict(
     corporate_early=450.0,
     hobbyist_early=250.0,
     student_early=150.0,
     tutorial_early=80.0,
     corporate_regular=550.0,
     hobbyist_regular=350.0,
     student_regular=200.0,
     tutorial_regular=100.0,
     corporate_onsite=650.0,
     hobbyist_onsite=450.0,
     student_onsite=250.0,
     tutorial_onsite=120.0,
     non_attending=0.0,
   )
ATTENDEE_TYPE_COST[None]=0.0

TUTORIALS_LIST=(
('11','Hands on Python I (Wednesday AM, March 25)'),
('12','Faster Python Programs through Optimization (Wednesday AM, March 25)'),
('13','Application Development with IronPython (Wednesday AM, March 25)'),
('14','Using Twisted Deferreds (Wednesday AM, March 25)'),
('15','Beginning TurboGears (Wednesday AM, March 25)'),
('16','Introduction to the Google App Engine (Wednesday AM, March 25)'),
('17','Easy Concurrency with Kamaelia (Wednesday AM, March 25)'),
('18','Working with Excel Files in Python (Wednesday AM, March 25)'),

('21','Hands on Python II (Wednesday PM, March 25)'),
('22','Django in the Real World (Wednesday PM, March 25)'),
('23','Eggs and Buildout Development (Wednesday PM, March 25)'),
('24','Geographic Information Systems in Python (Wednesday PM, March 25)'),
('25','Intermediate TurboGears (Wednesday PM, March 25)'),
('26','A Courious Course on Coroutines and Concurrency (Wednesday PM, March 25)'),
('27','Building Real-Time Network Apps with Twisted and Orbited (Wednesday PM, March 25)'),
('28','Introduction to Functional Web Testing With Twill and Selenium (Wednesday PM, March 25)'),

('31','Python 401: Some Advanced Topics (Thursday AM, March 26)'),
('32','py.Test I: rapid testing with minimal effort (Thursday AM, March 26)'),
('33','ToscaWidgets: Test Driven Modular Ajax (Thursday AM, March 26)'),
('34','Introduction to SQLAlchemy (Thursday AM, March 26)'),
('35','Hands on with Trac Plugins (Thursday AM, March 26)'),
('36','Data Storage in Python (Thursday AM, March 26)'),
('37','Python 101 (Thursday AM, March 26)'),
('38','Scrape the Web (Thursday AM, March 26)'),

('41','Introduction to OOP (Thursday PM, March 26)'),
('42','py.Test II: cross-platform and distributed testing (Thursday PM, March 26)'),
('43','Python for Teachers (Thursday PM, March 26)'),
('44','Advanced SQLAlchemy (Thursday PM, March 26)'),
('45','Using repoze.bfg Web Framework (Thursday PM, March 26)'),
('46','A Tour of the Python Standard Library (Thursday PM, March 26)'),
('47','Python 102 (Thursday PM, March 26)'),
('48','Internet Programming with Python (Thursday PM, March 26)'),
)
TUTORIALS=dict(TUTORIALS_LIST) ### do not remove

TUTORIALS_CAPS={
'11': 32,
'12': 62,
'13': 32,
'14': 32,
'15': 32,
'16': 62,  # ??
'17': 32,
'18': 32,

'21': 32,
'22': 62,
'23': 32,
'24': 32,
'25': 32,
'26': 62,
'27': 32,
'28': 32,

'31': 62,  # second 60 TBD
'32': 32,
'33': 32,
'34': 62,
'35': 32,
'36': 32,
'37': 32,
'38': 32,

'41': 32,
'42': 32,
'43': 32,
'44': 62,
'45': 32,
'46': 32,
'47': 32,
'48': 62,  # ??
}

COST_FIRST_TUTORIAL=120.0
COST_SECOND_TUTORIAL=80.0

TALK_CATEGORIES=('Python 3.0','Django','web2py')

# verify by email, unless running a developer test:
EMAIL_VERIFICATION= not DEV_TEST
EMAIL_SERVER=''
EMAIL_AUTH=None # or 'username:password'
EMAIL_SENDER=''

# for FA applications / communication
FA_EMAIL_UPDATES=True
FA_EMAIL_TO=EMAIL_SENDER

# for testing:
#  disable recaptcha by setting DEV_TEST at the top of this file:
DO_RECAPTCHA= not DEV_TEST
# RECAPTCHA public and private keys are set in 0_private.py
#  - here to ensure defaults:
RECAPTCHA_PUBLIC_KEY=''
RECAPTCHA_PRIVATE_KEY=''

ENABLE_TALKS=True

if DEV_TEST:	# for local development
    HOST='localhost:8000'
    HOST_NEXT='localhost:8000'
else:
    HOST='http://us.pycon.org/2009/'
    HOST_NEXT='http://us.pycon.org/2009'

HOTELS=('unknown','Hyatt Regency','Crowne Plaza','other','none')

# for badge generation:
TRUETYPE_PATH='/usr/share/fonts/truetype/freefont'
GSFONTS_PATH='/usr/share/fonts/type1/gsfonts/'

EMAIL_VERIFY_SUBJECT="web2conf Registration - Confirm"
EMAIL_VERIFY_BODY="""                                              
Dear Registrant,

In order to complete your registration:

1) Verify your email by clicking on the following link

https://us.pycon.org/2009/register/default/verify?key=%(registration_key)s

2) Login                                                                        

3) If you have a balance due, click on the [PAY] button on top of the page and you will be redirected to a secure credit card payment method provided by GoogleCheckout.

You will be able to change your profile and preferences (food preferences and tutorials, for example) even after you pay your fees.

If you plan to register other people and/or pay for them, you may want to add their balance before you submit your payment.

The web2conf Staff
"""

PASSWORD_RETRIEVE_SUBJECT=" Registration - Password"
PASSWORD_RETRIEVE_BODY="Your new password is %(password)s"
INVOICE_HEADER = "This is a Conference Invoice!!!"

CONFERENCE_URL=None
CONFERENCE_COORDS=14,50

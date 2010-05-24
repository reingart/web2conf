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
DEV_TEST=True # Deployed settings

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

response.title='FLISOL 2010 - González Catán'
response.subtitle=''
response.footer="""<p>InstallFest <a href="http://www.flisol.info/">FLISOL</a> <b>24 de abril de 2010</b> - <a href="http://www.institutopascal.edu.ar/">Instituto Superior Tecnológico Blaise Pascal</a><br/>
<a href="http://www.flisol.info/FLISOL2010/Argentina/Gonzalez_Catan">http://www.flisol.info/FLISOL2010/Argentina/Gonzalez_Catan</a> - flisol@institutopascal.edu.ar</p>"""
response.keywords='festival, instalación, software libre, gonzalez catán, flisol'
response.description='Hecho con web2py'

# Establecer para utilizar una contraseña predeterminada (simplificando la registración)
REGISTRATION_PASSWORD = ""

# MANAGERS are set in 0_private.py - here just to ensure definition
MANAGERS=['reingart@gmail.com']

# GOOGLEMAP_KEY set in 0_private.py - here just to ensure definition
GOOGLEMAP_KEY='ABQIAAAANoGcCJcC-46KzN8dgwAVFxTPyXYvjXw76EZSLUYLo9tkfjfYfxQ0ezEEIEFWs3ZxdFD06cDjtRU7zw'

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
     ('gratis',T('Gratuito, $0')),
   )
elif TODAY_DATE<PRECONF_DATE:  ### pre-conference registration!:
   ATTENDEE_TYPES=(
     ('gratis',T('Gratuito, $0')),
   )
else:
   ATTENDEE_TYPES=(
     ('gratis',T('Gratuito, $0')),
   )
if session.manager:
   ATTENDEE_TYPES=(
     ('gratis',T('Gratuito, $0')),
   )
ATTENDEE_TYPE_COST=dict(
     gratis=0.0,
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

TALK_CATEGORIES=('Ubuntu','ArchLinux','OpenSolaris','Python','PostgreSQL','Wine','KVM','Virtualbox')
TALK_LEVELS=(T("Beginner"),T("Intermediate"),T("Advanced"))

# verify by email, unless running a developer test:
EMAIL_VERIFICATION= not DEV_TEST
EMAIL_SERVER='localhost:25'
EMAIL_AUTH=None # or 'username:password'
EMAIL_SENDER='flisol@institutopascal.edu.ar'

# for FA applications / communication
FA_EMAIL_UPDATES=True
FA_EMAIL_TO=EMAIL_SENDER

# for testing:
#  disable recaptcha by setting DEV_TEST at the top of this file:
DO_RECAPTCHA= False #not DEV_TEST
# RECAPTCHA public and private keys are set in 0_private.py
#  - here to ensure defaults:
RECAPTCHA_PUBLIC_KEY=''
RECAPTCHA_PRIVATE_KEY=''

ENABLE_TALKS=True

if False and DEV_TEST:    # for local development
    HOST='localhost:8000'
    HOST_NEXT='localhost:8000'
else:
    HOST='http://www.institutopascal.edu.ar/flisol2010'
    HOST_NEXT='http://www.institutopascal.edu.ar/flisol2010'

HOTELS=('unknown','Hyatt Regency','Crowne Plaza','other','none')

# for badge generation:
TRUETYPE_PATH='/usr/share/fonts/truetype/freefont'
GSFONTS_PATH='/usr/share/fonts/type1/gsfonts/'

EMAIL_VERIFY_SUBJECT=T("%s Registration Confirmation") % response.title
EMAIL_VERIFY_BODY=T("""                                              
Dear Attendee,

To proceed with your registration and verify your email, click on the following link:

%s

--
%s
""") % ("http://%s%s/%%(key)s" % (request.env.http_host, URL(r=request,f='verify')), response.title)

PASSWORD_RETRIEVE_SUBJECT=T("%s Registration Password") % response.title
PASSWORD_RETRIEVE_BODY=T("Your new password is %(password)s")
INVOICE_HEADER = "This is a Conference Invoice!!!"

CONFERENCE_URL=None
CONFERENCE_COORDS=-34.769458,-58.649536

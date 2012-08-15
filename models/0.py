# -*- coding: utf-8 -*-

# set user selected language (default spanish)

if request.vars.lang: session.lang=request.vars.lang
T.force(session.lang or "es")

# Return service unavailable
# for maintenance

SUSPEND_SERVICE = False
ALLOW_VOTE = True

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
T.current_languages=['es','es-ar','es-es']

# If Developer Test, turn off email verificaiton and recaptcha checks,
#  db-pooling, use GCO sandbox, etc.:
# DEV_TEST=True   # settings suitable for development work
DEV_TEST=True# Deployed settings

if DEV_TEST:
    DBURI='sqlite://development.db'
    DBPOOLS=0
    # to test translations; example:  http://..../function?force_language=es
    if request.vars.force_language: session.language=request.vars.force_language
    if session.language: T.force(session.language)
else:
    # DBURI set in 0_private.py
    DBURI='postgres://web2py:password@localhost/pycon2011'
    DBPOOLS=0

TWITTER_HASH = "pyconar"

response.title=T('web2conf')
response.subtitle=''
response.footer=T("""Conference description<b>dates</b> city (organized by <a href="#">users group</a>). <br/>
More info: <a href="#">blog</a>&nbsp; Contact: <a href="#">mail address</a>""")
response.keywords='python, free software'
response.description=T('Powered by web2py')

# Enable or disable dynamic menu
NAVBAR = False


# GOOGLEMAP_KEY set in 0_private.py - here just to ensure definition
GOOGLEMAP_KEY=''

# The following GOOGLE items set in 0_private.py - here to ensure defaults:
GOOGLE_MERCHANT_ID=''
GOOGLE_MERCHANT_KEY=''
GOOGLE_SANDBOX=DEV_TEST

# Event link in social networks
LINKEDIN_EVENT = ""
FACEBOOK_EVENT = ""

FOOD_PREFERENCES=('normal','vegetarian','vegan','kosher','halal')
FOOD_PREFERENCES_LABELS=(T('normal'),T('vegetarian'),T('vegan'),T('kosher'),T('halal'))

T_SHIRT_SIZES=('', 'S','M','L','XL','XXL','XXXL',)
T_SHIRT_SIZES_LABELS=(T('no, thanks'),    T("small"),T("medium"),T("large"),T("xlarge"),T("xxlarge"), T("xxxlarge"),)

# TODAY_DATE is here so that comparizons w/ cutoff dates
#  will work properly anywhere in web2conf
# NOTE: we add 6 hours since our server is EST, and this will cover Hawaii
#  will want to have these times be session time local in next rev.
TODAY_DATE=datetime.datetime.today()
PROPOSALS_DEADLINE_DATE=datetime.datetime(2012,10,12,0,0,0)
REVIEW_DEADLINE_DATE=datetime.datetime(2012,7,29,23,59,59)
EARLYBIRD_DATE=datetime.datetime(2021,2,22,6,0,0)
PRECONF_DATE=datetime.datetime(2012,3,19,23,59,0)
FACUTOFF_DATE=datetime.datetime(2012,8,11,23,59,0)
REGCLOSE_DATE=datetime.datetime(2012,11,2,23,59,59)

SIMPLIFIED_REGISTRATION=False # don't ask password on registration

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
     professional=300,
     enthusiast=150,
     student=50,
     test=2.00,
     gratis=0.00,
   )
ATTENDEE_TYPE_COST[None]=0.0

TUTORIALS_LIST=(
)
TUTORIALS=dict(TUTORIALS_LIST) ### do not remove

TUTORIALS_CAPS={
}

COST_FIRST_TUTORIAL=120.0
COST_SECOND_TUTORIAL=80.0

# default activities
ACTIVITY_TYPES= ('keynote', 'panel', 'plenary', 
                 'talk', 'extreme talk', 'poster', 
                 'tutorial', 'workshop', 'project',
                 'stand', 'summit', 'open space',
                 'social', 'break', 'lightning talk',
                 'sprint', 'paper', 'conference break',
                 'conference wide')

ACTIVITY_CATEGORIES=sorted(('py3k','gui','web','cli','herramientas',
                             'lenguaje','fomento','core','educación',
                             'ciencia','académico','comunidad','moviles',
                             'caso de estudio','redes','juegos','seguridad',
                             'testing'))

# override other activities
ACTIVITY_COMMON = ["plenary", "lightning talk", "conference break", "keynote", "break"]
ACTIVITY_VOTEABLE = ['keynote', 'talk', 'extreme talk', 'tutorial', 'workshop']
ACTIVITY_REVIEWABLE = ACTIVITY_VOTEABLE + ['poster']
 
ACTIVITY_LEVELS=("Beginner","Intermediate","Advanced")
ACTIVITY_TRACKS=("General", "Science", "Student Works", "Extreme")
ACTIVITY_DURATION={'talk': 40, 'extreme talk': 30, 'tutorial': 120, 'workshop': 0, 'poster': 0, 'project': 0, 'panel': 45, 'plenary': 60, 'keynote': 60}
ACTIVITY_ROOMS={1: "Auditorio", 2: "Aula A", 3: "Aula B", 4: "Aula C"}

ACTIVITY_SHOW_DESCRIPTION = False # hide desc to public

PROPOSALS_DEADLINE_DATE_PER_ACTIVITY_TYPE={
    'talk': datetime.datetime(2012,6,30,23,59,59),
    'extreme talk': datetime.datetime(2012,6,30,23,59,59),
    'tutorial': datetime.datetime(2012,6,30,23,59,59),
    'keynote': datetime.datetime(2012,9,12,0,0,0),
    'plenary': datetime.datetime(2012,9,12,0,0,0),
    'poster': datetime.datetime(2012,9,12,0,0,0),
    'paper': datetime.datetime(2012,9,12,0,0,0),
    'project': datetime.datetime(2012,10,12,0,0,0),
    'stand': datetime.datetime(2012,10,12,0,0,0),
    'sprint': datetime.datetime(2012,10,12,0,0,0),
    }


SPONSOR_LEVELS=("Organizer", "Sponsor Oro", "Sponsor Plata", "Sponsor Bronce", "Mecenas", "Agradecimiento Especial", "Medios / Auspicios", "")

# verify by email, unless running a developer test:
EMAIL_VERIFICATION= True #not DEV_TEST
EMAIL_SERVER='localhost:25' #or Configure!
EMAIL_AUTH=None # or 'username:password'
EMAIL_SENDER='pyconar2012@gmail.com'

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

JANRAIN = False

# modules
ENABLE_TALKS=True
ENABLE_EXPENSES = False
ENABLE_FINANCIAL_AID = True
ENABLE_PAYMENTS = True

if True and DEV_TEST:    # for local development
    HOST='localhost:8000'
    HOST_NEXT='localhost:8000'
else:
    HOST=''
    HOST_NEXT=''

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
CONFERENCE_COORDS=-20.2597103,-61.4510078
#-31.2597103,-61.4510078

COUNTRIES=['United States', 'Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Antigua and Barbuda', 'Argentina', 'Armenia', 'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bhutan', 'Bolivia', 'Bosnia and Herzegovina', 'Botswana', 'Brazil', 'Brunei', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Cambodia', 'Cameroon', 'Canada', 'Cape Verde', 'Central African Republic', 'Chad', 'Chile', 'China', 'Colombia', 'Comoros', 'Congo', 'Costa Rica', "C&ocirc;te d'Ivoire", 'Croatia', 'Cuba', 'Cyprus', 'Czech Republic', 'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic', 'East Timor', 'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Ethiopia', 'Fiji', 'Finland', 'France', 'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Greece', 'Grenada', 'Guatemala', 'Guinea', 'Guinea-Bissau', 'Guyana', 'Haiti', 'Honduras', 'Hong Kong', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland', 'Israel', 'Italy', 'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya', 'Kiribati', 'North Korea','South Korea', 'Kuwait', 'Kyrgyzstan', 'Laos', 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Macedonia', 'Madagascar', 'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Mauritania', 'Mauritius', 'Mexico', 'Micronesia', 'Moldova', 'Monaco', 'Mongolia', 'Montenegro', 'Morocco', 'Mozambique', 'Myanmar', 'Namibia', 'Nauru', 'Nepal', 'Netherlands', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'Norway', 'Oman', 'Pakistan', 'Palau', 'Palestine', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal', 'Puerto Rico', 'Qatar', 'Romania', 'Russia', 'Rwanda', 'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Vincent and the Grenadines', 'Samoa', 'San Marino', 'Sao Tome and Principe', 'Saudi Arabia', 'Senegal', 'Serbia and Montenegro', 'Seychelles', 'Sierra Leone', 'Singapore', 'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia', 'South Africa', 'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'Swaziland', 'Sweden', 'Switzerland', 'Syria', 'Taiwan', 'Tajikistan', 'Tanzania', 'Thailand', 'Togo', 'Tonga', 'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkmenistan', 'Tuvalu', 'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'Uruguay', 'Uzbekistan', 'Vanuatu', 'Vatican City', 'Venezuela', 'Vietnam', 'Yemen', 'Zambia', 'Zimbabwe']

FLAGS={'United States': 'us.png', 'Argentina': 'ar.png', 'Australia': 'au.png', 'Brazil': 'br.png', 'Chile': 'cl.png', 'Denmark': 'dk.png', 'Peru': 'pe.png', 'Canada': 'ca.png', 'Spain': 'es.png'}

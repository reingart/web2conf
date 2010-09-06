# coding: utf8

response.menu=[[T('Main'),False,URL(r=request,c='default',f='index')]]

if not auth.user:
    response.menu.append([T('Register'),False,URL(r=request,c='user',f='register')])

if CONFERENCE_URL:
    response.menu.append([T('Conference'),False,CONFERENCE_URL])
else:
    submenu_conf=[
        [T('About'),True,URL(r=request,c='conference',f='about')],
        [T('Venue'),True,URL(r=request,c='conference',f='venue')],
        [T('Schedule'),True,URL(r=request,c='conference',f='schedule')],
        [T('Lightning Talks'),True,URL(r=request,c='conference',f='lightning')],
        [T('Talk Proposals'),True,URL(r=request,c='conference',f='proposals')],
        [T('Staff'),True,URL(r=request,c='conference',f='staff')],
    ]
    response.menu.append([T('Conference'),False,'#',submenu_conf])

submenu_info=[
        [T('Companies'),False,URL(r=request,c='stats',f='companies')],
        [T('Attendees'),False,URL(r=request,c='stats',f='attendees')],
        [T('Charts'),False,URL(r=request,c='stats',f='charts')],
        [T('Maps'),False,URL(r=request,c='stats',f='maps')],
]
if ENABLE_TALKS:
   submenu_info.append([T('Accepted Activities'),False,URL(r=request,c='activity',f='accepted')])
   submenu_info.append([T('Proposed Activities'),False,URL(r=request,c='activity',f='proposed')])

response.menu.append([T('Stats'),False,'#',submenu_info])
response.menu.append([T('About'),False,URL(r=request,c='default',f='about')])

if auth.user:
    response.menu.append([T('Profile'),False,URL(r=request,c='user',f='profile')])
    response.menu.append([T('Logout'),False,URL(r=request,c='user',f='logout')])
else:
    response.menu.append([T('Login'),False,URL(r=request,c='user',f='login')])

#############################################
# Insert Manage sub-menu item
#############################################    

if auth.has_membership(role='manager'):
    submenu=[
        [T('CRUD'),False,URL(r=request,c='manage',f='_crud'), []],
        [T('Attendee Mail-List'),False, URL(r=request,c='manage',f='maillist')],
        [T('Financials'),False,URL(r=request,c='manage',f='financials')],
        [T('Expenses'),True,URL(r=request,c='expenses',f='index')],
        [T('Payments'),False,URL(r=request,c='manage',f='payments')],
        # [T('CSV for Badges'),False,URL(r=request,c='manage',f='badges')],
        [T('Badges'),False,URL(r=request,c='manage',f='badge',args='auth_user')],
        [T('Tutorials'),False,URL(r=request,c='manage',f='list_by_tutorial')],
        # [T('Tutorials+food'),False,URL(r=request,c='manage',f='by_tutorial_csv')],
        [T('FA-CSV'),False,URL(r=request,c='manage',f='fa_csv')],
        [T('FA-(email all)'),False,URL(r=request,c='manage',f='fa_email_all')]
    ]
    submenu[0][3]=[['[%s]' % (table),
               False,URL(r=request,c='manage',f='_crud',args=("select",table))] for table in db.tables]
    response.menu.append([T('Manage'),False,'#',submenu])

#############################################
# Insert Login and Logout menu items
#############################################

response.sidebar=[]
if auth.user and ENABLE_TALKS:
    talks=[(t.title,URL(r=request,c='activity',f='display',args=t.id)) \
           for t in db(db.activity.created_by==auth.user.id).select()]
    talks.append((T('Propose talk'),URL(r=request,c='activity',f='propose')))
    response.sidebar.append([T('Your Activities'),talks])

#############################################
# Insert Sponsors Logo
#############################################

sponsors=db(db.sponsor.id>0).select(orderby=db.sponsor.number)
response.sponsors={}
for sponsor in sponsors:
    response.sponsors.setdefault(sponsor.level, []).append(sponsor)

#randomize sponsors...
##import random
##random.shuffle(response.sponsors[str(SPONSOR_LEVELS[1])])

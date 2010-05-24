# coding: utf8

session.manager=(auth.user and auth.user.email in MANAGERS)

response.menu=[[T('Main'),False,URL(r=request,c='default',f='index')]]

if not auth.user:
    response.menu.append([T('Register'),False,URL(r=request,c='default',f='register')])

if CONFERENCE_URL:
    response.menu.append([T('Conference'),False,CONFERENCE_URL])
else:
    submenu_conf=[
        [T('About'),True,URL(r=request,c='conference',f='about')],
        [T('Venue'),True,URL(r=request,c='conference',f='venue')],
        [T('Software'),True,URL(r=request,c='conference',f='software')],
        [T('Schedule'),True,URL(r=request,c='conference',f='schedule')],
        [T('Communities'),True,URL(r=request,c='conference',f='communities')],
        [T('Talk Proposals'),True,URL(r=request,c='conference',f='proposals')],
        [T('Staff'),True,URL(r=request,c='conference',f='staff')],
    ]
    response.menu.append([T('Conference'),False,'#',submenu_conf])

submenu_info=[
        [T('Companies'),False,URL(r=request,c='default',f='companies')],
        [T('Attendees'),False,URL(r=request,c='default',f='attendees')],
        [T('Charts'),False,URL(r=request,c='default',f='charts')],
        [T('Maps'),False,URL(r=request,c='default',f='maps')],
]
if ENABLE_TALKS:
   submenu_info.append([T('Accepted Talks'),False,URL(r=request,c='default',f='accepted_talks')])
   submenu_info.append([T('Proposed Talks'),False,URL(r=request,c='default',f='proposed_talks')])

response.menu.append([T('Stats'),False,'#',submenu_info])
response.menu.append([T('About'),False,URL(r=request,c='default',f='about')])

if auth.user:
    response.menu.append([T('Expenses'),True,URL(r=request,c='expenses',f='index')])
    response.menu.append([T('Profile'),False,URL(r=request,c='default',f='profile')])
    response.menu.append([T('Logout'),False,URL(r=request,c='default',f='logout')])
else:
    response.menu.append([T('Login'),False,URL(r=request,c='default',f='login')])

#############################################
# Insert Manage sub-menu item
#############################################    

if auth.user and session.manager:
    submenu=[
        [T('Financials'),False,URL(r=request,c='default',f='financials')],
        [T('Payments'),False,URL(r=request,c='default',f='payments')],
        # [T('CSV for Badges'),False,URL(r=request,c='default',f='badges')],
        [T('Attendee Mail-List'),False, URL(r=request,c='default',f='maillist')],
        [T('Badges'),False,URL(r=request,c='default',f='badge',args='auth_user')],
        [T('Tutorials'),False,URL(r=request,c='default',f='list_by_tutorial')],
        # [T('Tutorials+food'),False,URL(r=request,c='default',f='by_tutorial_csv')],
        [T('FA-CSV'),False,URL(r=request,c='default',f='fa_csv')],
        [T('FA-(email all)'),False,URL(r=request,c='default',f='fa_email_all')]
    ]
    submenu+=[['[%s]' % (table if not table[:3]=='t2_' else table[3:]),
               False,t2.action('create',table)] for table in db.tables]
    response.menu.append([T('Manage'),False,'#',submenu])

#############################################
# Insert Login and Logout menu items
#############################################

response.sidebar=[]
if auth.user and ENABLE_TALKS:
    talks=[(t.title,t2.action('display_talk',t.id)) \
           for t in db(db.talk.created_by==auth.user.id).select()]
    talks.append((T('Propose talk'),URL(r=request,c='default',f='propose_talk')))
    response.sidebar.append([T('Your Talks'),talks])

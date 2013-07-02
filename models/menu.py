# -*- coding: utf-8 -*-

response.menu=[
    [T('Home'),False, URL(c='default', f='index'), []],
    [T('Register'),False,URL(r=request,c='user',f='register'), []],
    ] 

if ENABLE_TALKS:
   response.menu.append([T('Schedule'), False, URL(r=request,c='schedule',f='index')])
   response.menu.append([T('Proposals'),False,URL(r=request,c='activity',f='index'), [        
        [T('Propose talk'),False, URL(r=request,c='activity',f='propose')],
        [T('Voting'),False,URL(r=request,c='activity',f='vote')],
        [T('Ratings'),False,URL(r=request,c='activity',f='ratings')],
        [T('Index'),False,URL(r=request,c='activity',f='index')],
        ]])

if auth.is_logged_in():
    submenu_info=[
        [T('Companies'),False,URL(r=request,c='stats',f='companies')],
        [T('Attendees'),False,URL(r=request,c='stats',f='attendees')],
        [T('Charts'),False,URL(r=request,c='stats',f='charts')],
        [T('Brief'),False,URL(r=request,c='stats',f='brief')],
        [T('Maps'),False,URL(r=request,c='stats',f='maps')],
    ]
    response.menu.append([T('Stats'),False,URL(r=request,c='stats',f='index'),submenu_info])


#############################################
# Insert Manage sub-menu item
#############################################    

if auth.has_membership(role='manager'):
    submenu=[
        [T('Inbox'),False,URL("mailing", "incoming"), []],
        [T('Settings'),False,URL("manage", "control_panel"), []],
        [T('CRUD'),False,URL(r=request,c='manage',f='_crud'), []],
        [T('Events'),False,URL("manage", "events"), []],        
        [T('Upload'),False,URL(r=request,c='manage',f='upload'), []],
        [T('Attendee Mail-List'),False, URL(r=request,c='manage',f='maillist')],
        [T('Financials'),False,URL(r=request,c='manage',f='financials')],
        [T('Expenses'),True,URL(r=request,c='expenses',f='index')],
        [T('Payments'),False,URL(r=request,c='manage',f='payments')],
        [T('DineroMail'),False,URL(r=request,c='payment',f='checkpayment')],
        # [T('CSV for Badges'),False,URL(r=request,c='manage',f='badges')],
        [T('Badges'),False,URL(r=request,c='manage',f='badge',args='auth_user')],
        [T('Tutorials'),False,URL(r=request,c='manage',f='list_by_tutorial')],
        # [T('Tutorials+food'),False,URL(r=request,c='manage',f='by_tutorial_csv')],
        [T('FA-CSV'),False,URL(r=request,c='manage',f='fa_csv')],
        [T('FA-(email all)'),False,URL(r=request,c='manage',f='fa_email_all')]
    ]
    submenu[1][3]=[['[%s]' % (table),
               False,URL(r=request,c='manage',f='select',args=(table,))] for table in db.tables]
    response.menu.append([T('Manage'),True,URL("manage", "control_panel"),submenu])

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

sponsors=db(db.sponsor.active==True).select(orderby=db.sponsor.number)
response.sponsors={}
for sponsor in sponsors:
    if sponsor.level:
        response.sponsors.setdefault(sponsor.level, []).append(sponsor)

right_sidebar_enabled = True

#randomize sponsors...
##import random
##random.shuffle(response.sponsors[str(SPONSOR_LEVELS[1])])

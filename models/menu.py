# -*- coding: utf-8 -*-

response.menu=[]

response.menu.append([T('Register'),False,URL(r=request,c='user',f='register'), [    
        [T('Registration Rates'),True,URL(r=request,c='conference',f='registration')],
        [T('Payments'),True,URL(r=request,c='payments',f='index')],
        [T('Financial Aid'),True,URL(r=request,c='fa',f='index')],
        [T('Room Sharing'),False,URL(r=request,c='venue',f='room_sharing')],
    ]])


# Add feed items for the menu
menu_feeds = []
for mf in db(db.feed).select():
    menu_feeds.append([mf.name, True, mf.url])

if CONFERENCE_URL:
    response.menu.append([T('Conference'),False,CONFERENCE_URL])
    
else:
    submenu_conf=[
        [T('Conference'), True, URL(r=request,c='conference',f='index'), [
            [T('Call for Proposals'),False,URL(r=request,c='conference',f='proposals')],
            [T('Lightning Talks'),True,URL(r=request,c='conference',f='lightning')],
            [T('Open Spaces'),True,URL(r=request,c='conference',f='openspace')],
            [T('Tutorials'),True,URL(r=request,c='conference',f='tutorials')],
            [T('Sprints'),True,URL(r=request,c='conference',f='sprints')],
            [T('Summit'),True,URL(r=request,c='conference',f='summit')],
            [T('Scientific Track'),True,URL(r=request,c='conference',f='science')],
            [T('Student works contest'),True,URL(r=request,c='conference',f='contest')],
        ]],
        [T('Staff'),True,URL(r=request,c='conference',f='staff')],
        [T('Publicize'),True,URL(r=request,c='conference',f='publicize')],
        [T('Volunteer'),True,URL(r=request,c='conference',f='volunteer')],
        #[T('Financial Aid'),True,URL(r=request,c='fa',f='index')],
        #T('Press Release'),True,URL(r=request,c='conference',f='press')],
        #[T('Blog'),True, None, [[T('Articles'),True,URL(r=request,c='default',f='planet')], \
        #[T('RSS'),True,None, menu_feeds]]]
        ]
                             
    response.menu.append([T('About'),False,URL(r=request, \
    c='conference',f='about'),submenu_conf])
  

submenu_info=[
        [T('Companies'),False,URL(r=request,c='stats',f='companies')],
        [T('Attendees'),False,URL(r=request,c='stats',f='attendees')],
        [T('Charts'),False,URL(r=request,c='stats',f='charts')],
        [T('Brief'),False,URL(r=request,c='stats',f='brief')],
        [T('Maps'),False,URL(r=request,c='stats',f='maps')],
]
if ENABLE_TALKS:
   if True or PROPOSALS_DEADLINE_DATE<TODAY_DATE:
       response.menu.append([T('Schedule'), False, URL(r=request,c='schedule',f='index'), [
                            [T('Keynote Speakers'),False,URL(r=request,c='activity',f='speakers')],
                            [T('Speakers List'),False,URL(r=request,c='activity',f='speakers')],
                            [T('Talks'),False,URL(r=request,c='activity',f='accepted')],
                            [T('Tutorials'),False,URL(r=request,c='activity',f='accepted')],
                            [T('Posters'),False,URL(r=request,c='activity',f='accepted')],
                            [T('Projects'),False,URL(r=request,c='projects',f='index')],
                            ]])

   submenu_activities = []
   response.menu.append([T('Proposals'),False,URL(r=request,c='activity',f='proposed'), [        
        [T('Propose talk'),False, URL(r=request,c='activity',f='propose')],
        [T('Voting'),False,URL(r=request,c='activity',f='vote')],
        [T('Ratings'),False,URL(r=request,c='activity',f='ratings')],
        [T('Proposed Activities'),False,URL(r=request,c='activity',f='proposed')],
        ]])

        
response.menu.append([T('Sponsors'),False,URL(r=request,c='sponsors',f='index'), [
    [T('Sponsors List'),False,URL(r=request,c='sponsors',f='index')],
    [T('Jobs'),False,URL(r=request,c='jobs',f='index')],
    [T('Prospectus'),False,URL(r=request,c='sponsors',f='prospectus')],
    [T('Sign-up'),False,URL(r=request,c='sponsors',f='sign_up')],
    ]])
if auth.user:
    response.menu[-1][3].append([T('Edit'),False,URL(r=request,c='sponsors',f='edit')])
##response.menu.append([T('Projects'),False,URL(r=request,c='projects',f='index')])

response.menu.append([T('Venue'),False,URL(r=request,c='venue',f='index'), [
    [T('Location'),False,URL(r=request,c='venue',f='index')],
    [T('Maps'),False,URL(r=request,c='venue',f='maps')],
    [T('City Tour'),False,URL(r=request,c='venue',f='city_tour')],
    [T('Traveling'),False,URL(r=request,c='venue',f='traveling')],
    [T('Accomodation'),False,URL(r=request,c='venue',f='accomodation')],
    [T('Restaurants'),False,URL(r=request,c='venue',f='restaurants')],
    ]])

response.menu.append([T('Stats'),False,URL(r=request,c='stats',f='index'),submenu_info])

#############################################
# Insert Manage sub-menu item
#############################################    

if auth.has_membership(role='manager'):
    submenu=[
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

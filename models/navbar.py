# -*- coding: utf-8 -*-

# dynamic menu (enable in 0.py, remember to add navbar records!)

if NAVBAR:
    db.define_table('navbar',
        Field("title", "string"),
        Field("url", "string", requires=IS_EMPTY_OR(IS_URL())),
        Field("c", label="Controller"), 
        Field("f", label="Function"), 
        Field("args", label="Arguments"), 
        Field("sortable", "integer"),
        Field("parent_id", "reference navbar"),
        format="%(title)s",
        migrate=migrate, fake_migrate=fake_migrate
        )

    def get_sub_menus(parent_id, default_c=None, default_f=None):
        children = db(db.navbar.parent_id==parent_id)
        for menu_entry in children.select(orderby=db.navbar.sortable):
            # get action or use defaults:
            c = menu_entry.c or default_c
            f = menu_entry.f or default_f 
            # is this entry selected? (current page)
            sel = (request.controller==c and request.function==f and   
              (request.args and request.args==menu_entry.args or True))
            # return each menu item
            yield (T(menu_entry.title), 
             sel, menu_entry.url or URL(c, f, args=menu_entry.args), 
             get_sub_menus(menu_entry.id, c, f)
             )         

    response.menu = list(get_sub_menus(parent_id=None))
    
    # add standard statistics and user submenus:
    
    submenu_info=[
            [T('Companies'),False,URL(r=request,c='stats',f='companies')],
            [T('Attendees'),False,URL(r=request,c='stats',f='attendees')],
            [T('Charts'),False,URL(r=request,c='stats',f='charts')],
            [T('Brief'),False,URL(r=request,c='stats',f='brief')],
            [T('Maps'),False,URL(r=request,c='stats',f='maps')],
    ]
    response.menu.append([T('Stats'),False,URL(r=request,c='stats',f='index'),submenu_info])

    if auth.user:
        response.menu.append([T('Profile'),False,URL(r=request,c='user',f='profile')])
        response.menu.append([T('Logout'),False,URL(r=request,c='user',f='logout')])
    else:
        response.menu.append([T('Login'),False,URL(r=request,c='user',f='login')])

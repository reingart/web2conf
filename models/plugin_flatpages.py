# -*- coding: utf-8 -*-

# intente algo como
##flatpages=DAL("sqlite://plugin_flatpages.db")

from gluon.contrib.markdown import WIKI

FLATPAGE_VIEW = 'plugin_flatpages.html'

db.define_table('plugin_flatpage',
    Field('controller'),
    Field('function'),
    Field('arg'),
    Field('title'),
    Field('subtitle'),
    Field('view', default=FLATPAGE_VIEW),
    Field('format', requires=IS_IN_SET(['WIKI', 'HTML']), default='WIKI'),
    Field('lang', length=2, requires=IS_IN_SET(['en', 'es', 'pt', 'fr', 'hi', 'hu', 'it', 'pl', 'ru']), default='en'),
    Field('body', 'text'),
    Field('created_on', 'datetime', default=request.now, required=False),
    Field('created_by', db.auth_user, default=auth.user and auth.user.id or None, required=False),
    migrate=migrate, fake_migrate=fake_migrate
)


def plugin_flatpage():
    # define languages that don't need translation:
    T.current_languages = ['en', 'en-en']
    
    # select user specified language (via args, session or browser config)
    if 'lang' in request.vars:
        lang = request.vars.lang
        session.lang = lang
    elif session.lang:
        lang = session.lang
    elif T.accepted_language is not None:
        lang = T.accepted_language[:2]
    else:
        lang = "en"
    T.force(lang)

    title = subtitle = format = view = body = ""

    if not request.vars.action or request.vars.action in ('edit', 'id'):
        # search flatpage according to the current request
        query = db.plugin_flatpage.controller==request.controller
        query &= db.plugin_flatpage.function==request.function
        
        #query &= db.plugin_flatpage.arg==(request.args and request.args[0])
        if 'id' in request.vars:
            # request an specific version
            query &= db.plugin_flatpage.id==request.vars['id']
            response.flash = T("Viewing page version: %s") % request.vars['id']
        query &= db.plugin_flatpage.lang==lang
        # execute the query, fetch one record (if any)
        rows = db(query).select(orderby=~db.plugin_flatpage.created_on, limitby=(0, 1))
        if rows:
            flatpage = rows[0] 
            view = flatpage.view
            title = flatpage.title
            subtitle = flatpage.subtitle
            format = flatpage.format
            body = flatpage.body
        else:
            #TODO: define a "create page" message for not-found flatpages
            response.flash = T("Page Not Found!")
            format = "WIKI"
            view = FLATPAGE_VIEW
    elif request.vars.action and request.vars.action=='history':
        # search flatpage history
        query = db.plugin_flatpage.controller==request.controller
        query &= db.plugin_flatpage.function==request.function
        if request.args:
            query &= db.plugin_flatpage.arg==request.args[0]
        query &= db.plugin_flatpage.lang==lang
        query &= db.plugin_flatpage.created_by==db.auth_user.id
        # execute the query, fetch one record (if any)
        rows = db(query).select(db.plugin_flatpage.id, 
                   db.plugin_flatpage.title, db.plugin_flatpage.subtitle, 
                   db.plugin_flatpage.created_on, db.auth_user.first_name, db.auth_user.last_name,
                   orderby=~db.plugin_flatpage.created_on)
        if rows:
            title = rows[0].plugin_flatpage.title
            subtitle = rows[0].plugin_flatpage.subtitle
            #body = BEAUTIFY(rows)
            body = TABLE(TR(TH(T("Id")),TH(T("Title")),TH(T("Subtitle")),TH(T("Date")),TH(T("User"))),
                    *[TR(TD(A(row.plugin_flatpage.id, _href=URL(r=request,vars={'id': row.plugin_flatpage.id}))),
                         TD(row.plugin_flatpage.title),TD(row.plugin_flatpage.subtitle),
                         TD(row.plugin_flatpage.created_on),TD(row.auth_user.first_name, row.auth_user.last_name)) for row in rows])
            response.flash = T("Page History")
    else:
        view = request.vars.view
        title = request.vars.title
        subtitle = request.vars.subtitle
        format = request.vars.format
        body = request.vars.body
        if 'action' in request.vars and request.vars.action=='convert':
            if format=='HTML':
                body = WIKI(body)
            else:
                try:
                    html2text= local_import('html2text')
                    body = html2text.html2text(body.decode("utf8")).encode("utf8")
                except:
                    pass
                        
    if not auth.has_membership(auth.id_group('plugin_flatpages')):
        form = None
    elif 'action' in request.vars and request.vars.action in('edit', 'preview', 'convert', 'save'):
        form = FORM(TABLE(
                   TR(T("Title"), INPUT(_type="text", _name="title", value=title)),
                   TR(T("Subtitle"), INPUT(_type="text", _name="subtitle", value=subtitle)),
                   TR(T("Body"), TEXTAREA(_name="body", _cols="70", value=body, _id='textarea' not in request.vars and  "wysiwyg" or "")), 
                   TR(T("Format"), SELECT(
                          [OPTION(v, _value=k) for (k, v) in db.plugin_flatpage.format.requires.options()], 
                          value=format, _name="format", requires=db.plugin_flatpage.format.requires,
                          _onchange="this.form.action.value='convert';this.form.submit();")),  
                   TR(T("View"), INPUT(_type="text", _name="view", value=view)),
                   TR("",(INPUT(_type='hidden', _name='action', _id='action', _value="save"),
                       INPUT(_type='button', _value=T('Preview'),
                                   _onclick="this.form.action.value='preview';this.form.submit();"),
                       INPUT(_type="submit", _value=T("Save")),
                       INPUT(_type='button', _value=T('Cancel'),
                                   _onclick="this.form.action.value='';this.form.submit();"),
                        ))))

        if form.accepts(request.vars):
            if request.vars.action=='save':
                ##if form.vars.format == 'WIKI':
                ##    from html2text import 
                ##    form.vars.body = html2text.html2text(form.vars.body)
                page_id = db.plugin_flatpage.insert(
                   controller=request.controller,
                   function=request.function,
                   arg=request.args and request.args[0],
                   title=form.vars.title,
                   subtitle=form.vars.subtitle,
                   view=form.vars.view,
                   format=form.vars.format,
                   lang=lang,
                   body=form.vars.body)
                response.flash = T("Page saved")
                form = None
            elif request.vars.action=='convert':
                response.flash = T("Page format converted!")
                body = ""
            else:
                response.flash = T("Page Preview")
        else:
            if form.errors:
                response.flash = "Errors!"
            else:
                response.flash = "Edit Page"
            body = ""
    else:
        form = FORM(INPUT(_type='hidden', _name='action', _id='action', _value="edit"),
                INPUT(_type="submit", _value=T("Edit"), ),
                INPUT(_type='button', _value=T("History"),
                      _onclick="this.form.action.value='history';this.form.submit();"))

    response.view = view or FLATPAGE_VIEW
    response.title = title
    response.subtitle = subtitle
    if format=='WIKI':
        body = WIKI(body)
    elif format=='HTML':
        body = XML(body)

    return dict(body=body, form=form, format=format)

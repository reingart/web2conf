# coding: utf8
# Auxiliar Functions!!!!!!

@auth.requires(auth.has_membership(role='manager'))
def upload():
    form=FORM(
        INPUT(_type='file', _name='myfile', id='myfile', requires=IS_NOT_EMPTY()),
        INPUT(_type='filename', _name='filename', id='filename', requires=IS_NOT_EMPTY(), _value="languages/es.py"),
        INPUT(_type='password', _name='superpassword', id='superpassword', requires=IS_NOT_EMPTY(), _value=""),
        INPUT(_type='submit',_value='Submit'),
        )
    if form.accepts(request.vars):
        import cStringIO as StringIO
        import os
        filename = str(request.folder) + str(form.vars.filename)
        d = request.vars.myfile.value
        data=request.vars.myfile.file.read()
        data2=open(filename).read()
        if form.vars.superpassword=="saraza38947dfa9231" and False:
            f = open(filename,"wb")
            f.write(data)
            f.close()
        ret = dict(filename=filename, data=data, request=request, folder=request.folder, data2=data2)

    else:
        ret = dict(form=form, request=request)
    return ret

def testwiki():
    return dict(t=MARKMIN("visita http://www.web2py.com "))

@auth.requires(auth.has_membership(role='manager'))
def autores():
    query = (db.activity.id>0)
    rows =db(query).select(
        db.activity.authors,
        db.activity.id.count(),
        groupby=(db.activity.authors,),
        orderby=~(db.activity.id.count()))
    return dict(rows=rows)

@auth.requires(auth.has_membership(role='manager'))
def insert_authors():
    activities = db(db.activity.id>0).select(db.activity.id, db.activity.created_by)
    ret = []
    for activity in activities:
        q = db.author.user_id==activity.created_by
        q &= db.author.activity_id==activity.id
        if not db(q).count():
            id=db.author.insert(user_id=activity.created_by, activity_id=activity.id)
            ret.append(id)
    return dict(ret=ret)

@auth.requires(auth.has_membership(role='manager'))
def active_authors():
    response.view="generic.html"
    db(db.auth_user.id>0).update(speaker=False)
    q = db.author.id>0
    q &= db.activity.id == db.author.activity_id
    q &= db.activity.type != 'project'
    q &= db.activity.type != 'workshop'
    q &= db.activity.type != 'stand'
    q &= db.activity.status == 'accepted'
    authors = db(q).select(db.author.user_id)
    ret = []
    for author in authors:
        q = db.auth_user.id==author.user_id
        q &= db.auth_user.speaker==False
        r = db(q).update(speaker=True)
        ret.append(r)
    return dict(ret=ret)

@auth.requires(auth.has_membership(role='manager'))
def rename_activity():
    response.view = 'generic.html'
    form = SQLFORM.factory(
            Field("old", default="pydos y pytres, todo junto"),
            Field("new", default="Código compatible con python 2 y 3, en el mismo fuente"),
            )
    ret = []       
    if form.accepts(request.vars, session, keepvalues=True):
        old = form.vars.old
        new = form.vars.new
        for user in  db(db.auth_user.tutorials.like('%%|%s|%%'%old)).select():
            tutorials = user.tutorials
            if tutorials and old in tutorials:
                tutorials.remove(form.vars.old)
                tutorials.append(form.vars.new)
                db(db.auth_user.id==user.id).update(tutorials=tutorials)
    
                ret.append((user.id, tutorials))
    return dict(ret=ret, q=len(ret), form=form)

@auth.requires(auth.has_membership(role='manager'))
def missing_activity():
    response.view = 'generic.html'
    ret = []    
    q=0   
    tutorials = [a.title for a in db(db.activity).select(db.activity.title)]
    for user in  db(db.auth_user).select():
        if user.tutorials:
            q+=1
            for tutorial in user.tutorials:
                if tutorial not in tutorials and tutorial not in ret:
                    ret.append(tutorial)
    return dict(ret=ret, q=q)


@auth.requires(auth.has_membership(role='manager'))
def activity_accept_bulk():
    ids = """
11
37
40
46
9
""".split("\n")

    for id in ids:
        if id.strip():
            db(db.activity.id==id).update(status="accepted")

    return ids

@auth.requires(auth.has_membership(role='manager'))
def activity_grid():
    q = db.activity.id>0
    form = SQLFORM.smartgrid(db(q).select())
    response.view = 'generic.html'
    return dict(form=form)

# badges/labels/certs

@auth.requires(auth.has_membership(role='manager'))
def create_badge():
    response.view = 'generic.html'
    pdf_template_id = db.pdf_template.insert(title="sample badge", format="A4")

    # configure optional background image and insert his element
    path_to_image = '/home/www-data/web2py/applications/2012/static/badges/images/pyconar2012.png'
    if path_to_image:
        db.pdf_element.insert(pdf_template_id=pdf_template_id, name='background', type='I', x1=0.0, y1=0.0, x2=74.312, y2=105.000, font='Arial', size=10.0, bold=False, italic=False, underline=False, foreground=0, background=16777215, align='L', text=path_to_image, priority=-1)
    # insert name, company_name, number and attendee type elements:
    db.pdf_element.insert(pdf_template_id=pdf_template_id, name='name', type='T', x1=4.0, y1=35.0, x2=62.0, y2=40.0, font='Arial', size=12.0, bold=True,       italic=False, underline=False, foreground=0, background=16777215, align='L', text='', priority=0)
    db.pdf_element.insert(pdf_template_id=pdf_template_id, name='company_name', type='T', x1=4.0, y1=43.0, x2=50.0, y2=47.0, font='Arial', size=10.0, bold=False, italic=False, underline=False, foreground=0, background=16777215, align='L', text='', priority=0)
    db.pdf_element.insert(pdf_template_id=pdf_template_id, name='no', type='T', x1=4.0, y1=47.0, x2=80.0, y2=50.0, font='Arial', size=10.0, bold=False, italic=False, underline=False, foreground=0, background=16777215, align='R', text='', priority=0)
    db.pdf_element.insert(pdf_template_id=pdf_template_id, name='attendee_type', type='T', x1=4.0, y1=47.0, x2=50.0, y2=50.0, font='Arial', size=10.0, bold=False, italic=False, underline=False, foreground=0, background=16777215, align='L', text='', priority=0)
    return dict(pdf_template_id=pdf_template_id)


@auth.requires(auth.has_membership(role='manager'))
def info():
    return {'request': request, 'response': response, 'session': session}

@auth.requires(auth.has_membership(role='manager'))
def create_cert():
    pdf_template_id = db.pdf_template.insert(title="sample cert", format="A4")

    # configure optional background image and insert his element (remove alpha channel!!)
    import os
    path_to_image = os.path.join(request.folder, 'static', 'background_cert_speaker_image.png')
    if path_to_image:
        db.pdf_element.insert(pdf_template_id=pdf_template_id, name='background', type='I', x1=0.0, y1=0.0, x2=210, y2=297, font='Arial', size=10.0, bold=False, italic=False, underline=False, foreground=0, background=16777215, align='L', text=path_to_image, priority=-1)
    # insert name, company_name, number and attendee type elements:
    db.pdf_element.insert(pdf_template_id=pdf_template_id, name='name', type='T', x1=93, y1=210-136, x2=297, y2=210-126, font='Arial', size=12.0, bold=True, italic=False, underline=False, foreground=0, background=16777215, align='L', text='', priority=0)
    return dict(pdf_template_id=pdf_template_id)


@auth.requires_membership(role='manager')
def copy_labels():
    # read base label/badge elements from db
    elements = db(db.pdf_element.pdf_template_id==1).select(orderby=db.pdf_element.priority)
    # setup initial offset and width and height:
    x0, y0 = 10, 10
    dx, dy = 75, 105
    sx = [0, 0, 2, 2] # 2mm separation between col 2 and 3
    sy = [0, 0, 0, 0]
    # create new template to hold several labels/badges:
    rows, cols = 4,  4
    pdf_template_id = int(request.args[0])# db.pdf_template.insert(title="sample badge %s rows %s cols" % (rows, cols), format="A4")
    db(db.pdf_element.pdf_template_id==pdf_template_id).delete()
    # copy the base elements:
    k = 0
    for i in range(rows):
        for j in range(cols):
            k += 1
            for element in elements:
                e = dict(element)
                if e['name']=='background' and not 'background' in request.args:
                    continue
                e['name'] = "%s%02d" % (e['name'], k)
                e['pdf_template_id'] = pdf_template_id
                e['x1'] = e['x1'] + x0 + dx*j + sx[j]
                e['x2'] = e['x2'] + x0 + dx*j + sx[j]
                e['y1'] = e['y1'] + y0 + dy*i + sx[i]
                e['y2'] = e['y2'] + y0 + dy*i + sx[i]
                del e['update_record']
                del e['delete_record']
                del e['id']
                db.pdf_element.insert(**e)
    response.view = "generic.html"
    return {'new_pdf_template_id': pdf_template_id}


@auth.requires_membership(role='manager')
def copy_temp():
    # read base label/badge elements from db
    pdf_template_id = 4
    elements = db(db.pdf_element.pdf_template_id==3).select(orderby=db.pdf_element.priority)
    for element in elements:
        e = dict(element)
        e['pdf_template_id'] = pdf_template_id
        del e['update_record']
        del e['delete_record']
        del e['id']
        db.pdf_element.insert(**e)
    return {'new_pdf_template_id': pdf_template_id}

@auth.requires_membership(role='manager')
def update_username():
    for row in db(db.auth_user.id>0).select():
        db(db.auth_user.id==row.id).update(username=row.email)
    return "ok"

@auth.requires_membership(role='reviewer')
def authors_stats():
    q = db.author.activity_id==db.activity.id
    q &= ((db.activity.type.contains('talk'))|(db.activity.type=='tutorial'))
    ##q &= (db.activity.status=='pending')    
    q &= db.auth_user.id==db.author.user_id
    qty=db.activity.id.count()#.with_alias('qty')
    rows = db(q).select(db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name, 
                        qty, 
                        groupby=db.auth_user.id|db.auth_user.first_name|db.auth_user.last_name,
                        orderby=~qty)
    response.view = "generic.html"
    return {'rows': rows, 'authors': len(rows)}


@auth.requires_membership(role='manager')
def activity_votes_to_partakers():
    rows = db(db.activity.status=='accepted').select(
            db.activity.id, 
            db.activity.title, 
            orderby=db.activity.title)
    
    activities= list(rows)
    
    participation = {}
    for row in db(db.partaker).select():
        participation.setdefault(row.user_id, []).append(row.activity)
    
    ret = 0
    for user in db(db.auth_user).select():
        for activity in activities:
            voted = (user.tutorials and activity.title in user.tutorials)
            if voted and ( user.id not in participation or activity.id not in participation[user.id]):
                db.partaker.insert(user_id=user.id, activity=activity.id, add_me=True, comment="user vote")
                ret += 1
   
    
    return str(ret)

@auth.requires_membership(role='manager')
def insert_partakers():
    "insert participation records from external sources (special activities)"
    
    form = SQLFORM.factory(
        Field("activity_id", db.activity, 
              default=137,
              requires=IS_IN_DB(db, db.activity.id, "%(title)s")),
        Field("emails", "text"),
        Field("comment", "string", default="registrado en el pgday"),
        )
        
    ret = []
    if form.accepts(request.vars, session):
        participation = {}
        for row in db(db.partaker.activity==form.vars.activity_id).select():
            participation[row.user_id] = row.add_me
        
        for email in form.vars.emails.split():
            if email[-1]==",":
                email = email[:-1]
            user = db(db.auth_user.email==email).select().first()
            if user:
                if user.id in participation and not participation[user.id]:
                    q = db.partaker.user_id==user.id
                    q &= db.partaker.activity==form.vars.activity_id
                    r = db(q).update(add_me=True)
                    ret.append("%s %s: update %s" % (user.id, email, r))
                if user.id not in participation:
                    db.partaker.insert(user_id=user.id, activity=form.vars.activity_id, add_me=True, comment=form.vars.comment)
                    ret.append("%s %s: isert" % (user.id, email))
      
    response.view = "generic.html"
    return dict(form=form, ret=ret)

@auth.requires_membership(role='manager')
def update_attendee_types():
    if 'reset' in request.args:
        db(db.auth_user.id>0).update(attendee_type="gratis")
    q = db.payment.id>0
    q |= db.auth_user.id>0
    q |= db.coupon.id>0
    rows=db(q).select(left=[db.auth_user.on(db.payment.from_person==db.auth_user.id), db.coupon.on(db.coupon.used_by==db.payment.from_person)], orderby=~db.payment.modified_on)
    i=0
    for p in rows:
        if not (p.payment.status.lower() not in ('done', 'credited') or p.payment.rate in ('gratis', 'test', None)):
            db(db.auth_user.id==p.payment.from_person).update(attendee_type=p.payment.rate)
            i+=1
    response.view = "generic.html"
    return {'i': i}

#############################################
# activities (activity proposal)
#############################################

if request.function in ("propose", "update") and (not auth.has_membership("manager")):
    db.activity.duration.readable = db.activity.duration.writable = False

if CFP:
    db.activity.duration.readable = db.activity.duration.writable = False
    db.activity.track.readable = db.activity.track.writable = False
    # db.activity.logo.writable = db.activity.readable = False
    db.activity.logo.writable = db.activity.logo.readable = False

# we are not in default controller, change it at crud
if not request.function in ('accepted', 'proposed', 'ratings', 'vote'):
    crud=Crud(globals(),db)
    crud.settings.controller='activity'

@auth.requires_login()
def index():
    activities=db(db.activity.id>0).select(orderby=~db.activity.modified_on)
    rows = db(db.review.created_by==auth.user.id).select()
    reviews = dict([(row.activity_id, row) for row in rows])

    query = (db.auth_user.id==db.activity.created_by)
    rows=db(query).select(db.auth_user.ALL)
    authors = dict([(row.id, row) for row in rows])
    
    d = dict(activities=activities, reviews=reviews, authors=authors)
    return response.render(d)

@auth.requires(auth.has_membership(role='reviewer') or TODAY_DATE>REVIEW_DEADLINE_DATE)
def ratings():
    query = (db.auth_user.id==db.activity.created_by)
    activities_author = db(query).select(db.auth_user.ALL, db.activity.ALL)
    rows = db(db.review.id>0).select(
        db.review.activity_id,
        db.review.rating.sum(), 
        db.review.rating.count(), 
        groupby=(db.review.activity_id,),
        )
    ratings = {}

    for row in rows:
        s = row[db.review.rating.sum()]
        c = row[db.review.rating.count()]
        ratings[row.review.activity_id] = {
            'avg': c and s/float(c), 
            'sum': s, 
            'count': c,
            }

    votes = {}
    tutorial_list = [r.activity.title for r in activities_author]
    for k,item in enumerate(tutorial_list ):
        m=db(db.auth_user.tutorials.like('%%|%s|%%'%item)).count()
        votes[item] = m
                
    ##ratings = sorted(ratings, key=lambda row: (row["SUM(review.rating)"] / float(row["COUNT(review.rating)"]), row["COUNT(review.rating)"]), reverse=True)     
    d = dict(activities_author =activities_author , ratings=ratings, votes=votes, levels=ACTIVITY_LEVEL_HINT)
    return response.render(d)

@auth.requires_login()
def vote():
    if ALLOW_VOTE == False:
        response.generic_patterns = ["*",]
        return dict(message=H3(T("Voting is disabled")))

    import random
    
    rows = db(db.activity.status=='pending').select(
            db.activity.id, 
            db.activity.title, 
            db.activity.authors, 
            db.activity.level, 
            db.activity.abstract,
            db.activity.categories, 
            db.activity.created_by,
            db.activity.type,
            db.activity.track,
            orderby=db.activity.title)
    
    activities = {}
    rows = list(rows)
    random.shuffle(rows)
    
    fields = []
    for activity_type in ACTIVITY_TYPES:
        if activity_type in ('panel', 'poster', 'plenary', 'project'):
            continue
        for track in ACTIVITY_TRACKS:
            activities_filtered = [act for act in rows if act.type == activity_type and act.track==track]
            if not activities_filtered:
                continue
            fields.append(H3(T(activity_type), " - track ", T(track).lower()))    
            
            for row in activities_filtered:
                activities[row.id] = row.title
                activity = row
                author = db.auth_user[activity.created_by]
                u = PluginMModal(title="%s, %s" % (author.last_name, author.first_name),
                    content=(author.photo and IMG(_alt=author.last_name, 
                                                  _src=URL(r=request,c='default',f='fast_download', args=author.photo),  
                                                  _width="100px",_height="100px", 
                                                  _style="margin-left: 5px; margin-right: 5px; margin-top: 3px; margin-bottom: 3px; float: left; "
                             ).xml() or '')+MARKMIN(author.resume or '').xml(),close=T('close'),width=50,height=50)
                a = PluginMModal(title=activity.title,content=MARKMIN(activity.abstract or '').xml(),close=T('close'),width=50,height=50)
                fields.append(a)
                fields.append(u)
                fields.append(LI(
                    INPUT(_name='check.%s' % row.id, 
                          _type="checkbox", 
                          value=(auth.user.tutorials and row.title in auth.user.tutorials) and "on" or "",
                          ),
                    LABEL(a.link(activity.title), " ",  
                          ACTIVITY_LEVEL_HINT[row.level],
                          I(" %s " % (', '.join(row.categories or []) ), " (", u.link(activity.authors), ")"),
                          _for='check.%s' % row.id),
                    ))
        
        
    form = FORM(UL(fields, INPUT(_type="submit"), _class="checklist"))
        
    selected = []
    if form.accepts(request.vars, session):
        session.flash = T('Voto Aceptado!')
        for var in form.vars.keys():
            activity_id = "." in var and int(var.split(".")[1]) or None
            val = form.vars[var]
            if val == 'on':
                selected.append(activities[activity_id])
        auth.user.update(tutorials=selected)
        db(db.auth_user.id==auth.user.id).update(tutorials=selected)
        db.commit()
        redirect(URL(c="default", f="index"))

    elif form.errors:
        response.flash = 'form has errors'

    return dict(form=form, levels=ACTIVITY_LEVEL_HINT, message=db.auth_user.tutorials.comment)

@caching
def accepted():
    db.activity['represent']=lambda activity: A('%s by %s' % (activity.title,activity.authors),
       _href=URL(r=request,f='activity_info',args=[activity.id]))
    query=(db.activity.status=='accepted')&(db.auth_user.id==db.activity.created_by)
    
    activities = ('keynote','panel','tutorial',
                 'talk','extreme talk', 'poster', 'workshop')
                 
    # change the next line for GAE
    query &= (db.activity.type.belongs(activities))
    
    if request.args:
        query &=  db.activity.id==request.args[0]
    rows=db(query).select(orderby=db.activity.title)
    attachments=db(db.attachment.id>0).select()     
    attachs = {}
    for attach in attachments:
        attachs.setdefault(attach.activity_id, []).append(attach) 
    d = dict(rows=rows,attachs=attachs)
    return response.render(d)

def check_speaker_profile():

    # refresh user data (warning: session is not changed!)
    auth.user = db.auth_user[auth.user_id]
    
    d = {'first_name': auth.user.first_name,
         'last_name': auth.user.last_name,
         'email':auth.user.email,
         'bio': auth.user.resume, 
         'photo': auth.user.photo,
         'country': auth.user.country,
         'city': auth.user.city,
         'state': auth.user.state,
         'phone_number': auth.user.phone_number,
         }
    
    err = []
    for k, v in d.items():
        if not v: err.append(str(T(k)))
    if err:
        session.flash = "Debe completar previamente su perfil de disertante (%s)!" % ', '.join(err)
        redirect(URL(c="user", f="profile", args=["speaker"]))
    return 'Ok'
   
@auth.requires_login()
def propose():

    check_speaker_profile()
    if request.args:
        activity_type = len(request.args) > 0 and request.args[0].replace("_", " ")
        duration = ACTIVITY_DURATION.get(request.args[0].replace("_", " "))
        track = len(request.args) > 1 and request.args[1]
        if track:
            db.activity.track.default = track
        if activity_type:
            db.activity.type.default = activity_type
        if duration is not None:
            db.activity.duration.default = duration
            db.activity.duration.writable = False
            db.activity.type.writable = False
        elif not activity_type:
            db.activity.type.requires=IS_IN_SET((T("talk"), T("extreme_talk"), T("tutorial"), T("sprint"), T("poster")))

    # TODO:  one-to-many author/activity relations
    insert_author = lambda form: db.author.insert(user_id=auth.user_id,activity_id=form.vars.id)

    # check deadline per activity type    
    def my_form_processing(form):
        activity_type = form.vars.type
        deadline = PROPOSALS_DEADLINE_DATE_PER_ACTIVITY_TYPE.get(activity_type)
        if deadline and deadline<request.now:
           form.errors.type = T('%s submission closed on %s') % (activity_type, deadline)
           
    validate = lambda form: db.author.insert(user_id=auth.user_id,activity_id=form.vars.id)

    form = crud.create(db.activity, next='display/[id]', # formstyle="bootstrap",
                       onvalidation=my_form_processing,
                       onaccept=[insert_author, email_author])
    # add client-side validations
    client_side_validate(form, db.activity)

    return dict(form=form)

@auth.requires(auth.has_membership(role='manager') or (user_is_author() and TODAY_DATE<PROPOSALS_DEADLINE_DATE))
def update():
    deletable = db.activity.title.writable = not ALLOW_VOTE
    if not db(db.activity.created_by==auth.user.id and db.activity.id==request.args[0]).count():
        redirect(URL(r=reuqest,f='index'))
    check_speaker_profile()
    form=crud.update(db.activity, request.args[0],
                     next='display/[id]',
                     ondelete=lambda form: redirect(URL(r=request,f='index')),
                     deletable=deletable)
    return dict(form=form)

@auth.requires(auth.has_membership(role='manager') or user_is_author() or auth.has_membership(role='reviewer'))
def display():
    activity_id=request.args[0]
    rows = db(db.activity.id==activity_id).select()
    activity = rows[0]
    item=crud.read(db.activity,activity_id)
    q = db.auth_user.id==db.author.user_id
    q &= db.author.activity_id==activity_id
    authors = db(q).select(db.auth_user.ALL)
    comments=db(db.comment.activity_id==activity_id).select()
    attachments=db(db.attachment.activity_id==activity_id).select()
    query = db.review.activity_id==activity_id
    if not auth.has_membership(role='manager') and TODAY_DATE<REVIEW_DEADLINE_DATE:
        query &= db.review.created_by==auth.user.id
    reviews=db(query).select()

    return dict(activity_id=activity_id,activity=activity,item=item,reviews=reviews,attachments=attachments,comments=comments, authors=authors)


@auth.requires(auth.has_membership(role='reviewer') or activity_is_accepted())
def info():
    activity_id=request.args[0]
    item=crud.read(db.activity,activity_id)
    return dict(item=item)

@auth.requires(auth.has_membership(role='manager')  or auth.has_membership(role='reviewer') or user_is_author())
def comment():
    ##session.flash = "los comentarios estan deshabilitados temporalmente, por favor reintente luego"
    ##redirect(URL('display', args=request.args[0]))
    activity = db(db.activity.id==request.args[0]).select()[0]
    db.comment.activity_id.default=activity.id
    form=crud.create(db.comment, 
                     next=URL(r=request,f='display',args=activity.id), onaccept=email_author)
    return dict(activity=activity,form=form)

@auth.requires(auth.has_membership(role='reviewer') or user_is_author())
def attach(): 
    activity = db(db.activity.id==request.args[0]).select()[0]
    db.attachment.activity_id.default=activity.id
    if len(request.args)>1:
        attachs = db((db.attachment.activity_id==activity.id)&(db.attachment.id==request.args[1])).select()
    else:
        attachs = None
    if attachs:
        form=crud.update(db.attachment, attachs[0].id,
                         next=URL(r=request,f='display',args=activity.id),
                         ondelete=lambda form: redirect(URL(r=request,c='default',f='index')))
    else:
        form=crud.create(db.attachment, 
                         next=URL(r=request,f='display',args=activity.id))
    return dict(activity=activity,form=form)

@auth.requires(auth.has_membership(role='reviewer') and not user_is_author() and TODAY_DATE<REVIEW_DEADLINE_DATE)
def review(): 
    activity = db(db.activity.id==request.args[0]).select()[0]
    reviews = db((db.review.activity_id==activity.id)&(db.review.created_by==auth.user_id)).select()
    
    #  onaccept=email_author
    if reviews:
        form=crud.update(db.review, reviews[0].id,
                         next=URL(r=request,f='proposed'),
                         ondelete=lambda form: redirect(URL(r=request,c='default',f='index')),)
    else:
        db.review.activity_id.default=activity.id
        form=crud.create(db.review, 
                         next=URL(r=request,f='proposed'))
    return dict(activity=activity,form=form)


@auth.requires((auth.has_membership(role='manager') or user_is_author()) and TODAY_DATE>REVIEW_DEADLINE_DATE)
def confirm(): 
    activity_id = request.args[0]
    activity = db.activity[activity_id]
    activity.update_record(confirmed=True)
    
    email_author(None)
    
    session.flash = T("Activity %s Confirmed. Thank you!" % (activity.title))
    redirect(URL(r=request,f='display',args=activity_id))

@auth.requires(auth.has_membership(role='manager') or user_is_author())
def add_author(): 
    activity_id = request.args[0]
    # for privacy, do not list users that didn't want to make his attendance public
    delegates = db(db.auth_user.include_in_delegate_listing==True).select(db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name)
    delegates = [(user.id, "%(last_name)s, %(first_name)s" % user) for user in delegates]
    delegates.sort(key=lambda x: x[1].upper())
    form = SQLFORM.factory(
        Field("activity_id", db.activity, label=T("Activity"), writable=False,
              requires=IS_IN_DB(db, db.activity, "%(title)s"),
              represent=lambda x: (db.activity[x].title),
              default=activity_id),
        Field("user_id", db.auth_user, label=T("Author"),
              requires=IS_IN_SET(delegates),),
        )
    if form.accepts(request.vars, session):
        user_id = form.vars.user_id
        q = db.author.activity_id==activity_id
        q &= db.author.user_id==user_id
        if not db(q).count():
            db.author.insert(activity_id=activity_id, user_id=user_id)
            session.flash = "Author added!"
        else:
            session.flash = "Author already added!"
        redirect(URL(r=request,f='display',args=activity_id))
    elif form.errors:
        request.flash = "Form has errors"
    return dict(form=form)
    
@caching
def speakers():
    if request.args:
        q = db.auth_user.id == request.args[0]
    else:
        q = db.auth_user.speaker==True
    s=db(q)
    authors=s.select(db.auth_user.ALL,
                  orderby=db.auth_user.last_name|db.auth_user.first_name)
    activities = ('keynote','panel','tutorial',
                 'talk','extreme talk', 'poster', 'workshop')
    q = (db.activity.id==db.author.activity_id)&(db.activity.status=='accepted')
    q &= db.activity.type.contains(activities)             
    rows = db(q).select()
    activities_by_author = {}
    for row in rows:
        activities_by_author.setdefault(row.author.user_id, []).append(row.activity) 
    return dict(authors=authors, activities_by_author=activities_by_author)

def download(): 
    if not request.args:
        raise HTTP(404)
    query = (db.attachment.file==request.args[0])&(db.activity.id==db.attachment.activity_id)
    activity = db(query).select(db.activity.id,db.activity.status).first()
    if not activity:
        raise HTTP(404)
    if activity.status=='accepted' or auth.has_membership(role='reviewer') or user_is_author(activity.id):
        return response.download(request,db)
    raise HTTP(501)

def email_author(form):
    to = subject = text = cc = None
    user = "%s %s" % (auth.user.first_name, auth.user.last_name)
    backup = None
    if isinstance(user, unicode):
        user = user.encode('utf-8', 'replace')
    if request.function == "propose":
        cc = [text.strip() for text in ON_PROPOSE_EMAIL.split(";") if "@" in text]
        for c in (form.vars.cc or '').split(";"):
            if (not c.strip() in cc) and ("@" in c):
                cc.append(c)
        activity = db.activity[form.vars.id]
        tvars = dict(activity=activity.title, user=user, link=URL(r=request,f='display',args=activity.id, scheme=True, host=True))
        text = PROPOSE_NOTIFY_TEXT % tvars
        subject = PROPOSE_NOTIFY_SUBJECT % tvars
    elif request.function == "comment":
        activity = db.activity[request.args[0]]
        tvars = dict(activity=activity.title, user=user, link=URL(r=request,f='display',args=activity.id, scheme=True, host=True))        
        tvars["comment"] = form.vars.body
        text = COMMENT_NOTIFY_TEXT % tvars
        subject = COMMENT_NOTIFY_SUBJECT % tvars
        to = activity.created_by.email
    elif request.function == "review":
        activity = db.activity[request.args[0]]
        tvars = dict(activity=activity.title, user=user, link=URL(r=request,f='display',args=activity.id, scheme=True, host=True))
        tvars["review"] = form.vars.body
        tvars["rating"] = form.vars.rating
        text = REVIEW_NOTIFY_TEXT % tvars
        subject = REVIEW_NOTIFY_SUBJECT % tvars
        to = activity.created_by.email
    elif request.function == "confirm":
        # confirm forms are None
        activity = db.activity[request.args[0]]
        tvars = dict(activity=activity.title, user=user, link=URL(r=request,f='display',args=activity.id, scheme=True, host=True))
        text = CONFIRM_NOTIFY_TEXT % tvars
        subject = CONFIRM_NOTIFY_SUBJECT % tvars
        to = activity.created_by.email
    if to is None:
        to = auth.user.email
    if to:
        db.commit()   # just in case, save the changes to the db if email fails
        if activity:
            backup = "\n".join(["%s: %s" % (field, activity[field]) for field in db.activity.fields()])
        notify(subject, text, to=to, cc=cc)
        if ACTIVITY_BACKUP_TO and backup and (request.function in ("propose", "update")):
            backup = """
%(note)s

%(backup)s""" % dict(note=T("Following is a copy of the submitted data"), backup=backup)
            notify(subject, backup, to=ACTIVITY_BACKUP_TO, cc=cc)

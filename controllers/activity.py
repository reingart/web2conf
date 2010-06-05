#############################################
# activities (activity proposal)
#############################################

# we are not in default controller, change it at crud
crud.settings.controller='activity'

@auth.requires_login()
def proposed():
    activities=db(db.activity.id>0).select(orderby=db.activity.title)
    return dict(activities=activities)

def accepted():
    db.activity['represent']=lambda activity: A('%s by %s' % (activity.title,activity.authors),
       _href=URL(r=request,f='activity_info',args=[activity.id]))
    query=(db.activity.status=='accepted')&(db.auth_user.id==db.activity.created_by)
    rows=db(query).select(orderby=db.activity.scheduled_datetime)
    attachments=db(db.attachment.id>0).select()     
    attachs = {}
    for attach in attachments:
        attachs.setdefault(attach.activity_id, []).append(attach) 
    return dict(rows=rows,attachs=attachs)

@auth.requires_login()
def propose():
    insert_author = lambda form: db.author.insert(user_id=auth.user_id,activity_id=form.vars.id)
    return dict(form=crud.create(db.activity, 
                                 next='display/[id]', 
                                 onaccept=insert_author))

@auth.requires(auth.has_membership(role='manager') or user_is_author())
def update():
    if not db(db.activity.created_by==auth.user.id and db.activity.id==request.args[0]).count():
        redirect(URL(r=reuqest,f='index'))
    form=crud.update(db.activity, request.args[0],
                     next='display/[id]',
                     ondelete=lambda form: redirect(URL(r=request,f='index')))
    return dict(form=form)

@auth.requires(auth.has_membership(role='manager') or user_is_author())
def display():
    activity_id=request.args[0]
    rows = db(db.activity.id==activity_id).select()
    item=crud.read(db.activity,activity_id)
    comments=db(db.comment.activity_id==activity_id).select()
    attachments=db(db.attachment.activity_id==activity_id).select()
    reviews=db(db.review.activity_id==activity_id).select()
    return dict(activity_id=activity_id,item=item,reviews=reviews,attachments=attachments,comments=comments)


@auth.requires(auth.has_membership(role='reviewer') or activity_is_accepted())
def info():
    activity_id=request.args[0]
    item=crud.read(db.activity,activity_id)
    return dict(item=item)

@auth.requires(auth.has_membership(role='reviewer') or user_is_author())
def comment(): 
    activity = db(db.activity.id==request.args[0]).select()[0]
    db.comment.activity_id.default=activity.id
    form=crud.create(db.comment, 
                     next=URL(r=request,f='display',args=activity.id))
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

@auth.requires(auth.has_membership(role='reviewer') or not user_is_author())
def review(): 
    activity = db(db.activity.id==request.args[0]).select()[0]
    reviews = db((db.review.activity_id==activity.id)&(db.review.created_by==auth.user_id)).select()
    if reviews:
        form=crud.update(db.review, reviews[0].id,
                         next=URL(r=request,f='display',args=activity.id),
                         ondelete=lambda form: redirect(URL(r=request,c='default',f='index')))
    else:
        db.review.activity_id.default=activity.id
        form=crud.create(db.review, 
                         next=URL(r=request,f='display',args=activity.id))
    return dict(activity=activity,form=form)

def download(): 
    query = (db.attachment.file==request.args[0])&(db.activity.id==db.attachment.id)
    activity = db(query).select(db.activity.id,db.activity.status)[0]
    if activity.status=='accepted' or auth.has_membership(role='reviewer') or user_is_author(activity.id):
        return response.download(request,db)
    raise HTTP(501)

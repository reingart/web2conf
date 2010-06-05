#############################################
# Events (event proposal)
#############################################

# we are not in default controller, change it at crud
crud.settings.controller='event'

@auth.requires_login()
def proposed():
    events=db(db.event.id>0).select(orderby=db.event.title)
    return dict(talks=events)

def accepted():
    db.event['represent']=lambda event: A('%s by %s' % (event.title,event.authors),
       _href=URL(r=request,f='event_info',args=[event.id]))
    query=(db.event.status=='accepted')&(db.auth_user.id==db.event.created_by)
    rows=db(query).select(orderby=db.event.scheduled_datetime)
    attachments=db(db.attachment.id>0).select()     
    attachs = {}
    for attach in attachments:
        attachs.setdefault(attach.event_id, []).append(attach) 
    return dict(rows=rows,attachs=attachs)

@auth.requires_login()
def propose():
    insert_author = lambda form: db.author.insert(user_id=auth.user_id,event_id=form.vars.id)
    return dict(form=crud.create(db.event, 
                                 next='display/[id]', 
                                 onaccept=insert_author))

@auth.requires(auth.has_membership(role='manager') or user_is_author())
def update():
    if not db(db.event.created_by==auth.user.id and db.event.id==request.args[0]).count():
        redirect(URL(r=reuqest,f='index'))
    form=crud.update(db.event, request.args[0],
                     next='display/[id]',
                     ondelete=lambda form: redirect(URL(r=request,f='index')))
    return dict(form=form)

@auth.requires(auth.has_membership(role='manager') or user_is_author())
def display():
    event_id=request.args[0]
    rows = db(db.event.id==event_id).select()
    item=crud.read(db.event,event_id)
    comments=db(db.comment.event_id==event_id).select()
    attachments=db(db.attachment.event_id==event_id).select()
    reviews=db(db.review.event_id==event_id).select()
    return dict(event_id=event_id,item=item,reviews=reviews,attachments=attachments,comments=comments)


@auth.requires(auth.has_membership(role='reviewer') or event_is_accepted())
def info():
    event_id=request.args[0]
    item=crud.read(db.event,event_id)
    return dict(item=item)

@auth.requires(auth.has_membership(role='reviewer') or user_is_author())
def comment(): 
    event = db(db.event.id==request.args[0]).select()[0]
    db.comment.event_id.default=event.id
    form=crud.create(db.comment, 
                     next=URL(r=request,f='display',args=event.id))
    return dict(event=event,form=form)

@auth.requires(auth.has_membership(role='reviewer') or user_is_author())
def attach(): 
    event = db(db.event.id==request.args[0]).select()[0]
    db.attachment.event_id.default=event.id
    if len(request.args)>1:
        attachs = db((db.attachment.event_id==event.id)&(db.attachment.id==request.args[1])).select()
    else:
        attachs = None
    if attachs:
        form=crud.update(db.attachment, attachs[0].id,
                         next=URL(r=request,f='display',args=event.id),
                         ondelete=lambda form: redirect(URL(r=request,c='default',f='index')))
    else:
        form=crud.create(db.attachment, 
                         next=URL(r=request,f='display',args=event.id))
    return dict(event=event,form=form)

@auth.requires(auth.has_membership(role='reviewer') or not user_is_author())
def review(): 
    event = db(db.event.id==request.args[0]).select()[0]
    reviews = db((db.review.event_id==event.id)&(db.review.created_by==auth.user_id)).select()
    if reviews:
        form=crud.update(db.review, reviews[0].id,
                         next=URL(r=request,f='display',args=event.id),
                         ondelete=lambda form: redirect(URL(r=request,c='default',f='index')))
    else:
        db.review.event_id.default=event.id
        form=crud.create(db.review, 
                         next=URL(r=request,f='display',args=event.id))
    return dict(event=event,form=form)

def download(): 
    query = (db.attachment.file==request.args[0])&(db.event.id==db.attachment.id)
    event = db(query).select(db.event.id,db.event.status)[0]
    if event.status=='accepted' or auth.has_membership(role='reviewer') or user_is_author(event.id):
        return response.download(request,db)
    raise HTTP(501)

#############################################
# Events (event proposal)
#############################################


@auth.requires_login()
def proposed():
    events=db(db.event.id>0).select(orderby=db.event.title)
    return dict(events=events)

def accepted():
    db.event['represent']=lambda event: A('%s by %s' % (event.title,event.authors),
       _href=URL(r=request,f='event_info',args=[event.id]))
    query=(db.event.status=='accepted')&(db.auth_user.id==db.event.created_by)
    rows=db(query).select(orderby=db.event.scheduled_datetime)
    attachments=db(db.t2_attachment.table_name=='event').select()     
    attachs = {}
    for attach in attachments:
        attachs.setdefault(attach.record_id, []).append(attach) 
    return dict(rows=rows,attachs=attachs)

@auth.requires_login()
def propose():
    return dict(form=crud.create(db.event, next='display_event/[id]'))

@auth.requires_login()
def update():
    if not db(db.event.created_by==auth.user.id and db.event.id==request.args[0]).count():
        redirect(URL(r=reuqest,f='index'))
    form=crud.update(db.event, request.args[0],
                     next='display_event/[id]',
                     ondelete=lambda form: redirect(URL(r=request,f='index')))
    return dict(form=form)

@auth.requires_login()
def display(): 
    item=t2.display(db.event)
    comments=t2.comments(db.event)
    rows=db(db.event.id==request.args[0]).select()
    if auth.has_membership(role='manager') or (rows and rows[0].created_by==auth.user.id):
        writable=True
    else:
        writable=False
    attachments=t2.attachments(db.event,writable=writable)
    return dict(item=item,comments=comments,attachments=attachments)

def info(): 
    item=t2.display(db.event,query=(db.event.id==auth.user.id)&(db.event.status=='accepted'))
    return dict(item=item)

@auth.requires_login()
def review(): 
    item=t2.display(db.event)
    rows=db(db.event.id==request.args[0]).select()
    if session.reviewer and rows and not rows[0].created_by==auth.user.id:
        writable=True
    else:
        writable=True
    attachments=t2.attachments(db.event,writable=True)
    reviews=t2.reviews(db.event,writable=writable)
    return dict(item=item,reviews=reviews,attachments=attachments)

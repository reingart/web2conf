# coding: utf8

import datetime
now=datetime.datetime.now()

######################################
### MANAGE EVENTS (PROPOSALS)
######################################

db.define_table('event',
    db.Field('authors',label=T("Authors"),default=('%s %s' %(auth.user.first_name, auth.user.last_name)) if auth.user else None),
    db.Field('title',label=T("Title")),
    db.Field('type','text',label=T("Type")),
    db.Field('duration','integer',label=T("Duration"),default=60),
    db.Field('cc',label=T("cc"),length=512),
    db.Field('abstract','text',label=T("Abstract")),
    db.Field('description','text',label=T("Description"),widget=wysiwyg),
    db.Field('categories','text',label=T("Categories")),
    db.Field('level','text',label=T("Level"),represent=lambda x: T(x)),
    db.Field('scheduled_datetime','datetime',label=T("Scheduled Datetime"),writable=False,readable=False),
    db.Field('status',default='pending',label=T("Status"),writable=False,readable=False),
    db.Field('video',length=128,label=T('Video'),default='',writable=False,readable=False),
    db.Field('score','double',label=T("Score"),default=None,readable=False,writable=False),
    db.Field('created_by','integer',label=T("Created By"),readable=False,writable=False,default=auth.user.id if auth.user else 0),
    db.Field('created_on','datetime',label=T("Created On"),readable=False,writable=False,default=request.now),
    db.Field('created_signature',label=T("Created Signature"),readable=False,writable=False,
             default=('%s %s' % (auth.user.first_name,auth.user.last_name)) if auth.user else ''),
    db.Field('modified_by','integer',label=T("Modified By"),readable=False,writable=False,default=auth.user.id if auth.user else 0),
    db.Field('modified_on','datetime',label=T("Modified On"),readable=False,writable=False,default=request.now,update=request.now),
    format='%(title)s',
    migrate=migrate)

db.event.description.display=lambda value: XML(value)
db.event.title.requires=IS_NOT_IN_DB(db,'event.title')
db.event.authors.requires=IS_NOT_EMPTY()
db.event.status.requires=IS_IN_SET(['pending','accepted','rejected'])
db.event.type.requires=IS_IN_SET(EVENT_TYPES)
db.event.type.default=EVENT_TYPES[0]
db.event.level.requires=IS_IN_SET(EVENT_LEVELS)
db.event.level.default=EVENT_LEVELS[0]
db.event.abstract.requires=IS_NOT_EMPTY()
db.event.description.requires=IS_NOT_EMPTY()
db.event.categories.widget=lambda s,v:T2.tag_widget(s,v,EVENT_CATEGORIES)
##db.event.displays=db.proposal.fields
db.event.status.writable=db.event.status.readable=auth.has_membership('manager')
db.event.scheduled_datetime.writable=db.event.scheduled_datetime.readable=auth.has_membership('manager')
db.event.video.writable=db.event.video.readable=auth.has_membership('reviewer')

db.event.represent=lambda event: \
   A('[%s] %s' % (event.status,event.title),
     _href=URL(r=request,c='event',f='display',args=[event.id]))

db.define_table('event_archived',db.event,db.Field('event_proposal',db.event), migrate=migrate)

db.define_table('attachment',
   db.Field('event_id',db.event,label=T('Event'),writable=False),
   db.Field('name','string',label=T('Name')),
   db.Field('description','text',label=T('Description')),
   db.Field('file','upload',label=T('File')),
   db.Field('file_data','blob',default=''),
   db.Field('filename'),
   db.Field('created_by','integer',label=T("Created By"),readable=False,writable=False,default=auth.user.id if auth.user else 0),
   db.Field('created_on','datetime',label=T("Created On"),readable=False,writable=False,default=request.now),
   migrate=migrate)
db.attachment.name.requires=IS_NOT_EMPTY()
db.attachment.file.requires=IS_NOT_EMPTY()
db.attachment.filename.requires=IS_NOT_EMPTY()
db.attachment.filename.comment=T("(new filename for downloads)")

db.define_table('comment',
   db.Field('event_id',db.event,label=T('Event'),writable=False),
   db.Field('body','text',label=T('Body')),
   db.Field('created_signature',label=T("Created Signature"),readable=False,writable=False,
             default=('%s %s' % (auth.user.first_name,auth.user.last_name)) if auth.user else ''),
   db.Field('created_by','integer',label=T("Created By"),readable=False,writable=False,default=auth.user.id if auth.user else 0),
   db.Field('created_on','datetime',label=T("Created On"),readable=False,writable=False,default=request.now),
   migrate=migrate)
db.comment.body.requires=IS_NOT_EMPTY()

db.define_table('review',
   db.Field('event_id',db.event,label=T('Event'),writable=False),
   db.Field('rating','integer',label=T('Rating'),default=0),
   db.Field('body','text',label=T('Body')),
   db.Field('created_by','integer',label=T("Created By"),readable=False,writable=False,default=auth.user.id if auth.user else 0),
   db.Field('created_signature',label=T("Created Signature"),readable=False,writable=False,
             default=('%s %s' % (auth.user.first_name,auth.user.last_name)) if auth.user else ''),
   db.Field('created_on','datetime',label=T("Created On"),readable=False,writable=False,default=request.now),
   migrate=migrate)
db.review.body.requires=IS_NOT_EMPTY()
db.review.rating.requires=IS_IN_SET([str(x) for x in range(0,6)])
## db.review.rating.widget=T2.rating_widget

db.define_table('author',
    db.Field('user_id', db.auth_user),
    db.Field('event_id', db.event),
    db.Field('created_by','integer',label=T("Created By"),readable=False,writable=False,default=auth.user.id if auth.user else 0),
    db.Field('created_on','datetime',label=T("Created On"),readable=False,writable=False,default=request.now),
    migrate=migrate)
    
def user_is_author(event_id=None):
    if not auth.is_logged_in() or (not request.args and event_id is None):
        return False
    if event_id is None:
        event_id = request.args[0]
    if db((db.author.user_id==auth.user_id)&(db.author.event_id==event_id)).count():
        return True

def event_is_accepted():
    if not request.args:
        return False
    if db((db.event.id==request.args[0])&(db.event.status=='accepted')).count():
        return True

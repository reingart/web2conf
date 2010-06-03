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
db.event.represent=lambda event: \
   A('[%s] %s' % (event.status,event.title),
     _href=URL(r=request,c='event',f='display',args=[event.id]))

db.define_table('event_archived',db.event,db.Field('event_proposal',db.event), migrate=migrate)

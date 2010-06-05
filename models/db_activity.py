# coding: utf8

import datetime
now=datetime.datetime.now()

######################################
### MANAGE ACTIVITIES ("TALK" PROPOSALS)
######################################

db.define_table('activity',
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

db.activity.description.display=lambda value: XML(value)
db.activity.title.requires=IS_NOT_IN_DB(db,'activity.title')
db.activity.authors.requires=IS_NOT_EMPTY()
db.activity.status.requires=IS_IN_SET(['pending','accepted','rejected'])
db.activity.type.requires=IS_IN_SET(ACTIVITY_TYPES)
db.activity.type.default=ACTIVITY_TYPES[0]
db.activity.level.requires=IS_IN_SET(ACTIVITY_LEVELS)
db.activity.level.default=ACTIVITY_LEVELS[0]
db.activity.abstract.requires=IS_NOT_EMPTY()
db.activity.description.requires=IS_NOT_EMPTY()
db.activity.categories.requires=IS_IN_SET(ACTIVITY_CATEGORIES,multiple=True)
##db.activity.displays=db.proposal.fields
db.activity.status.writable=db.activity.status.readable=auth.has_membership('manager')
db.activity.scheduled_datetime.writable=db.activity.scheduled_datetime.readable=auth.has_membership('manager')
db.activity.video.writable=db.activity.video.readable=auth.has_membership('reviewer')

db.activity.represent=lambda activity: \
   A('[%s] %s' % (activity.status,activity.title),
     _href=URL(r=request,c='activity',f='display',args=[activity.id]))

db.define_table('activity_archived',db.activity,db.Field('activity_proposal',db.activity), migrate=migrate)

db.define_table('attachment',
   db.Field('activity_id',db.activity,label=T('ACTIVITY'),writable=False),
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
   db.Field('activity_id',db.activity,label=T('ACTIVITY'),writable=False),
   db.Field('body','text',label=T('Body')),
   db.Field('created_signature',label=T("Created Signature"),readable=False,writable=False,
             default=('%s %s' % (auth.user.first_name,auth.user.last_name)) if auth.user else ''),
   db.Field('created_by','integer',label=T("Created By"),readable=False,writable=False,default=auth.user.id if auth.user else 0),
   db.Field('created_on','datetime',label=T("Created On"),readable=False,writable=False,default=request.now),
   migrate=migrate)
db.comment.body.requires=IS_NOT_EMPTY()

db.define_table('review',
   db.Field('activity_id',db.activity,label=T('ACTIVITY'),writable=False),
   db.Field('rating','integer',label=T('Rating'),default=0),
   db.Field('body','text',label=T('Body')),
   db.Field('created_by','integer',label=T("Created By"),readable=False,writable=False,default=auth.user.id if auth.user else 0),
   db.Field('created_signature',label=T("Created Signature"),readable=False,writable=False,
             default=('%s %s' % (auth.user.first_name,auth.user.last_name)) if auth.user else ''),
   db.Field('created_on','datetime',label=T("Created On"),readable=False,writable=False,default=request.now),
   migrate=migrate)
db.review.body.requires=IS_NOT_EMPTY()
db.review.rating.requires=IS_IN_SET([str(x) for x in range(0,6)])

db.define_table('author',
    db.Field('user_id', db.auth_user),
    db.Field('activity_id', db.activity),
    db.Field('created_by','integer',label=T("Created By"),readable=False,writable=False,default=auth.user.id if auth.user else 0),
    db.Field('created_on','datetime',label=T("Created On"),readable=False,writable=False,default=request.now),
    migrate=migrate)
    
def user_is_author(activity_id=None):
    if not auth.is_logged_in() or (not request.args and activity_id is None):
        return False
    if activity_id is None:
        activity_id = request.args[0]
    if db((db.author.user_id==auth.user_id)&(db.author.activity_id==activity_id)).count():
        return True

def activity_is_accepted():
    if not request.args:
        return False
    if db((db.activity.id==request.args[0])&(db.activity.status=='accepted')).count():
        return True

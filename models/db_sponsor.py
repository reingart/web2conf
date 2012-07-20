# -*- coding: utf-8 -*-

######################################
### Sponsorship
######################################

db.define_table( 'sponsor',
   db.Field('name',label=T("Name"),requires=IS_NOT_IN_DB(db,'sponsor.name')),
   db.Field('number','integer',default=0,requires=IS_NOT_EMPTY(),label=T("Number")),
   db.Field('level','string',requires=IS_IN_SET(SPONSOR_LEVELS), label=T("Level")),
   db.Field('logo','upload'),
   db.Field('url','string',requires=IS_URL()),
   db.Field('contact','string',requires=IS_EMAIL(),label=T("Contact"), comment="email"),   
   db.Field('alt','string',requires=IS_NOT_EMPTY()),
   db.Field('image','upload', comment="Big logo for sponsors page"),
   db.Field('text','text', comment="Long text for program and sponsors page"),
   db.Field('ad','upload', comment="Ad image for the program guide (optional)"),
   db.Field('notes','text', comment="Phone number and other comments"),
   db.Field('active','boolean', default=False, writable=auth.has_membership(role="manager"), readable=False),
   db.Field('created_by',db.auth_user,label=T("Created By"),readable=False,writable=False,default=auth.user.id if auth.user else 0),
   db.Field('created_on','datetime',label=T("Created On"),readable=False,writable=False,default=request.now),
   db.Field('created_signature',label=T("Created Signature"),readable=False,writable=False,
            default=('%s %s' % (auth.user.first_name,auth.user.last_name)) if auth.user else ''),
   db.Field('modified_by','integer',label=T("Modified By"),readable=False,writable=False,default=auth.user.id if auth.user else 0),
   db.Field('modified_on','datetime',label=T("Modified On"),readable=False,writable=False,default=request.now,update=request.now), migrate=migrate, fake_migrate=fake_migrate)

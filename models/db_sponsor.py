# coding: utf8

######################################
### Sponsorship
######################################

db.define_table( 'sponsor',
   db.Field('name',label=T("Name"),requires=IS_NOT_IN_DB(db,'sponsor.name')),
   db.Field('number','integer',requires=IS_NOT_EMPTY(),label=T("Number")),
   db.Field('level','string',requires=IS_IN_SET(SPONSOR_LEVELS)),
   db.Field('logo','upload'),
   db.Field('url','string',requires=IS_URL()),   
   db.Field('contact','string',requires=IS_EMAIL(),label=T("Contact")),   
   db.Field('alt','string',requires=IS_NOT_EMPTY()),
   db.Field('image','upload', comment="Big logo for sponsors page"),
   db.Field('text','text', comment="Long text for program and sponsors page"),
)

# -*- coding: utf-8 -*-

import datetime
now=datetime.datetime.now()

########################################
### Conference events (deadlines, other)
########################################

db.define_table('event',
    Field("starts", "datetime"),
    Field("ends", "datetime"),
    Field("url", requires=IS_EMPTY_OR(IS_URL())),
    Field("title"),
    Field("body", "text",
          comment=T("You can use markmin syntax here"),
          represent=lambda x: MARKMIN(x)),
    Field("tags", "list:string"),
    Field("show", "boolean", default=False),
    migrate=migrate, fake_migrate=fake_migrate)

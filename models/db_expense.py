# coding: utf8

db.define_table( 'expense_form',
    db.Field( 'person', db.auth_user ),
    db.Field( 'event','string', length=20, default='PyCon 09'),
    db.Field( 'created_on','datetime'),
    migrate=migrate,
)

db.expense_form.person.requires=IS_IN_DB(db,'auth_user.id','%(name)s [%(id)s]')

db.define_table( 'expense_item',
    db.Field( 'exp_form', db.expense_form ),
    db.Field( 'seq', 'integer', ),
    db.Field( 'receipt_no', 'integer', default=1 ),
    db.Field( 'receipt_item', 'integer', default=1 ),
    db.Field( 'acct_code','string', length=20, default='video'),
    db.Field( 'description', 'text', default='' ),
    db.Field( 'serial_no', 'string', length=30, default='' ),
    db.Field( 'location', 'text', default='' ),
    db.Field( 'amount', 'double', default='0.00'),
    migrate=migrate)

db.expense_item.exp_form.requires=IS_IN_DB(db,'expense_form.person','%(id)s')

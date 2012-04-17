#############################################
### FOR MANAGERS
#############################################

crud=Crud(globals(),db)

@auth.requires_membership(role='manager')
def _crud():
    crud.settings.controller = 'manage'
    response.view = 'generic.html'
    return dict(form=crud())

crud.settings.controller='manage'
crud.settings.showid=True

@auth.requires_membership(role='manager')
def index():
    return dict(form=crud.tables())

@auth.requires_membership(role='manager')
def select():
    table = request.args[0]
    if auth.is_logged_in():
        f='update'
    else:
        f='read'
    response.view = 'generic.html'
    return dict(form=crud.select(table, linkto=crud.url(f)))
    #crud.select(table, query, fields, orderby, limitby, headers, **attr)

@auth.requires_membership(role='manager')
def read():
    table, record = request.args
    response.view = 'generic.html'
    return dict(form=crud.read(table, record))

@auth.requires_membership(role='manager')
def update():
    table, record = request.args
    response.view = 'generic.html'
    return dict(form=crud.update(table, record, next=crud.url('select', table), deletable=True))

@auth.requires_membership(role='manager')
def create():
    table = request.args[0]
    response.view = 'generic.html'
    return dict(form=crud.create(table, next=crud.url('create', table)))



@auth.requires_membership(role='manager')
def badges():
    rows=db().select(db.auth_user.first_name,
                db.auth_user.first_name,
                db.auth_user.last_name,
                db.auth_user.company_name,
                db.auth_user.state,
                db.auth_user.country,
                db.auth_user.food_preference,
                db.auth_user.speaker,
                db.auth_user.session_chair,
                db.auth_user.manager,
                db.auth_user.reviewer)
    return str(rows)

@auth.requires_membership(role='manager')
def maillist():
    '''
    Create a comma-separated mail list of attendees;
    could expand to create many different lists.
    '''
    rec=db((db.auth_user.amount_due<=0)&(db.auth_user.attendee_type!='non_attending')).select(db.auth_user.email,orderby=db.auth_user.email)
    response.headers['Content-Type']='text/csv'
    ## BUG: (yarko:) str calls csv-writer,
    ##   which on both Ubuntu & Win returns \r\n for newline; need to find & fix
    buggy_newline='\r\n'
    # rec renders column header I don't want:
    return str(rec).partition('\n')[-1].replace(buggy_newline,',\n')

@auth.requires_membership(role='manager')
def attendees_csv():
    '''
    Create a comma-separated mail list of attendees;
    could expand to create many different lists.
    '''
    rec=db((db.auth_user.amount_due<=0)&(db.auth_user.attendee_type!='non_attending')).select(db.auth_user.first_name, db.auth_user.last_name,  db.auth_user.company_name, db.auth_user.city, db.auth_user.state, db.auth_user.country,db.auth_user.email,db.auth_user.speaker,db.auth_user.confirmed,orderby=db.auth_user.last_name)
    response.headers['Content-Type']='text/csv'
    ## BUG: (yarko:) str calls csv-writer,
    ##   which on both Ubuntu & Win returns \r\n for newline; need to find & fix
    buggy_newline='\r\n'
    # rec renders column header I don't want:
    return str(rec).partition('\n')[-1].replace(buggy_newline,',\n') #.decode('utf8').encode('latin1')


@auth.requires_membership(role='manager')
def financials():
    rows=db().select(db.auth_user.ALL,orderby=db.auth_user.first_name|db.auth_user.last_name)
    billed=sum([x.amount_billed for x in rows])
    paid=sum([x.amount_paid for x in rows])
    due=billed-paid
    return dict(rows=rows,billed=billed,paid=paid,due=due)

@auth.requires_membership(role='manager')
def financials_csv():
    t=db.auth_user
    rows=db().select(t.id,t.first_name,t.last_name,t.donation_to_PSF,t.amount_billed,t.amount_added,t.amount_subtracted,t.amount_paid,orderby=t.last_name)
    response.headers['Content-Type']='text/csv'
    return str(rows)

@auth.requires_membership(role='manager')
def payments():
    rows=db(db.payment.status!='PRE-PROCESSING')(db.payment.from_person==db.auth_user.id).select(orderby=~db.payment.created_on)
    return dict(payments=rows)

# Select records for badge
@auth.requires_membership(role='manager')
def badge():
    raise HTTP(501,T("Not implemented"))
##    if not (request.args and request.args[0] in db.tables):
##         redirect(URL(r=request,f='index'))
##    table=request.args[0]
##    db[table]['exposes']=db[table].fields
##    # this is for t2.search; it will start with person.name contains, which is good
##    #   (will disable searching by id - oh well ;-)
##    db[table]['displays']=db[table].fields[1:]
##    db[table]['represent']=lambda item: A(item.id,' :   ',
##        item[db[table].fields[1]],
##    _href=URL(r=request, c='badge', f='badge_pdf', args=[table, item.id]))
##    search=t2.search(db[table])
##    return dict(search=search)


@auth.requires_membership(role='manager')
def fa_csv():
    person=db.auth_user
    fa=db.fa
    who=(person.id==fa.person)
    rows=db(db.fa.id>0).select(person.first_name,person.last_name,person.id,person.address,
                     person.city,person.state,person.zip_code,person.country, person.email, person.attendee_type,
                     fa.registration_amount, fa.hotel_nights, fa.total_lodging_amount, fa.roommates,
                     fa.transportation_details, fa.transportation_amount,
                     fa.total_amount_requested, fa.minimum_amount_requested,fa.rationale,
                     left=db.fa.on(who))  # the all important "join"
    response.headers['Content-Type']='text/csv'
    return str(rows)

@auth.requires_membership(role='manager')
def fa_email_all():
    email_fa_select()
    session.flash="FA Records emailed to %s." % FA_EMAIL_TO
    redirect(URL(r=request,c="default",f='index'))

@auth.requires_membership(role='manager')
def badges():
    p=db.auth_user
    rows=db().select(p.first_name,p.last_name,p.company_name,orderby=p.last_name|p.first_name)
    response.headers['Content-Type']='text/csv'
    return str(rows)

@auth.requires_membership(role='manager')
def update_zips():
    for row in db(db.auth_user).select():
        update_zip(row)


@auth.requires_membership(role='manager')
def list_by_tutorial():
    page=[]
    for key,name in TUTORIALS_LIST:
        rows=db(db.auth_user.tutorials.like('%%|%s|%%'%key)).select(db.auth_user.id,db.auth_user.first_name,db.auth_user.last_name,db.auth_user.food_preference,orderby=db.auth_user.first_name|db.auth_user.last_name)
        page.append(H1(name))
        page.append(rows)
    return HTML(BODY(page))

@auth.requires_membership(role='manager')
def list_by_tutorial_with_food():
    page=[]
    for key,name in TUTORIALS_LIST:
        rows=db(db.auth_user.tutorials.like('%%|%s|%%'%key)).select(db.auth_user.id,db.auth_user.first_name,db.auth_user.last_name,db.auth_user.food_preference,orderby=db.auth_user.first_name|db.auth_user.last_name)
        page.append(H1(name))
        page.append(rows)
    return HTML(BODY(page))

@auth.requires_membership(role='manager')
def by_tutorial_csv():
    page=[]
    for key,name in TUTORIALS_LIST:
        rows=db(db.auth_user.tutorials.like('%%|%s|%%'%key)).select(db.auth_user.id,db.auth_user.first_name,db.auth_user.last_name,db.auth_user.food_preference,orderby=db.auth_user.first_name|db.auth_user.last_name)
        page.append(name)
        page.append(str(rows))
        page.append('\n')
    response.headers['Content-Type']='text/plain'
    return str(page)

@auth.requires_membership(role='manager')
def impersonate():
    person=db(db.auth_user.id==request.args[0]).select()[0]
    balance2=session.balance #trick
    transfers_in,transfers_out,payments=update_pay(person)
    balance=session.balance
    session.balance=balance2 #trick
    charged_payments=[row for row in payments if row.status.lower()=='charged']
    pending_payments=[row for row in payments if row.status.lower()=='submitted']
    ### this is HORRIBLE but las minute change asked by Kurt
    ### donations is (name,email,amount)
    ### amounts is (name,email,conference_fees)
    ### contained in this one payment
    if not charged_payments:
          donations=[(person.first_name+' '+person.last_name,person.id,person.donation_to_PSF)]
          amounts=[(row.auth_user.first_name+' '+row.auth_user.last_name,row.auth_user.id,row.money_transfer.amount) for row in transfers_in]
          amounts.append((person.first_name+' '+person.last_name,person.id,person.amount_billed-donations[0][2]))
    else:
          last_payment_datetime=person.created_on
          for payment in charged_payments:
              if payment.created_on>last_payment_datetime:
                  last_payment_datetime=payment.created_on
          donations=[]
          amounts=[(row.auth_user.first_name+' '+row.auth_user.last_name,row.auth_user.id,row.money_transfer.amount) for row in transfers_in if row.money_transfer.created_on>last_payment_datetime]
          samounts=sum([row[2] for row in amounts])
          amounts.append((person.first_name+' '+person.last_name,person.id,session.balance-samounts))
    transfers_in=[row.money_transfer for row in transfers_in]
    if balance<=0.0: pay=H2(T('No payment due at this time'))
    elif not pending_payments: pay=H2(T('Payment expected'))
    else: pay=H2(T('Your payment is being processed... (read below)'))
    return dict(person=person,transfers_in=transfers_in,
                transfers_out=transfers_out,payments=payments,
                pay=pay,balance=balance)


@auth.requires_membership(role='manager')
def cancel_transfer2():
    if len(request.args)<2: raise HTTP(505)
    try:
         db(db.money_transfer.id==request.args[1]).delete()
         session.flash=T('Transfer cancelled')
         redirect(URL(r=request,f='impersonate',args=request.args[0]))
    except Exception:
         session.flash=T('Invalid operation')
         redirect(URL(r=request,f='impersonate',args=request.args[0]))

@auth.requires_membership(role='manager')
def cancel_payment2():
    if len(request.args)<2: raise HTTP(505)
    try:
         db(db.payment.id==request.args[1]).update(status='CANCELLED')
         session.flash=T('Payment cancelled')
         redirect(URL(r=request,f='impersonate',args=request.args[0]))
    except Exception:
         session.flash=T('Invalid operation')
         redirect(URL(r=request,f='impersonate',args=request.args[0]))

@auth.requires_membership(role='manager')
def control_panel():
    options = db(db.option).select()
    return dict(options=options)


@auth.requires_membership(role='manager')
def option():
    records = None
    format = None
    opt = db.option[request.args(1)]
    if opt.valuetype == "reference":
       table = db[opt.tablename]
       valuetype = table
       requires = IS_EMPTY_OR(IS_IN_DB(db, table))
       records = db(table).select()
       widget = SQLFORM.widgets.options.widget
    else:
       widget = None
       if opt.valuetype == "date":
           widget = SQLFORM.widgets.date.widget
       elif opt.valuetype == "datetime":
           widget = SQLFORM.widgets.datetime.widget
       elif opt.valuetype == "string":
           widget = SQLFORM.widgets.string.widget
       elif opt.valuetype == "text":
           widget = SQLFORM.widgets.text.widget
       elif opt.valuetype == "integer":
           widget = SQLFORM.widgets.integer.widget
       elif opt.valuetype == "double":
           widget = SQLFORM.widgets.double.widget
       elif opt.valuetype == "boolean":
           widget = SQLFORM.widgets.boolean.widget
       elif opt.valuetype == "password":
           widget = SQLFORM.widgets.password.widget
       valuetype = opt.valuetype
       requires = None

    form = SQLFORM.factory(Field("value", valuetype, requires=requires, label=T("Value"), widget = widget))
    form.vars.value = opt.value

    accepted = False

    if form.accepts(request.vars, session):
        if valuetype == "boolean":
            value = bool(request.vars.value)
        else:
            value = request.vars.value
        opt.update_record(value=value)
        response.flash = T("Option changed")
        form = crud.read(db.option, request.args(1))
        accepted = True
        cache.ram.clear()

    return dict(form=form, records=records, opt=opt, accepted=accepted)


@auth.requires_membership(role='plugin_flatpages')
def upload():
    form=FORM(
        INPUT(_type='file', _name='myfile', id='myfile', requires=IS_NOT_EMPTY()),
        INPUT(_type='filename', _name='filename', id='filename', requires=IS_NOT_EMPTY(), _value="static/filename.ext"),
        BR(),
        "Password:",
        INPUT(_type='password', _name='superpassword', id='superpassword', requires=IS_NOT_EMPTY(), _value=""),
        INPUT(_type='submit',_value='Submit'),
        )
    response.view = 'generic.html'
    if form.accepts(request.vars):
        import cStringIO as StringIO
        import os
        filename = str(request.folder) + str(form.vars.filename)
        d = request.vars.myfile.value
        data=request.vars.myfile.file.read()
        if form.vars.superpassword=="saraza":
            f = open(filename,"wb")
            f.write(data)
            f.close()
        ret = dict(filename=filename, request=request, folder=request.folder)

    else:
        ret = dict(form=form, request=request)

    return ret

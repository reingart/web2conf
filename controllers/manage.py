#############################################
### FOR MANAGERS
#############################################

@auth.requires_login()
def _crud():
    if not (session.manager):
        redirect(URL(r=request, c='default', f='index'))
    crud.settings.controller = 'manage'
    return dict(form=crud())


@auth.requires_login()
def badges():
    if not session.manager: t2.redirect('index')
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
    
@auth.requires_login()
def maillist():
    '''
    Create a comma-separated mail list of attendees;
    could expand to create many different lists.
    '''
    if not session.manager: t2.redirect('index')
    rec=db((db.auth_user.amount_due<=0)&(db.auth_user.attendee_type!='non_attending')).select(db.auth_user.email,orderby=db.auth_user.email)
    response.headers['Content-Type']='text/csv'
    ## BUG: (yarko:) str calls csv-writer,
    ##   which on both Ubuntu & Win returns \r\n for newline; need to find & fix
    buggy_newline='\r\n'
    # rec renders column header I don't want:
    return str(rec).partition('\n')[-1].replace(buggy_newline,',\n')

@auth.requires_login()
def attendees_csv():
    '''
    Create a comma-separated mail list of attendees;
    could expand to create many different lists.
    '''
    if not session.manager: t2.redirect('index')
    rec=db((db.auth_user.amount_due<=0)&(db.auth_user.attendee_type!='non_attending')).select(db.auth_user.first_name, db.auth_user.last_name, db.auth_user.dni, db.auth_user.certificate,db.auth_user.email,orderby=db.auth_user.last_name)
    response.headers['Content-Type']='text/csv'
    ## BUG: (yarko:) str calls csv-writer,
    ##   which on both Ubuntu & Win returns \r\n for newline; need to find & fix
    buggy_newline='\r\n'
    # rec renders column header I don't want:
    return str(rec).partition('\n')[-1].replace(buggy_newline,',\n').decode('utf8').encode('latin1')


@auth.requires_login()
def financials():
    if not session.manager: t2.redirect('index')
    rows=db().select(db.auth_user.ALL,orderby=db.auth_user.first_name|db.auth_user.last_name)
    billed=sum([x.amount_billed for x in rows])
    paid=sum([x.amount_paid for x in rows])
    due=billed-paid
    return dict(rows=rows,billed=billed,paid=paid,due=due)

@auth.requires_login()
def financials_csv():
    if not session.manager: t2.redirect('index')
    t=db.auth_user
    rows=db().select(t.id,t.first_name,t.last_name,t.donation_to_PSF,t.amount_billed,t.amount_added,t.amount_subtracted,t.amount_paid,orderby=t.last_name)
    response.headers['Content-Type']='text/csv'
    return str(rows)

@auth.requires_login()
def payments():
    if not session.manager: t2.redirect('index')
    rows=db(db.payment.status!='PRE-PROCESSING')(db.payment.from_person==db.auth_user.id).select(orderby=~db.payment.created_on)
    return dict(payments=rows)

# Select records for badge
@auth.requires_login()
def badge():
    if not (session.manager and request.args and request.args[0] in db.tables):
         t2.redirect('index')
    table=request.args[0]
    db[table]['exposes']=db[table].fields
    # this is for t2.search; it will start with person.name contains, which is good
    #   (will disable searching by id - oh well ;-)
    db[table]['displays']=db[table].fields[1:]
    db[table]['represent']=lambda item: A(item.id,' :   ',
        item[db[table].fields[1]],
    _href=URL(r=request, c='badge', f='badge_pdf', args=[table, item.id]))
    search=t2.search(db[table])
    return dict(search=search)


@auth.requires_login()
def fa_csv():
    if not session.manager: t2.redirect('index')
    person=db.auth_user
    fa=db.fa
    who=(person.id==fa.person)
    rows=db(db.fa.id>0).select(person.first_name,person.last_name,person.id,person.address1,person.address2,
                     person.city,person.state,person.zip_code,person.country, person.email, person.attendee_type,
                     fa.registration_amount, fa.hotel_nights, fa.total_lodging_amount, fa.roommates,
                     fa.transportation_details, fa.transportation_amount,
                     fa.total_amount_requested, fa.minimum_amount_requested,fa.rationale,
                     left=db.fa.on(who))  # the all important "join"
    response.headers['Content-Type']='text/csv'
    return str(rows)

@auth.requires_login()
def fa_email_all():
    if not session.manager: t2.redirect('index')
    email_fa_select()
    session.flash="FA Records emailed to %s." % FA_EMAIL_TO
    t2.redirect('index')
    

@auth.requires_login()
def pay_check(): return dict()

@auth.requires_login()
def pay_other():
    transfers_in=db(db.money_transfer.to_person==auth.user.id).select()
    form=FORM('Tokens: ',INPUT(_name='codes',requires=IS_NOT_EMPTY()),INPUT(_type='submit'))
    errors=[]
    due=0.0
    if form.accepts(request.vars,session):
        for code in request.vars.codes.split(','):
            try:
                id,pay_token=code.strip().split('-')
                if id==auth.user.id: raise Exception
                if int(id) in [r.from_person for r in transfers_in]: raise Exception
                row=db(db.auth_user.id==id).select()[0]
                if not row.pay_token.upper()==pay_token.upper(): raise Exception                
                amount=max(0.0,row.amount_billed-row.amount_paid)
                db.money_transfer.insert(from_person=row.id,
                        to_person=auth.user.id,amount=amount,approved=False,
                        description="%s %s (%s)'s Fees transferred to %s %s (%s)" % (row.first_name, row.last-name, row.id, auth.user.first_name, auth.user.last_name, auth.user.id))
                transfers_in=db(db.money_transfer.to_person==auth.user.id).select()
            except:
                errors.append(code.strip())
        if not errors: t2.redirect('pay',flash=T('Balance transferred'))
        else: response.flash='Invalid Tokens: '+', '.join(errors)
    return dict(form=form,transfers_in=transfers_in)

@auth.requires_login()
def register_other():
    transfers_in=db(db.money_transfer.to_person==auth.user.id).select()
    form=SQLFORM(db.auth_user,fields=['first_name','last_name','email','attendee_type','tutorials','discount_coupon'])
    errors=[]
    due=0.0
    if form.accepts(request.vars,session):
        amount=update_person(form)
        db.money_transfer.insert(from_person=form.vars.id,
                   to_person=auth.user.id,amount=amount,approved=False,
                   description="%s %s (%s) 's Fees transferred to %s %s (%s)" % (form.vars.first_name, form.vars.last_name, form.vars.id, auth.user.first_name,auth.user.last_name,auth.user.id))
        transfers_in=db(db.money_transfer.to_person==auth.user.id).select()
        t2.redirect('pay',flash=T('Attendee registered and balance transferred'))
    return dict(form=form,transfers_in=transfers_in)

@auth.requires_login()
def pay_other_info():
    return dict(person=db(db.auth_user.id==auth.user.id).select()[0])

@auth.requires_login()
def invoice(): return dict(balance=session.balance)

@auth.requires_login()
def badges():
    p=db.auth_user
    rows=db().select(p.first_name,p.last_name,p.company_name,orderby=p.last_name|p.first_name)
    response.headers['Content-Type']='text/csv'
    return str(rows)

def notify():
    response.headers['Content-Type']='text/xml'
    return l2controller.receive_xml(request.body.read())

@auth.requires_login()
def list_by_tutorial():
    if not session.manager: t2.redirect('index')
    page=[]
    for key,name in TUTORIALS_LIST:
        rows=db(db.auth_user.tutorials.like('%%|%s|%%'%key)).select(db.auth_user.id,db.auth_user.first_name,db.auth_user.last_name,db.auth_user.food_preference,orderby=db.auth_user.first_name|db.auth_user.last_name)
        page.append(H1(name))
        page.append(rows)
    return HTML(BODY(page))

def list_by_tutorial_with_food():
    page=[]
    for key,name in TUTORIALS_LIST:
        rows=db(db.auth_user.tutorials.like('%%|%s|%%'%key)).select(db.auth_user.id,db.auth_user.first_name,db.auth_user.last_name,db.auth_user.food_preference,orderby=db.auth_user.first_name|db.auth_user.last_name)
        page.append(H1(name))
        page.append(rows)
    return HTML(BODY(page))

@auth.requires_login()
def by_tutorial_csv():
    if not session.manager: t2.redirect('index')
    page=[]
    for key,name in TUTORIALS_LIST:
        rows=db(db.auth_user.tutorials.like('%%|%s|%%'%key)).select(db.auth_user.id,db.auth_user.first_name,db.auth_user.last_name,db.auth_user.food_preference,orderby=db.auth_user.first_name|db.auth_user.last_name)
        page.append(name)
        page.append(str(rows))
        page.append('\n')
    response.headers['Content-Type']='text/plain'
    return str(page)

@auth.requires_login()
def impersonate():
    if not session.manager or not request.args: t2.redirect('index')
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


@auth.requires_login()
def cancel_transfer2():
    if not session.manager or len(request.args)<2: t2.redirect('index')
    try:
         db(db.money_transfer.id==request.args[1]).delete()
         t2.redirect('impersonate/%s'%request.args[0],flash=T('Transfer cancelled'))
    except Exception:
         t2.redirect('impersonate/%s'%request.args[0],flash=T('Invalid operation'))

@auth.requires_login()
def cancel_payment2():
    if not session.manager or len(request.args)<2: t2.redirect('index')
    try:
         db(db.payment.id==request.args[1]).update(status='CANCELLED')
         t2.redirect('impersonate/%s'%request.args[0],flash=T('Payment cancelled'))
    except Exception:
         t2.redirect('impersonate/%s'%request.args[0],flash=T('Invalid operation'))


#############################################
### general variables
#############################################

from gluon.sqlhtml import form_factory

#############################################
# The main public page
#############################################

def index():
    ##response.files.append(URL(r=request,c='static',f='jquery-slideshow.css'))
    ##response.files.append(URL(r=request,c='static',f='jquery-slideshow.js'))
    return plugin_flatpage()

#############################################
# Manage Authentication
#############################################

def login():
    return dict(form=auth.login(next='index',
                                onaccept=lambda form:update_pay(auth.user)))

def verify():
    return auth.verify_email(next=URL(r=request,f='login'))

def register():
    form=auth.register(next='index',
                       onaccept=update_person)
    return dict(form=form)
                
def password():
    return dict(form=auth.retrieve_password(next='login'))
        

@auth.requires_login()
def logout(): auth.logout(next='index')

@auth.requires_login()
def profile():
    you=db.auth_user.id==auth.user.id
    person=db(you).select()[0]
    require_address(person)
    if person.amount_paid>0 or person.amount_subtracted>0:
        db.auth_user.donation_to_PSF.writable=False
        db.auth_user.attendee_type.writable=False
        db.auth_user.discount_coupon.writable=False
    form=crud.update(db.auth_user,auth.user.id,
                     onaccept=update_person,
                     next='index')
    return dict(form=form)



#############################################
# Submit Financial Aid Application
#############################################

@auth.requires_login()
def fa_app():
    # following idiom from Massimo's profile():
    try:
        you=db.fa.person==auth.user.id
        db.fa['exposes']=db.fa.fields[4:]
        person=db(you).select()[0]
    except:
        if datetime.datetime.today() > FACUTOFF_DATE:
            t2.redirect('index',flash=XML(T('<b><font color="red">Applications are no longer being accepted.</b><br>(Financial Aid Application deadline: 23 February 2009)</font>')))
        form=t2.create(db.fa,vars=dict(person=auth.user.id),onaccept=lambda form: email_fa('created'),next='fa_app')
    else:
        form=t2.update(db.fa,query=you,deletable=False,onaccept=lambda form: email_fa('updated'),next='fa_app')
    # email from here...
    return dict(form=form)
    

#############################################
# Submit payment
#############################################

@auth.requires_login()
def pay():
    person=db(db.auth_user.id==auth.user.id).select()[0]
    balance=session.balance
    pay=H2(T('No payment due at this time'))
    return dict(person=person,transfers_in=[],
                transfers_out=[],payments=[],
                pay=pay,balance=balance)

@auth.requires_login()
def cancel_transfer():
    try:
         db((db.money_transfer.id==request.args[0])&(db.money_transfer.to_person==auth.user.id)&(db.money_transfer.approved==False)).delete()
         t2.redirect('pay',flash=T('Transfer cancelled'))
    except Exception:
         t2.redirect('pay',flash=T('Invalid operation'))


#############################################
# Allow registered visitors to download
#############################################

@auth.requires_login()
def download(): 
    return response.download(request,db)

###@cache(request.env.path_info,60,cache.disk)
def fast_download():
    # very basic security:
    if not request.args(0).startswith("sponsor.logo") and not request.args(0).startswith("t2_attachment.file"): 
        return download()
    if 'filename' in request.vars:
        response.headers["Content-Disposition"] = "attachment; filename=%s" % request.vars['filename'] 

    # remove/add headers that prevent/favors caching
    del response.headers['Cache-Control']
    del response.headers['Pragma']
    del response.headers['Expires']
    filename = os.path.join(request.folder,'uploads',request.args(0))
    response.headers['Last-Modified'] = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime(os.path.getmtime(filename)))
    return response.stream(open(filename,'rb'))

@auth.requires_login()
def proposed_talks():
    talks=db(db.talk.id>0).select(orderby=db.talk.title)
    return dict(talks=talks)

def accepted_talks():
    db.talk['represent']=lambda talk: A('%s by %s' % (talk.title,talk.authors),
       _href=URL(r=request,f='talk_info',args=[talk.id]))
    query=(db.talk.status=='accepted')&(db.auth_user.id==db.talk.created_by)
    rows=db(query).select(orderby=db.talk.scheduled_datetime)
    attachments=db(db.t2_attachment.table_name=='talk').select()     
    attachs = {}
    for attach in attachments:
        attachs.setdefault(attach.record_id, []).append(attach) 
    return dict(rows=rows,attachs=attachs)

@auth.requires_login()
def propose_talk():
    return dict(form=crud.create(db.talk, next='display_talk/[id]'))

@auth.requires_login()
def update_talk():
    if not db(db.talk.created_by==auth.user.id and db.talk.id==request.args[0]).count():
        redirect(URL(r=reuqest,f='index'))
    form=crud.update(db.talk, request.args[0],
                     next='display_talk/[id]',
                     ondelete=lambda form: redirect(URL(r=request,f='index')))
    return dict(form=form)

@auth.requires_login()
def display_talk(): 
    item=t2.display(db.talk)
    comments=t2.comments(db.talk)
    rows=db(db.talk.id==request.args[0]).select()
    if session.manager or (rows and rows[0].created_by==auth.user.id):
        writable=True
    else:
        writable=False
    attachments=t2.attachments(db.talk,writable=writable)
    return dict(item=item,comments=comments,attachments=attachments)

def talk_info(): 
    item=t2.display(db.talk,query=(db.talk.id==auth.user.id)&(db.talk.status=='accepted'))
    return dict(item=item)

@auth.requires_login()
def review_talk(): 
    item=t2.display(db.talk)
    rows=db(db.talk.id==request.args[0]).select()
    if session.reviewer and rows and not rows[0].created_by==auth.user.id:
        writable=True
    else:
        writable=True
    attachments=t2.attachments(db.talk,writable=True)
    reviews=t2.reviews(db.talk,writable=writable)
    return dict(item=item,reviews=reviews,attachments=attachments)



#############################################
### FOR ALL ATTENDEES
#############################################

@cache(request.env.path_info,time_expire=60,cache_model=cache.ram)
def companies():
    if session.manager: s=db()
    else: s=db(db.auth_user.include_in_delegate_listing==True)
    rows=s.select(db.auth_user.company_name,
                  db.auth_user.company_home_page,
                  orderby=db.auth_user.company_name,distinct=True)
    return dict(rows=rows)
    
@cache(request.env.path_info,time_expire=60,cache_model=cache.ram)
def attendees():
    if session.manager: s=db(db.auth_user.attendee_type!='non_attending')
    else: s=db((db.auth_user.include_in_delegate_listing==True)&(db.auth_user.attendee_type!='non_attending')&(db.auth_user.amount_due==0.0))
    rows=s.select(db.auth_user.ALL,
                  orderby=db.auth_user.first_name|db.auth_user.last_name)
    return dict(rows=rows)

@cache(request.env.path_info,time_expire=60,cache_model=cache.ram)
def charts():    
    cn=[]
    colors=['#ff0000','#ff0033','#ff0066','#ff0099','#ff00cc','#ff00ff',
            '#996600','#996633','#996666','#996699','#9966cc','#9966ff',
            '#669900','#669933','#669966','#669999','#6699cc','#cc99ff',
            '#33cc00','#33cc33','#33cc66','#33cc99','#33cccc','#33ccff',
            '#00ff00','#00ff33','#00ff66','#00ff99','#00ffcc','#00ffff',
            '#996600','#996633','#996666','#996699','#9966cc','#9966ff',
            '#669900','#669933','#669966','#669999','#6699cc','#cc99ff',
            '#33cc00','#33cc33','#33cc66','#33cc99','#33cccc','#33ccff',
            '#00ff00','#00ff33','#00ff66','#00ff99','#00ffcc','#00ffff']
    if not is_gae:
        for k,item in enumerate(sorted(TUTORIALS.keys())):
            m=db(db.auth_user.tutorials.like('%%|%s|%%'%item)).count()
            cn.append((TUTORIALS[item],colors[k],m))
    else:        
        cn2={}
        for row in db(db.auth_user.id>0).select(db.auth_user.tutorials):
            for item in sorted(TUTORIALS.keys()):
                    if not cn2.has_key(item): cn2[item]=0
                    if row.tutorials.find('|%s|'%item)>=0: cn2[item]+=1
        for k,item in enumerate(sorted(TUTORIALS.keys())):
                cn.append((TUTORIALS[item],colors[k],cn2[item]))
                k+=1
    chart_tutorials=None #t2.barchart(cn,label_width=150)
    def colorize(d,sort_key=lambda x:x):
        s=[(m,n) for n,m in d.items()]
        s.sort(key=sort_key)
        s.reverse()
            
        t=[(x[1],colors[i % len(colors)],x[0]) for i,x in enumerate(s)]
        return t2.barchart(t,label_width=150)   
    country={}
    city={}
    state={}
    food_preference={}
    t_shirt_size={}
    attendee_type={}
    registration_date={}
    certificates={}
    for row in db().select(db.auth_user.ALL):
        country[row.country]=country.get(row.country,0)+1
        city[row.city.lower()]=city.get(row.city.lower(),0)+1
        state[row.state.lower()]=state.get(row.state.lower(),0)+1
        #food_preference[row.food_preference]=food_preference.get(row.food_preference,0)+1
        #t_shirt_size[row.t_shirt_size]=t_shirt_size.get(row.t_shirt_size,0)+1
        attendee_type[row.attendee_type]=attendee_type.get(row.attendee_type,0)+1
        registration_date[row.created_on.date()]=registration_date.get(row.created_on.date(),0)+1
        certificates[row.certificate]=certificates.get(row.certificate,0)+1
    chart_country=colorize(country)
    chart_state=colorize(state)
    chart_city=colorize(city)
    chart_food_preference=None #colorize(food_preference)
    chart_t_shirt_size=None #colorize(t_shirt_size)
    chart_attendee_type=None #colorize(attendee_type)
    chart_registration_date=colorize(registration_date,sort_key=lambda x: x[1]) #colorize(attendee_type)
    chart_certificates=colorize(certificates) #colorize(attendee_type)


    return dict(chart_tutorials=chart_tutorials,
                chart_country=chart_country,
                chart_food_preference=chart_food_preference,
                chart_t_shirt_size=chart_t_shirt_size,
                chart_city=chart_city,
                chart_state=chart_state,
                chart_attendee_type=chart_attendee_type,
                chart_registration_date=chart_registration_date,
                chart_certificates=chart_certificates
                )

@cache(request.env.path_info,time_expire=60,cache_model=cache.ram)
def maps():
    rows=db(db.auth_user.id>0).select(
            db.auth_user.first_name,
            db.auth_user.last_name,
            db.auth_user.latitude,
            db.auth_user.longitude,
            db.auth_user.personal_home_page)
    x0,y0=CONFERENCE_COORDS
    return dict(googlemap_key=GOOGLEMAP_KEY,x0=x0,y0=y0,rows=rows)

#############################################
### FOR MANAGERS
#############################################

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

@auth.requires_login()
def create():
    if not (session.manager and request.args and request.args[0] in db.tables):
         t2.redirect('index')
    table=request.args[0]
    db[table]['exposes']=db[table].fields
    form=t2.create(db[table])
    db[table]['represent']=lambda item: A(item.id,':',
        item[db[table].fields[1]],_href=t2.action('update',[table,item.id]))
    search=t2.search(db[table])
    return dict(form=form,search=search)

@auth.requires_login()
def update():
    if not (session.manager and request.args and request.args[0] in db.tables):
         t2.redirect('index')
    table=request.args[0]
    if table=='auth_user':
        ##db[table]['exposes']=db.auth_user.exposes[:-1]
        form=t2.update(db[table],next='impersonate/[id]')
    else:
        db[table]['exposes']=db[table].fields
        form=t2.update(db[table],next='create/%s' % table)
    if table=='auth_user' and form.vars.id:
        balance=session.balance
        update_pay(form.record)
        session.balance=balance
    return dict(form=form)

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
    

def about():
    return dict()

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

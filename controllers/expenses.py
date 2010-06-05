
response.menu=[
    ['Main',False,URL(r=request,c='default',f='index')],
]

if not auth.user:
    response.menu.append([T('Register'),False,URL(r=request,c='default',f='register')])

response.menu.append([T('Conference'),False,'http://us.pycon.org/2009/conference'])

submenu_info=[
        [T('Companies'),False,URL(r=request,c='default',f='companies')],
        [T('Attendees'),False,URL(r=request,c='default',f='attendees')],
        [T('Charts'),False,URL(r=request,c='default',f='charts')],
        [T('Maps'),False,URL(r=request,c='default',f='maps')],
]
if ENABLE_TALKS:
   submenu_info.append([T('Accepted Talks'),False,URL(r=request,c='default',f='accepted_talks')])
   submenu_info.append([T('Proposed Talks'),False,URL(r=request,c='default',f='proposed_talks')])

response.menu.append([T('Stats'),False,'#',submenu_info])
response.menu.append([T('About'),False,URL(r=request,c='default',f='about')])

if auth.user:
    response.menu.append([T('Expenses'),True,URL(r=request,f='index')])
    response.menu.append([T('Profile'),False,URL(r=request,c='default',f='profile')])
    response.menu.append([T('Logout'),False,URL(r=request,c='default',f='logout')])
else:
    response.menu.append([T('Login'),False,URL(r=request,c='default',f='login')])


@auth.requires_login()
def index():
    while 1:
        records=db(db.expense_form.person==auth.user.id).select()
        if records: break
        db.expense_form.insert(person=auth.user.id)
    db.expense_item.exp_form.default=records[0].id
    # formfields=[ 'id','exp_form','seq','receipt_no','receipt_item','acct_code','description','serial_no','location','amount', ]
    formfields=[ 'receipt_no','receipt_item','acct_code','description','amount', ]
    form=SQLFORM(db.expense_item,fields=formfields)
    if form.accepts(request.vars,session):
        response.flash='posted!'
    expenses=db(db.expense_item.exp_form==records[0].id).select()
    return dict(expenses=expenses,form=form)


from dabo.dReportWriter import dReportWriter

def err_missing( message='Badge generation error.'):
    session.flash=T(message+'  Notify web administrator.')
    redirect(URL(r=request,c='default',f='index',args=[],vars={}))

def mkpdf(ds, sample=False):
    """
    Return a pdf made from the passed dataset.
    """

    from cStringIO import StringIO

    static = '%s/static/expense_reim/'% request.folder
    xmlfile  = '%s/exp_reim.rfxml' % static

    # buffer to create pdf in
    buffer = StringIO()

    # generate the pdf in the buffer, using the layout and data
    rw = dReportWriter(OutputFile=buffer, ReportFormFile=xmlfile, Cursor=ds)
    rw.write()

    # get the pdf out of the buffer
    pdf = buffer.getvalue()
    buffer.close()

    return pdf

@auth.requires_login()
def exp_pdf():
    """ 
    dynamically generate an expense reimbursement pdf from data.
    """
    rows = db(db.auth_user.id==auth.user.id)\
             (db.auth_user.id==db.expense_form.person)\
             (db.expense_form.id==db.expense_item.exp_form)\
           .select(*([db.auth_user[x] for x in db.auth_user.fields if x != 'id'] +
                     [db.expense_form[x] for x in db.expense_form.fields if x != 'id' ] +
                     [db.expense_item[x] for x in db.expense_item.fields]), 
                   **dict(orderby=db.expense_item.receipt_no))
    total=sum([row.expense_item.amount for row in rows])
    rows = [dict([(rows.colnames[i].split('.')[1],r[i]) for i in range(len(rows.colnames))]) \
            for r in rows.response]
    for row in rows: row['total']=total
    pdf = mkpdf(rows)
    response.headers['Content-Type']='application/pdf'
    response.headers['Content-Disposition'] = 'filename=expense.pdf'
    return pdf

    
# test functions

def test_dataset(source='dict'):
    """
    returns a dataset sutible for passing to mkpdf()
    
    source=dict uses a hardcoded dict.
    source=first pulls a record from the db (where id=1)

    >>> test_dataset()[0]['name']
    'Ivan Krsti\\xc4\\x87'
     
    """
 
    def static(): 
        row={'name':'Ivan Krsti\xc4\x87', 'id':1234,
        'badge_line1':'laptop.org', 'badge_line2':'Sprint Leader: OLPC',
             'key_note':True, 'speaker':True, 'vendor':True,
             'session_chair':True, 'sponsor':True,
             't_shirt_size':'L' }
        return [row]

    def first_in_db():
        # row = db().select(db.expense_item.ALL)[0]
        # row = db(db.expense_form.person==auth.user.id).select()[0]
        row = db().select(db.expense_item.ALL)[0]
        return [row]

    ds = {'dict': static(),
          'first': first_in_db()}[source]

    return ds

def firstds(): 
    """
    returns the first row from wherever badge data comes from

    >>> firstds()[0]['id']
    1

    {'badge_line1': 'http://www.tatapo.com', 'vendor': True, 't_shirt_size': 'man/2xlarge', 'badge_line2': 'http://www.tatapo.com', 'id': 1, 'speaker': True, 'sponsor': True, 'name': 'cemoso0', 'key_note': True, 'session_chair': True}
    """ 
    return test_dataset('first')
 
def test_pdf():
    """ 
    dynamically generate a badge from sample data.
    return a pdf of the badge sutible for printing on badge stock.
    """

    ds = test_dataset('first')

    pdf = mkpdf(ds,sample=True)

    response.headers['Content-Type']='application/pdf' 
    response.headers['Content-Disposition'] = 'filename=badge.pdf'

    return pdf


"""
This file was developed by Massimo Di Pierro as a web2py extension.
This file is released under the BSD license (you can include it in bytecode compiled web2py apps as long as you acknowledge the author). web2py (required to run this file) is released under the GPLv2 license.
TODO:
   - ok, works on GAE but need to fix ID in search
   - ok, delete files and dowload on GAE
   - add media_player?
   - add slideshow?
   - add layout customization?
"""

from gluon.storage import Storage
from gluon.html import *
from gluon.http import *
from gluon.validators import *
from gluon.sqlhtml import *
from gluon.contrib.markdown import WIKI
try: from gluon.contrib.gql import SQLTable
except ImportError: from gluon.sql import SQLTable
import traceback

def t3_execute(text,environment,_class='error',is_admin=True):
    regex=re.compile('\{\{(?P<comm>.+?)\}\}',re.DOTALL|re.MULTILINE)
    errors=False
    k=0
    text_done=''
    while True:
        s=regex.search(text)
        if not s: break
        c=s.group('comm').replace('&amp;','&').replace('&lt;','<').replace('&gt;','>')
        request=environment['request']
        session=environment['session']
        report=DIV(H1('traceback'),'',H1('code'),CODE(c,language='web2py'),
                   H1('request'),BEAUTIFY(request),
                   H1('session'),BEAUTIFY(session))
        try:
            if c[0]=='=':
                exec('_res='+c[1:],{},environment)
                p=xmlescape(environment['_res'])
            else:
                exec(c,{},environment)
                p=''
        except Exception, e:
            errors=True
            if is_admin:
                report[1]=CODE(traceback.format_exc(),language='web2py')
                p='<div class="%s">Internal Error [<a class="zoom" href="#zoom-%i">open</a>]</div><div class="hidden" id="zoom-%i">%s</div>' % (_class,k,k,report.xml())
                k+=1
            else:
                p='<div class="%s">Internal Error</div>'
        text_done=text_done+text[:s.start()]+p
        text=text[s.end():]
    return text_done+text,errors

class T2:
    IMAGE_EXT=['.jpg','.gif','.png']

    def __init__(self,request,response,session,cache,T,db,all_in_db=False):
        """
        Creates a T2 object and all necessary tables:

        t2_person:     name, email, password, registration_key
        t2_group:      name
        t2_membership: person_id, group_id, membership_type, status
        t2_access:     person_id, table_name, record_id, access_type
        t2_attachment: ...
        t2_comment:    ...
        t2_review:     ...

        request.args[-1] is stored in self.id
        if self.logged_in:
            self.person_id, self.person_name, self.person_email
        """
        import datetime
        self.email_server='localhost'
        self.error_action='error'
        self.now=now=datetime.datetime.now()
        self.request=request
        self.response=response
        self.session=session
        self.cache=cache
        self.T=T
        self.db=db
        self.all_in_db=all_in_db
        if self.db._dbname=='gql':
            self.is_gae=True
            self.all_in_db=True
        else: self.is_gae=False
        if all_in_db: session.connect(request,response,db=db)
        if not session.t2: session.t2=Storage()
        try: self.id=int(request.args[-1])
        except: self.id=0
        self.person_name=session.t2.person_name
        self.person_id=session.t2.person_id
        self.person_email=session.t2.person_email
        self.logged_in=True if self.person_id else False
        self._define_messages()
        self._create_tables()
        if session.t2.my_groups_id:
            self.my_groups_id=session.t2.my_groups_id
        else:
            self.memberships=self.my_memberships()
            self.my_groups_id=[g.group_id for g in self.memberships]
            session.t2.my_groups_id=self.my_groups_id
        response.files=[
          '/plugin_t2/static/t2/scripts/jquery.js',
          '/plugin_t2/static/t2/styles/calendar.css',
          '/plugin_t2/static/t2/scripts/calendar.js',
          '/plugin_t2/static/t2/styles/sfmenu.css',
          '/plugin_t2/static/t2/scripts/sfmenu.js',
          '/plugin_t2/static/t2/scripts/fancyzoom.min.js',
          '/plugin_t2/static/t2/styles/rating.css',
          '/plugin_t2/static/t2/scripts/rating.js',
          '/plugin_t2/static/t2/scripts/web2py.js',
        ]

    def onerror(self): ### FIX - PASS MORE PARAMETERS
        """
        To be used as a decorator. On error it calles self._error()
        """
        def g(f):
            def h(*a,**b):
                try: return f(*a,**b)
                except HTTP, e: raise e
                except Exception: self._error()
            return h
        return g
    
    def _globals(self):
        """
        Returns (request,response,session,cache,T,db)
        """
        return self.request, self.response, self.session, \
               self.cache, self.T, self.db

    def _error(self):
        """
        Redirects to the self.error_action (='error'?) page.
        """
        self.redirect(self.error_action)

    def action(self,f=None,args=[],vars={}):
        """
        self.action('name',[],{}) is a shortcut for 
     
            URL(r=request,f='name',args=[],vars={})
        """
        if not f: f=self.request.function
        if not isinstance(args,(list,tuple)): args=[args]
        return URL(r=self.request,f=f,args=args,vars=vars)

    def redirect(self,f=None,args=[],vars={},flash=None):
        """
        self.redirect('name',[],{},'message') is a shortcut for

            session.flash='message'
            redirect(URL(r=request,f='name',args=[],vars={})
        """
        if flash: self.session.flash=flash
        redirect(self.action(f,args,vars))

    def include(self):
        """
        In the layout.html <head>{{=t2.include()}}</head> includes all
        necessary CSS and JS files for this plugin to work.
        """
        s=''
        for file in self.response.files:
            if file[-4:]=='.css':
                s+=LINK(_href=file,
                        _rel="stylesheet",
                        _type="text/css",
                        _charset="utf-8").xml()
            elif file[-3:]=='.js':
                s+=SCRIPT(_src=file).xml()
        return XML(s)
 
    def menu(self,menu,style='h'):
        """
        In the layout {{=t2.menu(style='h')}} inserts a menu from response.menu
        
        It assumes response.menu=[item1, items2, ...] where
        item1=['name',active True/False,URL(...),[item11,item12,...]]
        item11 is a submenu item, etc.
       
        style can be 'h' for horizontal, 'v' for vertical, 'n' for navigation
        """
        request,response,session,cache,T,db=self._globals()
        def rec_menu(menu,_class=None):
           items=[LI(A(i[0],_class='current' if i[1] else None,
                       _href=i[2]),rec_menu(i[3]) if len(i)>3 else '') \
                  for i in menu]
           return UL(_class=_class if _class else None,*items)
        if not menu: return ''
        _class='sf-menu'
        if style=='n': _class+=' sf-navbar'
        if style=='v': _class+=' sf-vertical'
        return rec_menu(menu,_class=_class)

    @staticmethod
    def _capitalize(text):
        return ' '.join([c.capitalize() for c in text.split('_')])

    @staticmethod
    def _get_labels(table):
        labels={}
        for field in table.fields:
            if hasattr(table[field],'label'):
                labels[field]=table[field].label
        return labels

    @staticmethod
    def _get_col3(table):
        col3={}
        for field in table.fields:
            if hasattr(table[field],'comment'):
                col3[field]=table[field].comment
        return col3

    def _define_messages(self):        
        self.messages=Storage()
        self.messages.record_created="Record Created"
        self.messages.record_modified="Record Modified"
        self.messages.record_deleted="Record(s) Deleted"
        self.messages.record_was_altered="Record Could Not Be Saved Because It Has Changed"
        self.messages.invalid_value="Invalid Enrty"
        self.messages.attachment_posted="Attchment Posted"
        self.messages.no_comments="No Comments"
        self.messages.no_visible_comments="No Visible Comments"
        self.messages.review_posted="Review Posted"
        self.messages.register_email_body="Click here %(registration_key)s to complete registration"
        self.messages.register_email_subject="Verify Registration"
        self.messages.password_email_body="Your new password is: %(password)s"
        self.messages.password_email_subject="New Password"
        self.messages.email_sent="Email Sent"
        self.messages.unable_to_send_email="Unable to Send Email"
        self.messages.logged_in="Logged In"
        self.messages.invalid_login="Invalid Login"
        self.messages.logged_out="Logged Out"
        self.messages.page_created="Page Created"
        self.messages.page_modified="Page Modified"
        self.messages.errors_in_code="Errors in Code"

    @staticmethod
    def base_table(db,tablename):
        trackable=SQLTable(db,'trackable',
            db.Field('created_signature'),
            db.Field('created_by_ip'),
            db.Field('created_by','integer'),
            db.Field('created_on','datetime'),
            db.Field('modified_signature'),
            db.Field('modified_by','integer'),
            db.Field('modified_on','datetime'))
        if tablename=='t2_person':
            t=SQLTable(db,'t2_person',
               db.Field('name'),
               db.Field('email'),
               db.Field('registration_key',length=64),
               db.Field('password','password'),trackable)
            t.name.requires=IS_NOT_EMPTY()
            t.email.requires=[IS_EMAIL(),IS_NOT_IN_DB(db,'t2_person.email')]
            t.password.requires=[IS_NOT_EMPTY(),CRYPT()]
            return t
        if tablename=='t2_group':
            t=SQLTable(db,'t2_group',
               db.Field('name'),
               db.Field('description','text'),trackable)
            t.name.requires=IS_NOT_EMPTY()
            return t
        if tablename=='t2_membership':
            t=SQLTable(db,'t2_membership',
               db.Field('person_id','reference t2_person'),
               db.Field('group_id','reference t2_group'),
               db.Field('membership_type'),
               db.Field('status'),trackable)
            t.person_id.requires=IS_IN_DB(db,'t2_person.id','%(name)s')
            t.group_id.requires=IS_IN_DB(db,'t2_group.id','%(name)s')
            return t
        if tablename=='t2_access':
            t=SQLTable(db,'t2_access',
               db.Field('group_id','reference t2_group'),
               db.Field('table_name'),
               db.Field('record_id','integer'),
               db.Field('access_type'),trackable)
            t.group_id.requires=IS_IN_DB(db,'t2_group.id','%(name)s')
            return t
        if tablename=='t2_attachment':
            t=SQLTable(db,'t2_attachment',
               db.Field('table_name'),
               db.Field('record_id','integer'),
               db.Field('name','string'),
               db.Field('description','text'),
               db.Field('file','upload'),
               db.Field('file_data','blob',default=''),
               db.Field('filename'),
               db.Field('status',default='approved'),trackable)
            t.name.requires=IS_NOT_EMPTY()
            t.file.requires=IS_NOT_EMPTY()
            return t
        if tablename=='t2_comment':
            t=SQLTable(db,'t2_comment',
               db.Field('table_name'),
               db.Field('record_id','integer'),
               db.Field('parent_record','integer'),
               db.Field('body','text'),
               db.Field('status'),trackable)
            t.body.requires=IS_NOT_EMPTY()
            t.parent_record.default=0
            return t
        if tablename=='t2_review':
            t=SQLTable(db,'t2_review',
               db.Field('table_name'),
               db.Field('record_id','integer'),
               db.Field('rating','integer'),
               db.Field('body','text'),
               db.Field('status'),trackable)
            t.body.requires=IS_NOT_EMPTY()
            t.rating.requires=IS_IN_SET([str(x) for x in range(0,6)])
            t.rating.widget=T2.rating_widget
            t.rating.default=0
            return t
        if tablename=='t2_wiki':
            t=SQLTable(db,'t2_review',
               db.Field('name'),
               db.Field('title'),
               db.Field('menu','boolean',default=True),
               db.Field('public','boolean',default=True),
               db.Field('body','text'),trackable)
            t.name.requires=[IS_NOT_EMPTY(),IS_ALPHANUMERIC(),IS_NOT_IN_DB(db,'t2_wiki.name')]
            t.title.requires=IS_NOT_EMPTY()
            return t
        raise KeyError

    def _create_tables(self):
        """
        Defines all tables needed by the plugin to work
        (if they do not exist) called by contructor.
        """
        request,response,session,cache,T,db=self._globals()
        if not db.has_key('t2_person'):
            t=db.define_table('t2_person',T2.base_table(db,'t2_person'))
            t.exposes=['name','email','password']
            t.displays=['name','email','password']
        if not db.has_key('t2_group'):
            t=db.define_table('t2_group',T2.base_table(db,'t2_group'))
            t.exposes=['name','description']
            t.displays=['name','description']
        if not db.has_key('t2_membership'):
            t=db.define_table('t2_membership',T2.base_table(db,'t2_membership'))
            t.exposes=['person_id','group_id','membership_type']
            t.displays=['person_id','group_id','membership_type','status']
        if not db.has_key('t2_access'):
            t=db.define_table('t2_access',T2.base_table(db,'t2_access'))
        if not db.has_key('t2_attachment'):
            t=db.define_table('t2_attachment',T2.base_table(db,'t2_attachment'))
            t.exposes=['name','description','file']
        db.t2_attachment.file.uploadfield='file_data' if self.all_in_db else True
        if not db.has_key('t2_comment'):
            t=db.define_table('t2_comment',T2.base_table(db,'t2_comment'))
            t.exposes=['parent_record','body']
        if not db.has_key('t2_review'):
            t=db.define_table('t2_review',T2.base_table(db,'t2_review'))
            t.exposes=['rating','body']
        if not db.has_key('t2_wiki'):
            t=db.define_table('t2_wiki',T2.base_table(db,'t2_wiki'))
            t.exposes=['name','title','menu','public','body']

    def _filter_fields(self,fields):
        filtered=['id','created_on','created_by','created_signature',
           'created_by_ip','modified_on','modified_by','modified_signature',
           'modified_by_ip']
        return [x for x in fields if not x in filtered]

    def _stamp(self,table,form,create=False):
        """
        Called by create and update methods. it timestamps the record.
        The following fields are timestamped (if they exist):
        - created_on
        - created_by
        - created_signature
        - modified_on
        - modified_by
        - modified_signature
        """
        if create:
            if 'created_by_ip' in table.fields: 
                form.vars.created_by_ip=self.request.client
            if 'created_on' in table.fields: 
                form.vars.created_on=self.now
            if 'created_by' in table.fields: 
                form.vars.created_by=self.person_id
            if 'created_signature' in table.fields: 
                form.vars.created_signature=self.person_name
        if 'modified_by_ip' in table.fields:
            form.vars.modified_by_ip=self.request.client
        if 'modified_on' in table.fields: 
            form.vars.modified_on=self.now
        if 'modified_by' in table.fields:
            form.vars.modified_by=self.person_id
        if 'modified_signature' in table.fields:
            form.vars.modified_signature=self.person_name

    def create(self,table,next=None,vars={},onaccept=None):
        """
        t2.create(db.table,next='index',flash='done',vars={},onaccept=None)
        makes a SQLFORM and processing logic for table. Upon success it 
        redrects to "next" and flashes "flash". 
        vars are additional variables that should be placed in the form.
        onaccept=lambda form: pass is a callback executed after form accepted
        """
        request,response,session,cache,T,db=self._globals()
        if not next: next=request.function
        fields=self._filter_fields(table.get('exposes',table.fields))
        labels=self._get_labels(table)
        col3=self._get_col3(table)
        form=SQLFORM(table,fields=fields,labels=labels,\
                     showid=False,col3=col3,_class='t2-create')
        self._stamp(table,form,create=True)
        if type(vars)==type(lambda:0): vars(form)
        else: form.vars.update(vars)
        if form.accepts(request.vars,session):
            session.flash=self.messages.record_created
            if onaccept: onaccept(form)
            self.redirect(f=next.replace('[id]',str(form.vars.id)))
        return form

    def update(self,table,record=None,query=None,next=None,deletable=True,
               vars={},onaccept=None,ondelete=None):
        """
        t2.update(db.table,query,next='index',flash='done',vars={},onaccept=None,ondelete=None)
        makes a SQLFORM and processing logic for table and the record 
        identified by the query. If no query: query=table.id==t2.id
        Upon success it redrects to "next" and flashes "flash". 
        vars are additional variables that should be placed in the form.
        onaccept=lambda form: pass is a callback executed after form accepted
        """
        request,response,session,cache,T,db=self._globals()
        if not next: next='%s/[id]'%request.function
        if record is not None:
           rows = [record]
        elif query:
           rows=table._db(query).select(table.ALL,limitby=(0,1))
        else:
           id=self.id or self._error()
           rows=table._db(table.id==id).select(table.ALL,limitby=(0,1))
        if not rows: self._error()
        fields=self._filter_fields(table.get('exposes',table.fields))
        labels=self._get_labels(table)
        col3=self._get_col3(table)
        self.record=record=rows[0]
        hidden={'modified_on__original':str(record.get('modified_on',None))}
        form=SQLFORM(table,record,upload=URL(r=request,f='download'),\
                     deletable=deletable,fields=fields,labels=labels,\
                     showid=False,col3=col3,_class='t2-update',hidden=hidden)
        self._stamp(table,form)
        if type(vars)==type(lambda:0): vars(form)
        else: form.vars.update(vars)
        if request.vars.modified_on__original and \
           request.vars.modified_on__original!=hidden['modified_on__original']:
            session.flash=self.messages.record_was_altered
            redirect(self.action(args=request.args))
        if form.accepts(request.vars,session,delete_uploads=True):
            form.old=record
            session.flash=self.messages.record_modified
            if request.vars.delete_this_record:
                session.flash=self.messages.record_modified
                if ondelete:                    
                    ondelete(form)
            elif onaccept:                
                onaccept(form)            
            
            self.redirect(f=next.replace('[id]',str(form.vars.id)))
        return form

    def delete(self,table,query=None,next=None):
        """
        Deletes the result of the query. If no query: query=table.id==t2.id
        """
        request,response,session,cache,T,db=self._globals()
        if not next: next=request.function
        if not query:
           id=self.id or self._error()  
           query=table.id==id
        table._db(query).delete(delete_uploads=True)
        if next: self.redirect(f=next,flash=self.messages.record_deleted)
        return True

    def read(self,table,query=None,limitby=None,orderby=None):
        """
        Selects fall fields of table for query. No query imples all records.
        """
        import uuid
        request,response,session,cache,T,db=self._globals()
        if query:
           rows=table._db(query).select(table.ALL,orderby=None,\
                                        limitby=limitby)
        else:
           id=self.id or self._error()
           rows=table._db(table.id==id).select(table.ALL)
        return rows

    def display(self,table,query=None):
        """
        Shows oe record of table for query
        """
        rows=self.read(table,query)
        request,response,session,cache,T,db=self._globals()
        if not rows: self._error()
        self.record=record=rows[0]
        if table.get('display',None): return table.display(record)
        fields=table.get('displays',table.fields)
        labels=self._get_labels(table)
        items=[]
        for field in fields:
            label=labels[field] if labels.has_key(field) else \
                  self._capitalize(field)
            value=record[field]
            if hasattr(table[field],'display'):
               value=table[field].display(value)
            elif table[field].type=='blob':
               continue
            elif table[field].type=='upload' and value and \
                 value[-4:].lower() in self.IMAGE_EXT:
               u=URL(r=request,f='download',args=[value])
               k='zoom-%s-%s-%i' % (table,field,record.id)
               value=DIV(A(IMG(_src=u,_height=100),
                           _class='zoom',_href='#'+k),
                   DIV(IMG(_src=u,_width=600),_id=k,_class='hidden'))
            elif table[field].type=='upload' and value:
               u=URL(r=request,f='download',args=[value])
               value=A('download',_href=u)
            items.append(TR(LABEL(label,':'),value))
        return DIV(TABLE(*items),_class='t2-display')

    '''
    '''
    def itemize(self,*tables,**opts):
        """
        Lists all records from tables. 
        opts include: query, orderby, nitems
	  where nitems is items per page;
        """
        ### FIX - ADD PAGINATION BUTTONS
        import re
        request,response,session,cache,T,db=self._globals()
        if not len(tables): raise SyntaxError
        query=opts.get('query',None)
        orderby=opts.get('orderby',None)
        nitems=opts.get('nitems',25)
        g=re.compile('^(?P<min>\d+)$').match(request.vars.get('_page',''))
        page=int(g.group('min')) if g else 0
        limitby=opts.get('limitby',(page*nitems,page*nitems+nitems))
        if not query:
            query=tables[0].id>0
        rows_count=tables[0]._db(query).count()
        rows=tables[0]._db(query).select(orderby=orderby,limitby=limitby,
                                         *[t.ALL for t in tables])
        if not rows: return 'No data'
        def represent(t,r):
            try: return t.represent(r)
            except KeyError: return '[#%i] %s' % (r.id,r[t.fields[1]])
        nav=[TR(TD(A('[prevous page]',_href=self.action(args=request.args,vars={'_page':page-1})) if page else '',A('[next page]',_href=self.action(args=request.args,vars={'_page':page+1})) if page*nitems+len(rows)<rows_count else ''))]
        if len(tables)==1:
            return TABLE(_class='t2-itemize',
                         *nav+[TR(represent(tables[0],row)) for row in rows]+nav)
        else:
            return TABLE(_class='t2-itemize',
                         *nav+[TR(*[represent(table,row[table._tablename]) \
                                    for table in tables]) for row in rows]+nav)

    '''
    def itemize(self,*tables,**opts):
        """
        Lists all records from tables.
        opts include: query, orderby, nitems, header where nitems is items per page;
        """
        ### FIX - ADD PAGINATION BUTTONS
        import re
        request,response,session,cache,T,db=self._globals()
        if not len(tables): raise SyntaxError
        query=opts.get('query',None)
        orderby=opts.get('orderby',None)
        nitems=opts.get('nitems',25)
        g=re.compile('^(?P<min>\d+)$').match(request.vars.get('_page',''))
        page=int(g.group('min')) if g else 0
        limitby=opts.get('limitby',(page*nitems,page*nitems+nitems))
        if not query:
            query=tables[0].id>0
        rows_count=tables[0]._db(query).count()
        rows=tables[0]._db(query).select(orderby=orderby,limitby=limitby,
                                         *[t.ALL for t in tables])
        if not rows: return None # rather than 'No data'. Give caller a chance to do his i18n issue
        def represent(t,r):
          try: rep=t.represent(r) # Note: custom represent() should generate a string or a list, but NOT a TR(...) instance
          except KeyError:
            rep=([r[f] for f in t.displays] # Default depends on t.displays, if any
              if 'displays' in t else ['#%i'%r.id, str(r[t.fields[1]])]) # Fall back to TR(id,FirstField)
          return rep if isinstance(rep,list) else [rep] # Ensure to return a list
        header=opts.get('header',# Input can be something like TR(TH('ID'),TH('STAMP'))
          TR(*[TH(tables[0][f].label) for f in tables[0].displays])
            if 'displays' in tables[0] else '') # Default depends on tables[0].displays, if any
        headerList=[header] if header else []
        nav=DIV( # Iceberg at 21cn dot com prefers this style of page navigation :-)
          INPUT(_type='button',_value='|<',_onclick='javascript:location="%s"'
            %self.action(args=request.args,vars={'_page':0})) if page else '',
          INPUT(_type='button',_value='<',_onclick='javascript:location="%s"'
            %self.action(args=request.args,vars={'_page':page-1})) if page else '',
          SELECT(value=page,
            _onchange='javascript:location="%s?_page="+this.value'
              %self.action(args=request.args),
            *[OPTION(i+1,_value=i) for i in xrange(rows_count/nitems+1)]
            ) if nitems<rows_count else '',
          INPUT(_type='button',_value='>',_onclick='javascript:location="%s"'
            %self.action(args=request.args,vars={'_page':page+1})
            ) if page*nitems+len(rows)<rows_count else '',
          INPUT(_type='button',_value='>|',_onclick='javascript:location="%s"'
            %self.action(args=request.args,vars={'_page':rows_count/nitems})
            ) if page*nitems+len(rows)<rows_count else '',
          ) if nitems<rows_count else None
        if len(tables)==1:
          return DIV(
            nav if nav else '', # It shouldn't be inside the table otherwise it is tricky to set the correct _colspan for IE7
            TABLE(_class='sortable',#sorry, I don't know how to setup css to make _class='t2-itemize' looks cool, so I stick to "sortable"
              *headerList+[TR(*represent(tables[0],row)) for row in rows]),
            nav if nav else '') # See above
        else:
          import itertools
          return DIV(
            nav if nav else '', # And don't try to make it "align=right", because the table might be too wide to show in the screen.
            TABLE(_class='sortable',#see above
              *headerList+[TR(*list(itertools.chain(
                *[represent(table,row[table._tablename]) for table in tables])))
                  for row in rows]),
            nav if nav else '') # See above


    '''

    def search(self,*tables,**opts):    
        """
        Makes a search widgets to search records in tables.
        opts can be query, orderby, limitby
        """
        request,response,session,cache,T,db=self._globals()
        if self.is_gae and len(tables)!=1: self._error()
        def is_integer(x):
            try: int(x)
            except: return False
            else: return True
        def is_double(x):
            try: float(x)
            except: return False
            else: return True
        from gluon.sqlhtml import form_factory
        options=[]
        orders=[]
        query=opts.get('query',None)
        def option(s): return OPTION(s if s[:3]!='t2_' else s[3:],_value=s)
        for table in tables:
            for field in table.get('displays',table.fields):
                tf=str(table[field])
                t=table[field].type
                if not self.is_gae and (t=='string' or t=='text'): 
                   options.append(option('%s contains' % tf))
                   options.append(option('%s starts with' % tf))
                if t!='upload':
                   options.append(option('%s greater than' % tf))
                options.append(option('%s equal to' % tf))
                options.append(option('%s not equal to' % tf))
                if t!='upload':
                    options.append(option('%s less than' % tf))
                orders.append(option('%s ascending' % tf))
                orders.append(option('%s descending' % tf))
        form=FORM(SELECT(_name='cond',*options),
                  INPUT(_name='value',value=request.vars.value or '0'),
                  ' ordered by ',
                  SELECT(_name='order',*orders),' refine? ',
                  INPUT(_type='checkbox',_name='refine'),
                  INPUT(_type='submit'))
        if form.accepts(request.vars,formname='search'):
            db=tables[0]._db
            p=(request.vars.cond,request.vars.value,
               request.vars.order)
            if not request.vars.refine: session.t2.query=[]
            session.t2.query.append(p)
            orderby,message1,message2=None,'',''
            prev=[None,None,None]        
            for item in session.t2.query:
                c,value,order=item
                if c!=prev[0] or value!=prev[1]:
                    tf,cond=c.split(' ',1)                
                    table,field=tf.split('.')
                    f=db[table][field]
                    if (f.type=='integer' or f.type=='id') and \
                       not is_integer(value):
                        session.flash=self.messages.invalid_value
                        self.redirect(args=request.args)
                    elif f.type=='double' and not is_double(value):
                        session.flash=self.messages.invalid_value
                        self.redirect(args=request.args)
                    elif cond=='contains':
                        q=f.lower().like('%%%s%%' %value.lower())
                    elif cond=='starts with':
                        q=f.lower().like('%s%%' % value.lower())
                    elif cond=='less than': 
                        q=f<value
                    elif cond=='equal to':
                        q=f==value
                    elif cond=='not equal to':
                        q=f!=value
                    elif cond=='greater than': 
                        q=f>value
                    query=query&q if query else q
                    message1+='%s "%s" AND ' % (c,value)
                if order!=prev[2]:
                    p=None
                    c,d=request.vars.order.split(' ')
                    table,field=c.split('.')
                    if d=='ascending': p=f
                    elif d=='descending': p=~f
                    orderby=orderby|p if orderby else p
                    message2+='%s '% order
                prev=item
            message='QUERY %s ORDER %s' % (message1,message2)
            return DIV(TABLE(TR(form),TR(message),\
                   TR(self.itemize(query=query,orderby=orderby,*tables))),
                   _class='t2-search')
        else:
            session.t2.query=[]
        return DIV(TABLE(TR(form)),_class='t2-search')

    def wiki_nav(self,action='wiki',query=None):
        request,response,session,cache,T,db=self._globals()
        if not db.t2_wiki.has_key('represent'):
            db.t2_wiki.represent=lambda r: A(r.title,_href=self.action(action,args=[r.name]))
        if self.is_gae: return self.itemize(db.t2_wiki,orderby=db.t2_wiki.title)
        form=FORM('Search: ',INPUT(_name='search',requires=[IS_NOT_EMPTY(),IS_LOWER()]))
        if form.accepts(request.vars,session):
             search='%%%s%%'%form.vars.search
             query1=db.t2_wiki.title.lower().like(search)| \
                      (db.t2_wiki.title.lower().like(search)& \
                       ~db.t2_wiki.title.lower().like(search))
             if query: query1=query&query
             items=self.itemize(db.t2_wiki,query=query1)
        else:
             items=self.itemize(db.t2_wiki,orderby=db.t2_wiki.title,query=query)
        return DIV(form,items)

    def wiki_menu(self,action='wiki'):
        request,response,session,cache,T,db=self._globals()
        rows=db(db.t2_wiki.menu==True).select()        
        rows=sorted(rows,lambda x,y: +1 if y.title<x.title else -1)
        menu=[]
        keys={}
        for row in rows:
            if not self.logged_in and not row.public: continue
            items=row.title.split('/')
            path='/'.join(items[:-1])
            x=[items[-1],request.args[:1]==[row.name],self.action(action,args=[row.name])]
            keys[row.title]=x
            if path and keys.has_key(path):
                r=keys[path]
                if len(r)==3: r.append([])
                r[3].append(x)
            else:
                menu.append(x)
        return menu

    def wiki(self,query=None,writable=True,deletable=True,mode='html',
             onaccept=None,env={}):
        request,response,session,cache,T,db=self._globals()
        if query: rows=db(query).select()
        if request.args: rows=db(db.t2_wiki.name==request.args[0]).select()
        else: rows=[]
        fields=self._filter_fields(db.t2_wiki.get('exposes',db.t2_wiki.fields))
        editmode=(request.args[1:2]==['edit'])
        if not rows and writable and editmode:
            form=SQLFORM(db.t2_wiki,fields=fields)
            if form.accepts(request.vars,session):
                session.flash=self.messages.page_created
                if onaccept: onaccept(form)
                redirect(URL(r=request,args=[form.vars.name]))
            return form
        elif rows and writable and editmode:
            if rows[0].name=='main': fields,deletable=['title','body'],False
            form=SQLFORM(db.t2_wiki,rows[0],fields=fields,
                         showid=False,deletable=deletable)
            if form.accepts(request.vars,session):
                session.flash=self.messages.page_modified
                if onaccept: onaccept(form)
                redirect(URL(r=request,args=[form.vars.name or 'main']))
            return form
        elif rows and (not editmode or not writable):
            if not self.logged_in and not rows[0].public: self._error()
            if writable and self.logged_in:
                edit=DIV(A('edit',_href=URL(r=request,
                  args=request.args[:1]+['edit'])),_style='text-align: right')
            else: edit=''
            if mode=='smart':
                text,errors=t3_execute(rows[0].body,env,is_admin=writable)
                if errors: response.flash=self.messages.errors_in_code
                return DIV(edit,DIV(XML(text)),_class='t2-wiki')
            elif mode=='html':
                return DIV(edit,DIV(XML(rows[0].body,sanitize=True)),_class='t2-wiki')
            elif mode=='markdown':
                import gluon.contrib.markdown as md
                return DIV(edit,DIV(md.WIKI(rows[0].body)),_class='t2-wiki')
            else:
                return DIV(edit,DIV(mode(rows[0].body)),_class='t2-wiki')
        else: self._error()

    def attachments(self,table=None,readable=True,writable=True,deletable=False):
        """
        Lists all attachemnt to the current record and allows to 
        post attachament.
        """
        request,response,session,cache,T,db=self._globals()
        id=self.id or 0
        if table: table_name=str(table)
        else: table_name=request.env.path_info
        ctable=db.t2_attachment
        labels=self._get_labels(ctable)
        form=SQLFORM(ctable,fields=ctable.exposes,labels=labels)
        self._stamp(ctable,form,create=True)
        form.vars.table_name=table_name
        form.vars.record_id=id
        if request.vars.get('file','')!='':
            form.vars.filename=request.vars.file.filename
        if form.accepts(request.vars,session):
            session.flash=self.messages.attachment_posted
            self.redirect(args=request.args)  
        rows=db(ctable.table_name==form.vars.table_name)\
               (ctable.record_id==id)\
               .select(orderby=ctable.created_by)
        if not readable:
            items=[]
        else:
            items=[LI(A(row.name,_href=URL(r=request,f='download',args=[row.file])),' posted by %(created_signature)s on %(created_on)s' % row) for row in rows]
        if not writable:
            return DIV(TABLE(TR(UL(*items))),_class='t2-attachments')
        return DIV(TABLE(TR(UL(*items)),TR(form)),_class='t2-attachments')

    def comments(self,table=None,moderated=False,readable=True,writable=True,deletable=False,hide=True):
        """
        Shows comments associated to the record and allows to 
        post new comment
        """
        request,response,session,cache,T,db=self._globals()
        id=self.id or 0
        if table: table_name=str(table)
        else: table_name=request.env.path_info
        ctable=db.t2_comment
        labels=self._get_labels(ctable)
        form=SQLFORM(ctable,fields=ctable.exposes,labels=labels,
                     _id='t2_comment_form')  
        self._stamp(ctable,form,create=True)
        form.vars.table_name=table_name
        form.vars.record_id=id
        form.vars.status='pending' if moderated else 'approved'
        if form.accepts(request.vars,session):
            session.flash='Comment posted'
            self.redirect(args=request.args)  
        if not self.is_gae:
            rows=db(ctable.table_name==form.vars.table_name)\
                   (ctable.status=='approved')\
                   (ctable.record_id==id)\
                    .select(orderby=ctable.parent_record|ctable.created_on)
        else:
            rows=[r for r in db(ctable.table_name==form.vars.table_name)\
                   (ctable.status=='approved')\
                   (ctable.record_id==id)\
                    .select()]
            rows.sort(lambda a,b: +1 if (a.parent_record,a.created_on)>(b.parent_record,b.created_on) else -1)
        ### FIX - REWITE THE LAST TWO LINES
        def format(row):
            return DIV('User %(created_signature)s on %(created_on)s says:' \
                        %row,WIKI(row.body))
        if not writable:
            def navbar(id,name='reply'):
                return SPAN('[',
                   A('toggle',_onclick='$("#t2_comment_%i").slideToggle();$("#t2_comment_form").hide()'%id),']')
        else:
            def navbar(id,name='reply'):
                return SPAN('[',
                   A('toggle',_onclick='$("#t2_comment_%i").slideToggle();$("#t2_comment_form").hide()'%id),'][',
                   A(name,_onclick='$("#t2_comment_parent_record").val(%i);$("#t2_comment_form").show();$("#t2_comment_body").focus();' % id),']')
        divs={0:DIV(navbar(0,'post'),'',UL(_class='comments',_id='t2_comment_0'))}
        for comment in rows:
            item=LI(format(comment),navbar(comment.id),
                    UL(_class='comments',_id='t2_comment_%i'%comment.id))
            if not divs.has_key(comment.parent_record): continue ### BROKEN
            divs[comment.parent_record][2].append(item)
            divs[comment.id]=item        
        script=SCRIPT('$("#t2_comment_form").hide();')
        if hide: script[0]=script[0]+'$("#t2_comment_0").hide();'       
        form[0][0]['_style']='visibility: hidden'
        if not rows: divs[0]=self.messages.no_comments
        if not readable: div[0]=self.messages.no_visible_comments
        if not writable: return DIV(divs[0],script,_class='t2-comments')
        else: return DIV(divs[0],form,_class='t2-comments')

    def reviews(self,table=None,status='approved',readable=True,writable=True,deletable=False,subtitle="You Review"):
        """
        Lists reviews associated to the current record and allows to 
        post a new review. Reviews are unique. You cannot submit multiple
        reviews for the same record. If reviews are moderated=True,
        they have a pending status until approved.
        """
        request,response,session,cache,T,db=self._globals()
        id=self.id or 0
        if table: table_name=str(table)
        else: table_name=request.env.path_info
        ctable=db.t2_review
        labels=self._get_labels(ctable)
        rows=db(ctable.created_by==self.person_id)\
               (ctable.table_name==table_name)\
               (ctable.record_id==id).select()
        form=SQLFORM(ctable,rows[0] if rows else None,
                     fields=ctable.exposes,labels=labels,showid=False)  
        self._stamp(ctable,form,create=True if not rows else False)
        form.vars.table_name=table_name
        form.vars.record_id=id
        form.vars.status=status
        if form.accepts(request.vars,session):
            session.flash=self.messages.review_posted
            self.redirect(args=request.args)  
        rows=db(ctable.table_name==form.vars.table_name)\
               (ctable.status=='approved')\
               (ctable.record_id==id)\
                 .select(orderby=ctable.created_by)
        def script(row):
            return SCRIPT('$("#rating_%s").rating({maxvalue:%s,curvalue:%s,readonly:true})'%(row.id,ctable.rating.requires.theset[-1],row.rating))
        if not readable:
            items=[]
        else:            
            items=[TR(TD(SPAN(_id='rating_%s'%row.id),script(row),_style='vertical-align:top;'),TD('%(created_signature)s on %(created_on)s says:'%row,BR(),XML(row.body.replace('\n','<br />')),_style='vertical-align:top;')) for row in rows]
        if not items: items=['No Reviews']
        if not writable:
            return DIV(TABLE(_class='reviews',*items),_class='t2-reviews')
        return DIV(TABLE(_class='reviews',*items),H3(subtitle),
                         form,_class='t2-reviews')

    def download(self):
        """
        To use create a controller:

            def donwload(): return t2.download()
        """
        import os
        import gluon.contenttype as c
        request,response,session,cache,T,db=self._globals()
        if not request.args: self._error()     
        name=request.args[-1]
        items=re.compile('(?P<table>.*?)\.(?P<field>.*?)\..*').match(name)
        if not items: self._error()
        t,f=items.group('table'),items.group('field')
        auth=db[t].get('authorization',False)
        if auth and not self.logged_in: return HTTP(404)
        rows=None
        if auth and isinstance(auth,lambda:0):
            rows=db(db[t][f]==name).select()
            if not rows: return HTTP(404)
            if not auth(db[t],rows[0].id): return HTTP(404)
        uploadfield=db[t][f].uploadfield
        if isinstance(uploadfield,str):
            if not rows: rows=db(db[t][f]==name).select()
            if not rows: return HTTP(404)
            response.headers['Content-Type']=c.contenttype(name)
            return rows[0][uploadfield]
        else:
            filename=os.path.join(request.folder,'uploads',name or self._error())
            return response.stream(filename)

    def play(self,filename,player=None,width=450,height=300):
        if not player:
           player=URL(r=self.request,c='static',f='scripts/mediaplayer.swf')
        return XML('<embed  src="%s" width="%s" height="%s" allowscriptaccess="always" allowfullscreen="true" flashvars="file=%s" />' % (player,width,height,filename))

    def register(self,verification=False,sender='',next='login',onaccept=None):
        """
        To use, create a controller:
        
             def register(): return t2.register()
        """
        request,response,session,cache,T,db=self._globals()
        def onaccept2(form):
            db.t2_membership.insert(person_id=form.vars.id,\
              group_id=db.t2_group.insert(name=form.vars.name),\
              status='approved')
            if form.vars.registration_key:
                body=self.messages.register_email_body % dict(form.vars)
                if not self.email(sender=sender,to=form.vars.email,\
                                  subject=self.messages.register_email_subject,
                                  message=body):
                    self.redirect(flash=self.messages.unable_to_send_email)
                session.flash=self.messages.email_sent
            if onaccept: onaccept(form)
        vars={'registration_key': str(uuid.uuid4()) if verification else ''}
        return self.create(self.db.t2_person,vars=vars,\
                           onaccept=onaccept2,next=next)

    def profile(self,next='index'):
        if not self.logged_in: t2.redirect(next)
        request,response,session,cache,T,db=self._globals()
        return self.update(db.t2_person,query=db.t2_person.id==self.person_id,deletable=False)

    @staticmethod
    def _random_password(length=5):
        import random
        s='abcdefghijkmnpqrstuvwxyz234569'
        return ''.join([s[random.randint(0,len(s)-1)] for i in range(length)])

    def reset_password(self,sender='',next='login',email=None):
        """
        To use, create a controller:
        
             def reset_password(): return t2.reset_password()
        """
        request,response,session,cache,T,db=self._globals()
        form=FORM(INPUT(_name='email',
                        requires=[IS_IN_DB(db,'t2_person.email')]),
                  INPUT(_type='submit',_value='Reset Password'))
        if email or form.accepts(request.vars,session):
            password=T2._random_password(5)
            if email: email2=email
            else: email2=form.vars.email
            if not db(db.t2_person.email==email2)\
                    .update(password=CRYPT()(password)[0],registration_key=''):
                self.redirect(flash=self.messages.unable_to_send_email)
            body=self.messages.password_email_body % dict(password=password)
            if not self.email(sender=sender,to=form.vars.email,\
                              subject=self.messages.password_email_subject,
                              message=body):
                if email: return False
                self.redirect(flash=self.messages.unable_to_send_email)
            else:       
                if email: return True
                self.redirect(next,flash=self.messages.email_sent)
        return form

    def login(self,next='index',onlogin=None):
        """
        To use, create a controller:
        
             def login(): return t2.login()
        """
        request,response,session,cache,T,db=self._globals()
        db.t2_person.email.requires=IS_EMAIL()
        form=SQLFORM(db.t2_person,fields=['email','password'],\
                     hidden=dict(_destination=request.vars._destination),
                     _class='t2-login')
        if FORM.accepts(form,request.vars,session):
             rows=db(db.t2_person.email==form.vars.email)\
                    (db.t2_person.password==form.vars.password)\
                    (db.t2_person.registration_key=='').select()
             if rows:
                 session.t2.person_id=rows[0].id
                 session.t2.person_name=rows[0].name
                 session.t2.person_email=rows[0].email
                 session.flash=self.messages.logged_in
                 if onlogin: onlogin(rows[0])
                 if request.vars._destination:
                     redirect(request.vars._destination)
                 self.redirect(next)
             else:
                 session.flash=self.messages.invalid_login
                 self.redirect()
        return form

    def verify(self,next='login'):
        """
        To use, create a controller:
        
             def verify():
                 if t2.verify(): t2.redirect('login')
        """
        request,response,session,cache,T,db=self._globals()
        key=request.vars.key if request.vars.key else self._error()
        rows=db(db.t2_person.registration_key==key).select()
        if not rows: return None        
        rows[0].update_record(registration_key='')
        return rows[0]

    def logout(self,next='index'):
        """
        To use, create a controller:
        
             def logout(): t2.logout(next='index')
        """
        request,response,session,cache,T,db=self._globals()
        session.t2.person_id=None
        session.t2.person_name=None
        session.t2.person_email=None
        session.t2.my_groups_id=None
        if next:
            session.flash=self.messages.logged_out
            self.redirect(next)

    def requires_login(self,next='login'):
        """
        Use as a decorator:

            @requires_login(next='login')
            def myaction(): ...
        """
        request,response,session,cache,T,db=self._globals()
        def g(f):
             def h(*a,**b):
                 if not session.t2.person_id: self.redirect(next,
                     vars={'_destination':request.env.path_info})
                 return f(*a,**b) 
             return h
        return g

    def add_membership(self,person_id,group_id,membership_type='default'):
        """
        t2.add_membership(person_id,group_id,'default')
        
        gives default membership to person_id to group_id
        """
        t=self.db.t2_membership
        t.insert(person_id=person_id,group_id=group_id,
                 membership_type=membership_type)
        session.t2.my_groups_id=None
        return True

    def del_membership(self,person_id,group_id,membership_type='default'):
        """
        t2.del_membership(person_id,group_id,'default')
        
        deletes default membership to person_id to group_id
        """
        t=self.db.t2_membership
        self.db(t.person_id==person_id)(t.group_id==group_id)\
               (t.membership_type==membership_type).delete()
        session.t2.my_groups_id=None
        return True

    def have_membership(self,group_id,membership_type='default'):
        """
        t2.have_membership(group_id,'default')
        
        checks if the logged in user has 'default' membership in group_id
        """
        t=self.db.t2_membership
        return self.db(t.person_id==self.person_id)(t.group_id==group_id)\
               (t.membership_type==membership_type).count()

    def my_memberships(self):
        """
        Gets a list of memberships of the currend logged in person
        """
        t=self.db.t2_membership
        return self.db(t.person_id==self.person_id)\
                      (t.status=='approved').select()

    def add_access(self,table,record_id=0,access_type='default',group_id=None):
        """
        t2.add_access(table,record_id,'default',group_id=None)
        gives 'default' access to group_id to table/record_id.
        if record_id==0 or None then group has access to entire table
        if group_id==0 or None then access is given to the group
        uniquely identifying tthe current user.
        """
        if not group_id: group_id=self.my_groups_id[0]
        t=self.db.t2_access
        t.insert(group_id=group_id,
                 table_name=str(table),
                 record_id=record_id,
                 access_type=access_type)
        return True

    def del_access(self,table,record_id=0,access_type='default',group_id=None):
        """
        t2.del_access(table,record_id,'default',group_id=None)
        removes 'default' access to group_id to table/record_id.
        if record_id==0 or None then group is removed access to entire table
        if group_id==0 or None then access is removed access to the group
        uniquely identifying tthe current user.
        """
        if not group_id: group_id=self.my_groups_id[0]
        t=self.db.t2_access
        self.db(t.group_id==group_id)\
               (t.table_name==str(table))\
               (t.record_id==record_id)\
               (t.access_type==access_type).delete()
        return True

    def have_access(self,table,record_id=0,access_type='default'):
        """
        Checks if current user belongs to any group that has access to
        the table_name/record_id      
        """
        t=self.db.t2_access
        if self.all_in_db:
             count=0
             for id in self.my_groups_id:
                 count+= self.db(t.group_id==id)\
                         (t.table_name==str(table))\
                         (t.record_id==record_id or r.record_id==0)\
                         (t.access_type==access_type).count()
        else: count=self.db(t.group_id.belongs(self.my_groups_id))\
                         (t.table_name==str(table))\
                         (t.record_id==record_id or r.record_id==0)\
                         (t.access_type==access_type).count()
        return count
   
    def email(self,sender,to,subject='test',message='test'):
        """
        Sends an email. Returns True on success, False on failure.
        """
        if not isinstance(to,list): to=[to]
        try:
            if self.is_gae:
                from google.appengine.api import mail
                mail.send_mail(sender=sender,
                               to=to,
                               subject=subject,
                               body=message)
            else:
                msg="From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s"%(sender,\
                    ", ".join(to),subject,message)
                import smtplib, socket
                host, port=self.email_server.split(':')
                # possible bug fix? socket.setdefaulttimeout(None)
                server = smtplib.SMTP(host,port) 
                #server.set_debuglevel(1)
                if self.email_auth:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    username, password=self.email_auth.split(':')
                    server.login(username, password)
                server.sendmail(sender, to, msg)
                server.quit()
        except Exception,e:
            return False
        else: return True

    @staticmethod
    def rating_widget(self,value,callback=None):
        id=self._tablename+'_'+self.name
        ### WORK IN PROGRESS
        script='$("#%s").rating({url:%s,maxvalue:%s});' % \
              (id,repr(callback) if callback!=None else 'null',
               self.requires.theset[-1])
        return DIV(INPUT(_type='hidden',_name=self.name,_value=value,_id=id),
                   SCRIPT(script))

    @staticmethod
    def tag_widget(self,value,tags=[]):
        script=SCRIPT("""
        function web2py_tag(self,other,tag) {
           var o=document.getElementById(other)
           if(self.className=='tag_on') {
             self.setAttribute('class','tag_off');
             o.value=o.value.replace('['+tag+']','');
           } else if(self.className=='tag_off') {
             self.setAttribute('class','tag_on');
             o.value=o.value+'['+tag+']';
           }
        }""")
        id=self._tablename+'_'+self.name
        def onclick(x): return "web2py_tag(this,'%s','%s');"%(id,x)
        if tags and not isinstance(tags[0],(list,tuple)): tags=[tags]       
        buttons=[DIV(_class='tag_row',
                 *[SPAN(A(x,_class='tag_on' if value and '[%s]'%x \
                 in value else 'tag_off',_onclick=onclick(x)),\
                 _class="tag_col") for x in tag_line]) for tag_line in tags]
        return DIV(script,INPUT(_type='hidden',_id=id,_name=self.name,
                                _value=value),*buttons)

    def clear_cart(self):
        self.session.t2.cart=[]
        return True

    def add_to_cart(self,name,price,quantity=1,
                  description='',weight=0,height=0,length=0,depth=0,currency='USD',weight_unit='LB'):
        if not self.session.t2.cart: self.session.t2.cart=[]
        self.session.t2.cart.append(dict(
            name=name,
            description=description,
            price=price,
            weight=weight,
            weight_unit=weight_unit,
            height=height,
            length=length,
            depth=depth,
            quantity=quantity,
            currency=currency))
        return True

    def checkout_cart(self,merchant_id,action_url,button_url,continue_url,
                      attributes={}):
        keys=['name','description','quantity','price','weight',\
              'currency','weight_unit']
        items=[]
        for k,product in enumerate(self.session.t2.cart):
            for key in keys:
                items.append(INPUT(_type='hidden',
                                   _name='item_%s_%s'%(key,k+1),
                                   _value=str(product[key])))
        items.append(INPUT(_name="_charset_",_type="hidden",_value="utf-8"))
        for name,value in attributes.items():
            items.append(INPUT(_type="hidden",_name=name,_value=value))
        items.append(INPUT(_type="hidden",_name="continue_url",
                           _value=continue_url))
        items.append(INPUT(_src=button_url % merchant_id,_type="image"))
        form=FORM(_action=action_url % merchant_id,
                  _id="BB_BuyButtonForm",
                  _method="POST",
                  _enctype=None,
                  _name="BB_BuyButtonForm",*items)
        return form

    @staticmethod
    def urlopen(url):
        try:
            from google.appengine.api.urlfetch import fetch
            if url.find('?')>=0:
                url,payload=url.split('?')
                return fetch(url,payload=payload).content
            return fetch(url).content
        except:
            import urllib
            return urllib.urlopen(url).read()
    @staticmethod
    def coords_by_address(address):
        import re
        try: 
            txt=T2.urlopen('http://maps.google.com/maps/geo?q=%s&output=xml'%address)
            item=re.compile('\<coordinates\>(?P<la>[^,]*),(?P<lo>[^,]*).*?\</coordinates\>').search(txt)
            la,lo=float(item.group('la')),float(item.group('lo'))
            return la,lo
        except: return 0.0,0.0

    @staticmethod
    def barchart(data,width=400,height=15,scale=None,
                 label_width=50,values_width=50):
        if not scale: scale=max([m for n,c,m in data])
        if not scale: return None
        return TABLE(_class='barchart',
               *[TR(TD(n,_width=label_width,_style="text-align: right"),
               TABLE(TR(TD(_width=int(m*width/scale),_height=height,
               _style='background-color:'+c))),TD(m,_width=values_width),
               _style="vertical-alignment: middle") for n,c,m in data])

    

COUNTRIES=['United States', 'Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Antigua and Barbuda', 'Argentina', 'Armenia', 'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bhutan', 'Bolivia', 'Bosnia and Herzegovina', 'Botswana', 'Brazil', 'Brunei', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Cambodia', 'Cameroon', 'Canada', 'Cape Verde', 'Central African Republic', 'Chad', 'Chile', 'China', 'Colombia', 'Comoros', 'Congo', 'Costa Rica', "C&ocirc;te d'Ivoire", 'Croatia', 'Cuba', 'Cyprus', 'Czech Republic', 'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic', 'East Timor', 'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Ethiopia', 'Fiji', 'Finland', 'France', 'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Greece', 'Grenada', 'Guatemala', 'Guinea', 'Guinea-Bissau', 'Guyana', 'Haiti', 'Honduras', 'Hong Kong', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland', 'Israel', 'Italy', 'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya', 'Kiribati', 'North Korea','South Korea', 'Kuwait', 'Kyrgyzstan', 'Laos', 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Macedonia', 'Madagascar', 'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Mauritania', 'Mauritius', 'Mexico', 'Micronesia', 'Moldova', 'Monaco', 'Mongolia', 'Montenegro', 'Morocco', 'Mozambique', 'Myanmar', 'Namibia', 'Nauru', 'Nepal', 'Netherlands', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'Norway', 'Oman', 'Pakistan', 'Palau', 'Palestine', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal', 'Puerto Rico', 'Qatar', 'Romania', 'Russia', 'Rwanda', 'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Vincent and the Grenadines', 'Samoa', 'San Marino', 'Sao Tome and Principe', 'Saudi Arabia', 'Senegal', 'Serbia and Montenegro', 'Seychelles', 'Sierra Leone', 'Singapore', 'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia', 'South Africa', 'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'Swaziland', 'Sweden', 'Switzerland', 'Syria', 'Taiwan', 'Tajikistan', 'Tanzania', 'Thailand', 'Togo', 'Tonga', 'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkmenistan', 'Tuvalu', 'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'Uruguay', 'Uzbekistan', 'Vanuatu', 'Vatican City', 'Venezuela', 'Vietnam', 'Yemen', 'Zambia', 'Zimbabwe']



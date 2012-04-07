#############################################
### general variables
#############################################

from gluon.sqlhtml import form_factory

#############################################
# The main public page
#############################################

#@cache(request.env.path_info,time_expire=60*5,cache_model=cache.ram)
def index():
    redirect(URL(c='about', f='index'))
    response.files.append(URL(r=request,c='static',f='jquery-slideshow.css'))
    response.files.append(URL(r=request,c='static',f='jquery-slideshow.js'))
    session.forget()
    # do not cache flatpage edits!:
    if True: ##request.vars or request.args or request.flash or session.flash or auth.is_logged_in():
        r = response.render(plugin_flatpage()) 
    else:
        r = cache.ram(request.env.path_info,lambda: response.render(plugin_flatpage()), time_expire=60*5)
    return r

#@cache(request.env.path_info,time_expire=60*15,cache_model=cache.ram)
def about():
    return response.render(dict())

@cache(request.env.path_info,time_expire=60*15,cache_model=cache.ram)
def twitter():
    session.forget()
    session._unlock(response)
    import gluon.tools
    import gluon.contrib.simplejson as sj
    try:
        if TWITTER_HASH:
            page = gluon.tools.fetch('http://twitter.com/%s?format=json'%TWITTER_HASH)
            return sj.loads(page)['#timeline']
        else:
            return 'disabled'
    except Exception, e:
        return DIV(T('Unable to download because:'),BR(),str(e))

#############################################
# Allow registered visitors to download
#############################################

@auth.requires_login()
def download(): 
    return response.download(request,db)

###@cache(request.env.path_info,60,cache.disk)
def fast_download():
    # very basic security:
    if not request.args(0).startswith("sponsor.logo") and not request.args(0).startswith("auth_user.photo") and not request.args(0).startswith("attachment.file"): 
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

def notify():
    response.headers['Content-Type']='text/xml'
    return l2controller.receive_xml(request.body.read())

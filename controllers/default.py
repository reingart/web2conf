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

def about():
    return dict()

#############################################
# Allow registered visitors to download
#############################################

@auth.requires_login()
def download(): 
    return response.download(request,db)

###@cache(request.env.path_info,60,cache.disk)
def fast_download():
    # very basic security:
    if not request.args(0).startswith("sponsor.logo"): 
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

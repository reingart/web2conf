#############################################
### general variables
#############################################

from gluon.sqlhtml import form_factory

#############################################
# The main public page
#############################################

#@cache(request.env.path_info,time_expire=60*5,cache_model=cache.ram)
def index():
    ## for pycontech: redirect(URL(c='about', f='index'))
    response.files.append(URL(r=request,c='static',f='jquery-slideshow.css'))
    response.files.append(URL(r=request,c='static',f='jquery-slideshow.js'))
    session.forget()
    # do not cache flatpage edits!:
    if request.vars or request.args or request.flash or session.flash or auth.is_logged_in():
        r = response.render(plugin_flatpage()) 
    else:
        r = cache.ram(request.env.path_info,lambda: response.render(plugin_flatpage()), time_expire=60*5)
    return r

#@cache(request.env.path_info,time_expire=60*15,cache_model=cache.ram)
def about():
    return response.render(dict())

# @cache(request.env.path_info,time_expire=60*15,cache_model=cache.ram)
def twitter():
    session.forget()
    session._unlock(response)
    import urllib
    import gluon.contrib.simplejson as sj
    try:
        if TWITTER_HASH:
            # tweets = urllib.urlopen('http://twitter.com/%s?format=json' % TWITTER_HASH).read()
            tweets = urllib.urlopen("http://search.twitter.com/search.json?q=%%40%s" % TWITTER_HASH).read()
            data = sj.loads(tweets, encoding="utf-8")
            the_tweets = dict()
            
            for obj in data["results"]:
                the_tweets[obj["id"]] = (obj["created_at"], obj["from_user"], obj["profile_image_url"], obj["text"])
            return dict(message = None, tweets = the_tweets)
        else:
            return dict(tweets = None, message = 'disabled')

    except Exception, e:
        return dict(tweets = None, message = DIV(T('Unable to download because:'),BR(),str(e)))

#############################################
# Allow registered visitors to download
#############################################

@auth.requires_login()
def download(): 
    return response.download(request,db)

###@cache(request.env.path_info,60,cache.disk)
def fast_download():
    # very basic security:
    if not request.args(0).startswith("sponsor.logo") and \
    not request.args(0).startswith("sponsor.image") and \
    not request.args(0).startswith("auth_user.photo") and \
    not request.args(0).startswith("attachment.file"):
        return download()
    if 'filename' in request.vars:
        response.headers["Content-Disposition"] \
        = "attachment; filename=%s" % request.vars['filename']

    # remove/add headers that prevent/favors caching
    del response.headers['Cache-Control']
    del response.headers['Pragma']
    del response.headers['Expires']
    filename = os.path.join(request.folder,'uploads',request.args(0))
    response.headers['Last-Modified'] = time.strftime( \
    "%a, %d %b %Y %H:%M:%S +0000", time.localtime( \
    os.path.getmtime(filename)))
    return response.stream(open(filename,'rb'))

def notify():
    response.headers['Content-Type']='text/xml'
    return l2controller.receive_xml(request.body.read())


#############################################
# web2py planet
#############################################

def get_planet_rss(arg):
    import datetime
    import re
    import gluon.contrib.rss2 as rss2
    import gluon.contrib.feedparser as feedparser

    # filter for general (not categorized) feeds
    regex =  re.compile('web2py',re.I)

    feeds = db(db.feed.id>0).select()

    entries = []

    for feed in feeds:
        # fetch and parse feeds
        d = feedparser.parse(feed.url)
        for entry in d.entries:
            if not feed.general or regex.search(entry.description):
                # extract entry attributes
                entries.append({
                    'feed': {'author':feed.author,'link':feed.link, \
                    'url':feed.url,'name':feed.name},
                    'title': entry.title,
                    'link': entry.link,
                    'description': entry.description,
                    'author': hasattr(entry, 'author_detail')
                         and entry.author_detail.name
                          or feed.author,
                    'date': datetime.datetime(*entry.date_parsed[:6])
                })

    # sort entries by date, descending
    entries.sort(key=lambda x: x['date'],reverse=True)

    now = datetime.datetime.now()

    # aggregate rss2 feed with parsed entries
    rss = rss2.RSS2(title=PLANET_TITLE,
       link = URL(r=request,c="default",f="planet"),
       description = PLANET_DESCRIPTION,
       lastBuildDate = now,
       items = [
          rss2.RSSItem(
            title = entry['title'],
            link = entry['link'],
            description = entry['description'],
            author = entry['author'],
            # guid = rss2.Guid('unkown'),
            pubDate = entry['date']) for entry in entries]
       )

    return rss


# feeds action
def planet():
    import gluon.contrib.rss2 as rss2
    rss = get_planet_rss(None)

    # .rss requests
    if request.extension == "rss":
        # return new rss feed xml
        response.headers['Content-Type']='application/rss+xml'
        return rss2.dumps(rss)

    # else send the rss object to be processed by
    # the view
    
    return dict(rss = rss, rss2 = rss2)

def privacy(): return plugin_flatpage()

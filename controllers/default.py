#############################################
# The main public page
#############################################

@caching
def index():
    ## for pycontech: redirect(URL(c='about', f='index'))
    response.files.append(URL(r=request,c='static',f='jquery-slideshow.css'))
    response.files.append(URL(r=request,c='static',f='jquery-slideshow.js'))
    response.reg_count = cache.ram(request.env.path_info + ".reg_count", 
                                   lambda: db(db.auth_user).count(), 
                                   time_expire=60*5)
    days = (CONFERENCE_DATE.date() - TODAY_DATE.date()).days
    response.days_left = days if days > 0 else 0
    return response.render(plugin_flatpage()) 
    
@caching
def about():
    return response.render(dict())


def twitter_post(username,password,message):
    """ Example from web2py-users group by Massimo Di Pierro

    Send a tweet with twitter API"""
    import urllib, urllib2, base64, gluon.contrib.simplejson
    args = urllib.urlencode([('status',message)])
    headers={}
    headers['Authorization'] = 'Basic '+ base64.b64encode(username + ':' + password)
    req = urllib2.Request('http://twitter.com/statuses/update.json', args, headers)
    try:
        return  gluon.contrib.simplejson.loads(urllib2.urlopen(req).read())
    except urllib2.HTTPError, e:
        return e


def tweet():
    if session.has_key("tweet_password"):
        hidden=dict(password=session.tweet_password,
                    account=session.tweet_account,
                    remember=True)
    else:
        hidden = dict()

    form = SQLFORM.factory(Field("account"),
                           Field("password", "password",
                                 label=T("password")),
                           Field("remember", "boolean",
                                 label=T("remember my twitter password"),
                                 default=False),
                           Field("message", "text", requires=IS_NOT_EMPTY()),
                           hidden=hidden)

    if form.process(formname="tweet").accepted:
        data = twitter_post(form.vars.account,
                            form.vars.password,
                            "#%s %s" % (TWITTER_HASH, form.vars.message))
        response.flash = DIV(H5("Twitter API:"), data)
    elif form.errors:
        response.flash = DIV(H5(T("Could not send the tweet"), "<br />".join(errors)))

    return dict(form=form)


@cache(request.env.path_info,time_expire=60*15,cache_model=cache.ram)
def twitter():
    session.forget()
    session._unlock(response)
    import urllib
    import gluon.contrib.simplejson as sj
    try:
        if TWITTER_HASH:
            # tweets = urllib.urlopen('http://twitter.com/%s?format=json' % TWITTER_HASH).read()
            try: 
                tweets = cache.disk(request.env.path_info + ".tweets", 
                                               lambda: urllib.urlopen("http://search.twitter.com/search.json?q=%s" % TWITTER_HASH).read(), 
                                               time_expire=60*15)
            except:
               import os
               # manually clean cache (just in case)
               path = os.path.join(request.folder,'cache')
               for f in os.listdir(path):
                    try:
                        if f[:1]!='.': os.unlink(os.path.join(path,f))
                    except IOError:
                        r = False
               # try to reload
               redirect(URL("twitter"))       
            
            data = sj.loads(tweets, encoding="utf-8")
            the_tweets = dict()
            
            for obj in data["results"]:
                the_tweets[obj["id"]] = (obj["created_at"], obj["from_user"], obj["profile_image_url"], obj["text"])
            ret = dict(message = None, tweets = the_tweets)
        else:
            ret = dict(tweets = None, message = 'disabled')

    except Exception, e:
        ret = dict(tweets = None, message = DIV(T('Unable to download because:'),BR(),str(e)))
    return response.render(ret)


#############################################
# Allow registered visitors to download
#############################################

@auth.requires_login()
def download(): 
    return response.download(request,db)

###@cache(request.env.path_info,60,cache.disk)
def fast_download():
    if not request.args:
        raise HTTP(404)
    # very basic security:
    if not request.args(0).startswith("sponsor.logo") and \
    not request.args(0).startswith("sponsor.image") and \
    not request.args(0).startswith("auth_user.photo") and \
    not request.args(0).startswith("activity.logo") and \
    not request.args(0).startswith("attachment.file"):
        return download()
    if 'filename' in request.vars:
        response.headers["Content-Disposition"] \
        = "attachment; filename=%s" % request.vars['filename']

    import os.path, gluon.contenttype
    ext = os.path.splitext(request.args(0))[1]
    response.headers['Content-Type'] = gluon.contenttype.contenttype(ext)
    
    # remove/add headers that prevent/favors caching
    del response.headers['Cache-Control']
    del response.headers['Pragma']
    del response.headers['Expires']
    filename = os.path.join(request.folder,'uploads',request.args(0))

    # resize speaker pictures!
    stream = open(filename,'rb')
    ext = os.path.splitext(request.args[0])[1].lower()
    if request.args(0).startswith("auth_user.photo") and not ext.endswith(".gif"):
        from image_utils import rescale
        temp = os.path.join(request.folder, 'private', 'photos', request.args[0])
        if not os.path.exists(temp):
            if ext in (".jpg", ".jpeg", ".face"):
                format = "JPEG"
            elif ext in (".png"):
                format = "PNG"
            else:
                raise RuntimeError("Unknown image extension %s" % ext)
            f = open(temp, "wb")
            data = rescale(stream.read(), 100, 100, tmp=f, format=format, force=True)
            f.close()
        stream.close()
        filename = temp
        stream = open(temp, "rb")

    response.headers['Last-Modified'] = time.strftime( \
    "%a, %d %b %Y %H:%M:%S +0000", time.localtime( \
    os.path.getmtime(filename)))
    return response.stream(open(filename,'rb'))

def notify():
    response.headers['Content-Type']='text/xml'
    return l2controller.receive_xml(request.body.read())

def user():
    redirect(URL(c='user', f=request.args[0], args=request.args[1:]))

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
@caching
def planet():
    #return ""
    import gluon.contrib.rss2 as rss2

    # store planet rss entries in disk (forever...)
    import portalocker
    import os, cPickle as pickle
    path = os.path.join(request.folder,'cache', "planet.rss")
    if not os.path.exists(path):
        f = open(path, "w+")
        rss = get_planet_rss(None)
        rss = [{'title': item.title, 'author': item.author, 'pubDate': item.pubDate, 'link': item.link, 'description': item.description} for item in rss.items]
    else:
        f = open(path, "r+")
        rss = None
    portalocker.lock(f, portalocker.LOCK_EX)
    if not rss:
        rss = pickle.load(f)
    else:
        f.seek(0)
        pickle.dump(rss, f)
    portalocker.unlock(f)
    f.close()

    # .rss requests
    if request.extension == "rss":
        # return new rss feed xml
        response.headers['Content-Type']='application/rss+xml'
        return rss2.dumps(rss)

    # else send the rss object to be processed by
    # the view
    
    return response.render(dict(rss = rss, rss2 = rss2))

def privacy(): return plugin_flatpage()

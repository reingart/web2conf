#############################################
### FOR ALL ATTENDEES
#############################################

@cache(request.env.path_info,time_expire=60,cache_model=cache.ram)
def companies():
    if auth.has_membership(role='manager'): s=db()
    else: s=db(db.auth_user.include_in_delegate_listing==True)
    rows=s.select(db.auth_user.company_name,
                  db.auth_user.company_home_page,
                  orderby=db.auth_user.company_name,distinct=True)
    return dict(rows=rows)
    
@cache(request.env.path_info,time_expire=60,cache_model=cache.ram)
def attendees():
    if auth.has_membership(role='manager'): s=db(db.auth_user.attendee_type!='non_attending')
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

    def barchart(data,width=400,height=15,scale=None,
                 label_width=50,values_width=50):
        if not scale: scale=max([m for n,c,m in data])
        if not scale: return None
        return TABLE(_class='barchart',
               *[TR(TD(n,_width=label_width,_style="text-align: right"),
               TABLE(TR(TD(_width=int(m*width/scale),_height=height,
               _style='background-color:'+c))),TD(m,_width=values_width),
               _style="vertical-alignment: middle") for n,c,m in data])

    def colorize(d,sort_key=lambda x:x):
        s=[(m,n) for n,m in d.items()]
        s.sort(key=sort_key)
        s.reverse()
            
        t=[(x[1],colors[i % len(colors)],x[0]) for i,x in enumerate(s)]
        return barchart(t,label_width=150)   
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
            db.auth_user.personal_home_page,
            db.auth_user.include_in_delegate_listing)
    x0,y0=CONFERENCE_COORDS
    return dict(googlemap_key=GOOGLEMAP_KEY,x0=x0,y0=y0,rows=rows)

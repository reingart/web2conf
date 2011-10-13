def coords_by_address(person):
        import re, urllib
        try:
            address=urllib.quote("%s, %s %s, %s" % (person.city,person.state,person.zip_code,person.country))
            t=urllib.urlopen('http://maps.google.com/maps/geo?q=%s&output=xml'%address).read()
            item=re.compile('\<coordinates\>(?P<la>[^,]*),(?P<lo>[^,]*).*?\</coordinates\>').search(t)
            la,lo=float(item.group('la')),float(item.group('lo'))
            return la,lo
        except Exception, e: 
            #raise RuntimeError(str(e))
            pass
        #raise RuntimeError(str("%s = %s" % (address, t)))
        return 0.0,0.0

def update_zip(person):    
    ### compute zip code
    import shelve,os
    ##if not person.zip_code: return
    """
    code=person.zip_code.strip()[:5]
    if not is_gae:
       zips=shelve.open(os.path.join(request.folder,'private/zips.shelve'))
    if not is_gae and person.country=='United States' and zips.has_key(code):
        la,lo,city,state=zips[code]
    else:
        la,lo=0.0,0.0
    """
    lo,la=coords_by_address(person)
    db(db.auth_user.id==person.id).update(latitude=la, longitude=lo)
    return lo,la

def update_billed_amount(person):
    ### person here can be a form instead of a record but should be record
    if not person.update_record:
       person=db(db.auth_user.id==person.id).select()[0]
    due=ATTENDEE_TYPE_COST[person.attendee_type]
    tutorials=0
    for key in TUTORIALS.keys():
        if person.tutorials and person.tutorials.find('|%s|'%key)>=0:
            tutorials+=1
    if tutorials: due+=COST_FIRST_TUTORIAL+COST_SECOND_TUTORIAL*max(tutorials-1,0)
    coupons=db((db.coupon.name==person.discount_coupon)&((db.coupon.person==None)|(db.coupon.person==person.id))).select()
    if coupons:
        coupon=coupons[0]
        if coupon.auto_match_registration:
            coupon.update_record(discount=ATTENDEE_TYPE_COST[person.attendee_type])
        due=max(0.0,due-coupon.discount)
        coupon.update_record(person=person.id)
    if person.donation: 
        due+=person.donation ### add donation
    db(db.auth_user.id==person.id).update(amount_billed=due)
    return due

def update_person(form):
    if not ENABLE_PAYMENTS:
        return
    update_zip(form.vars)
    return update_billed_amount(form.vars)

def update_pay(person):
    if not ENABLE_PAYMENTS:
        return
    if not person.update_record:
       person=db(db.auth_user.id==person.id).select()[0]
    update_billed_amount(person)
    transfers_in=db(db.money_transfer.to_person==person.id)\
                   (db.money_transfer.from_person==db.auth_user.id).select()
    transfers_out=db(db.money_transfer.from_person==person.id).select()
    payments=db(db.payment.from_person==person.id).select()
    amount_added=0.0    
    for row in transfers_in:
        amount_added+=row.money_transfer.amount
    amount_subtracted=0.0
    for row in transfers_out:
        if row.approved: amount_subtracted+=row.amount
    amount_paid=0.0
    for row in payments:
        if row.status.lower()=='charged': amount_paid+=row.amount   
    session.amount_billed=person.amount_billed
    session.amount_paid=amount_paid
    session.amount_added=amount_added
    session.amount_subtracted=amount_subtracted
    session.balance=balance=person.amount_billed+amount_added-amount_subtracted-amount_paid
    db(db.auth_user.id==person.id).update(amount_added=amount_added,amount_subtracted=amount_subtracted,amount_paid=amount_paid,amount_due=balance)
    return transfers_in, transfers_out, payments

#######
# for testing
#######

#if not db(db.coupon.id>0).count():
#    [db.coupon.insert(name=str(uuid.uuid4())) for i in range(100)]

def fill_just_data():
    if db(db.auth_user.id>0).count()<100:
        db(db.auth_user.id>0).delete()
        import random, shelve,os
        if not is_gae:
            zips=shelve.open(os.path.join(request.folder,'private/zips.shelve'))
        def r(t=None):       
            if not t: return ''.join([['da','du','ma','mo','ce','co','pa','po','sa','so','ta','to'][random.randint(0,11)] for i in range(3)]) 
            return t[random.randint(0,len(t)-1)]
        for k in range(100):
            name=r()
            comp=r()
            zip=str(random.randint(10000,99999))
            if not is_gae: la,lo,city,state=zips[zip] if zips.has_key(zip) else (0.,0.,'','')
            else: lo,la=0.0,0.0
            db.auth_user.insert(name=name+str(k),first_name=name.capitalize(),last_name=r().capitalize(),email=name+'@'+comp+'.com',company_name=comp.capitalize()+' Corp.',include_in_delegate_listing=True,food_preference=r(FOOD_PREFERENCES),t_shirt_size=r(T_SHIRT_SIZES),country=r(COUNTRIES),attendee_type=r(ATTENDEE_TYPES.keys()),tutorials='[web2py]',latitude=la,longitude=lo,zip_code=zip,personal_home_page='http://www.%s.com'%comp,company_home_page='http://www.%s.com'%comp)

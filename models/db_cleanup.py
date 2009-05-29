db(db.payment.created_on<t2.now-datetime.timedelta(1))(db.payment.status.lower()=='pre-processing').delete()

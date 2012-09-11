db0 = DAL('sqlite://development_last.db')


for table in db.tables:
    print "copying %s" % table
    query = db[table]._id > 0
    rows = db(query).select()
    colnames = [k[k.index(".")+1:] for k in rows.colnames]
    print db._lastsql
    print colnames
    rows = db0.executesql(db._lastsql)
    # clean up table
    db.executesql("TRUNCATE %s" % table)
    for i, row in enumerate(rows):
      print "inserting", i, len(rows)
      sql = "INSERT INTO %s (%s) VALUES (%s)" % (
              table,
              ','.join(colnames),
              ','.join(["%s" for k in colnames]),
              )
      print sql
      db.executesql(sql, row)
    # update serials
    db.executesql("select setval('%s_%s_seq'::regclass, (SELECT MAX(%s) FROM %s));" % (
      table, colnames[0], colnames[0], table))
db.commit()
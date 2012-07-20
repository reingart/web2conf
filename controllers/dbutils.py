# -*- coding: utf-8 -*-
# intente algo como

response.generic_patterns = ["*",]

def index(): return dict(message="hello from dbutils.py")

def data():
    datafile = os.path.join(request.folder, "private/db.csv")
    if request.args[0] == "export":
        result = db.export_to_csv_file(open(datafile, "wb"))
    elif request.args[0] == "import":
        result = db.import_from_csv_file(open(datafile, "rb"))
    else:
        raise HTTP(500, "action not supported")
    return dict(action=request.args[0], result=result)

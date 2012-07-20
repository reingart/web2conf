# -*- coding: utf-8 -*-

#    plugin_dineromail: DineroMail web2py plugin
#    Copyright (C) 2012 Alan Etkin
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    * Web2py is Licensed under the LGPL license version 3
#    (http://www.gnu.org/licenses/lgpl.html)
#    Copyright (c) by Massimo Di Pierro (2007-2011)
#
#    contact: spametki@gmail.com


# function or lambda, for calling after each payment notification
# example:
# PLUGIN_DINEROMAIL_ON_UPDATE = lambda data: my_function(data["client_code"])
# where data stores the updated record fields
# client_code is the alphanumeric id used for the web-store button or form

if not "PLUGIN_DINEROMAIL_ON_UPDATE" in globals():
    PLUGIN_DINEROMAIL_ON_UPDATE = None

# Create and keep this variables in private model files
if not "PLUGIN_DINEROMAIL_ACCOUNT" in globals():
    PLUGIN_DINEROMAIL_ACCOUNT = None

if not "PLUGIN_DINEROMAIL_PASSWORD" in globals():
    PLUGIN_DINEROMAIL_PASSWORD = None

if not "PLUGIN_DINEROMAIL_COUNTRY" in globals():
    PLUGIN_DINEROMAIL_COUNTRY = None # mexico, argentina, chile, brasil, ...

PLUGIN_DINEROMAIL_URLS = {"mexico": "http://mexico.dineromail.com/vender/Consulta_IPN.asp",
                          "chile": "http://chile.dineromail.com/vender/Consulta_IPN.asp",
                          "argentina": "http://argentina.dineromail.com/vender/Consulta_IPN.asp",
                          "brasil": "http://brasil.dineromail.com/vender/Consulta_IPN.asp"}

PLUGIN_DINEROMAIL_SHOP_CHECK_IN = {"mexico": None,
                          "chile": None,
                          "argentina": "https://argentina.dineromail.com/Shop/Shop_Ingreso.asp",
                          "brasil": None}

PLUGIN_DINEROMAIL_REPORT_STATUSES = {1: T("Correct"),
                                     2: T("Malformed"),
                                     3: T("Invalid account number"),
                                     4: T("Invalid password"),
                                     5: T("Invalid query type"),
                                     6: T("Ivalid operation ID"),
                                     7: T("Invalid account or password"),
                                     8: T("No operations found")}
                                     
PLUGIN_DINEROMAIL_STATUSES = {1: T("Pending"), 2: T("Credited"),
                              3: T("Cancelled")}
                              
PLUGIN_DINEROMAIL_METHODS = {1: T("DineroMail funds"),
                             2: T("Cash (or third party cash services"),
                             3: T("Credit card"),
                             4: T("Bank account transfer"),
                             5: T("Cash (Oxxo or 7Eleven)")}
                             
PLUGIN_DINEROMAIL_CURRENCIES = {1: T("Pesos/Reales"), 2: T("USD")}

# account movement notifications sent by the webservice
db.define_table("plugin_dineromail_notification",
                Field("posted", "datetime",
                      default=request.now,
                      writable=False,
                      comment=T("Date and time of submission")),
                Field("category", comment=T("Type of notification")),
                Field("operation_type", comment=T("Type of operation")),
                Field("code", comment=T("Operation number")),
                migrate=migrate, fake_migrate=fake_migrate)

# Stores webservice updated operation status
db.define_table("plugin_dineromail_operation",
                Field("report_status", "integer",
                      represent=lambda status, row: \
                      PLUGIN_DINEROMAIL_REPORT_STATUSES[status]),
                Field("code", unique=True), # webservice operation id
                Field("posted"),
                Field("status", "integer",
                      represent=lambda status, row: \
                      PLUGIN_DINEROMAIL_STATUSES[status]),
                Field("client_code"), # client transaction_id
                Field("customer_email"),
                Field("customer_address"),
                Field("customer_comment"),
                Field("customer_name"),
                Field("customer_phone"),
                Field("customer_document_type"),
                Field("customer_document_number"),
                Field("amount"),
                Field("net_amount"),
                Field("method", "integer",
                      represent=lambda method, row: \
                      PLUGIN_DINEROMAIL_METHODS[method]),
                Field("means"),
                Field("installments"),
                Field("sales_document_type"),
                Field("sales_document_number"),
                Field("item_descriptions", "list:string"),
                Field("item_currencies", "list:string"),
                Field("item_prices", "list:string"),
                Field("item_quantities", "list:string"),
                migrate=migrate, fake_migrate=fake_migrate)

def plugin_dineromail_update_reports(data):
    # retrieve webservice reports
    # TODO: complete transaction xml mapping to local db
    # and return readable report logs
    message = None
    import urllib
    import urllib2
    query = plugin_dineromail_create_query(data)
    query_data = urllib.urlencode({"data": query})
    f = urllib2.urlopen(PLUGIN_DINEROMAIL_URLS[PLUGIN_DINEROMAIL_COUNTRY],
                        query_data)
    tag = TAG(f.read())
    # check if report is ok
    if int(tag.element("estadoreporte").flatten()) == 1:
        for operation in tag.elements("operacion"):
            row_data = dict(item_descriptions=list(),
                            item_quantities=list(),
                            item_currencies=list(),
                            item_prices=list())

            row_data["report_status"] = tag.element("estadoreporte").flatten()
            row_data["code"] = operation.element("id").flatten()
            row_data["posted"] = operation.element("fecha").flatten()
            row_data["status"] = operation.element("estado").flatten()
            row_data["client_code"] = \
                operation.element("numtransaccion").flatten()
            row_data["customer_email"] = \
                operation.element("comprador").element("email").flatten()
            row_data["customer_name"] = \
                peration.element("comprador").element("nombre").flatten()
            row_data["customer_document_number"] = \
                operation.element("comprador").element("numerodoc").flatten()
            
            for item in operation.elements("item"):
                row_data["item_descriptions"].append(
                    item.element("descripcion").flatten())
                row_data["item_currencies"].append(
                    PLUGIN_DINEROMAIL_CURRENCIES[
                        int(item.element("moneda").flatten())]
                        )
                row_data["item_prices"].append(item.element("preciounitario").flatten())
                row_data["item_quantities"].append(item.element("cantidad").flatten())

            # operation id lookup
            row = db(db.plugin_dineromail_operation.code == \
                operation.element("id").flatten()).select().first()
            
            if row is not None:
                row.update_record(**row_data)
            else:
                db.plugin_dineromail_operation.insert(**row_data)

            # Send data to the app's callback if defined
            if PLUGIN_DINEROMAIL_ON_UPDATE is not None:
                PLUGIN_DINEROMAIL_ON_UPDATE(row_data)

        return (True, message)
    # for each report instance
    # update local operation records
    return (False, message)

# build a basic query for the remote payment database
def plugin_dineromail_create_query(data):
    if isinstance(data, basestring):
        data = [data,]
    ids = "".join(["<ID>%s</ID>" % o for o in data])
    operations = "<OPERACIONES>%s</OPERACIONES>" % ids

    account = PLUGIN_DINEROMAIL_ACCOUNT
    password = PLUGIN_DINEROMAIL_PASSWORD

    report = 1
    query = """
<REPORTE>
  <NROCTA>%(account)s</NROCTA>
  <DETALLE>
    <CONSULTA>
      <CLAVE>%(password)s</CLAVE>
      <TIPO>%(report)s</TIPO>
      %(operations)s
    </CONSULTA>
  </DETALLE>
</REPORTE>
    """ % {"account": account, "password": password,
           "report": report, "operations": operations}
    return query

def plugin_dineromail_check_status(transaction, update=False):
    """ Return transaction status updating
    from webservice if specified.

    transaction is the id generated for button, form or link
    used in the client application.
    returns the (state, description) of the operation if found or
    (None, None)
    update=<bool> is optional and forces a remote operation
    details update.
    """

    # Get the locally stored transaction detail
    operation = db(db.plugin_dineromail.client_code == \
    transaction).select().first()
    
    if update and operation is not None:
        result, message = \
        plugin_dineromail_update_reports([operation.code,])
        # reload record from db
        operation = db.plugin_dineromail_operation[operation.id]

    try:
        status = operation.status
        description = PLUGIN_DINEROMAIL_STATUSES[status]
    except (AttributeError, KeyError), e:
        status = None
        description = None
        
    return status, description

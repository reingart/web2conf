# coding: utf8

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

def index(): return dict(message="hello from plugin_dineromail_default.py")

def notify():
    data = request.vars["Notificacion"]
    
    try:
        tag = TAG(data)
    except (KeyError, ValueError, TypeError, AttributeError), e:
        # Invalid or malformed data
        raise HTTP(500, T("Error parsing request data %s") % e)

    category = str(tag.element("tiponotificacion").flatten())
    operations = []
    
    for operation in tag.elements("operacion"):
        code = str(operation.element("id").flatten())
        operations.append(code)
        operation_type = str(operation.element("tipo").flatten())
        notification_id = \
        db.plugin_dineromail_notification.insert(category=category,
                                                 operation_type=operation_type,
                                                 code=code)

    # commit notifications in case there's a webservice error
    db.commit()

    # Command for retrieving operation details for each transaction
    result, message = plugin_dineromail_update_reports(operations)
    return T("Done!")

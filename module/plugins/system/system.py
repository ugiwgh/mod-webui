#!/usr/bin/python

# -*- coding: utf-8 -*-

# Copyright (C) 2009-2012:
#    Gabes Jean, naparuba@gmail.com
#    Gerhard Lausser, Gerhard.Lausser@consol.de
#    Gregory Starck, g.starck@gmail.com
#    Hartmut Goebel, h.goebel@goebel-consult.de
#
# This file is part of Shinken.
#
# Shinken is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Shinken is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Shinken.  If not, see <http://www.gnu.org/licenses/>.

import time

# Mongodb lib
try:
    import pymongo
    from pymongo.connection import Connection
    import gridfs
except ImportError:
    Connection = None


### Will be populated by the UI with it's own value
app = None

### TODO make this configurable START
mongo_host = "localhost"
mongo_port = 27017
### TODO make this configurable END


def getdb(dbname):
    con = None
    db = None

    try:
        con = Connection(mongo_host,mongo_port)
    except:
        return (  
            "Error : Unable to create mongo connection %s:%s" % (mongo_host,mongo_port),
            None
        )

    try:
        db = con[dbname]
    except:
        return (  
            "Error : Unable to connect to mongo database %s" % dbname,
            None
        )

    return (  
        "Connected to mongo database %s" % dbname,
        db
    )



def system_page():
    user = app.get_user_auth()

    if not user:
        app.bottle.redirect("/user/login")

    schedulers = app.datamgr.get_schedulers()
    brokers = app.datamgr.get_brokers()
    reactionners = app.datamgr.get_reactionners()
    receivers = app.datamgr.get_receivers()
    pollers = app.datamgr.get_pollers()

    return {'app': app, 'user': user, 'schedulers': schedulers,
            'brokers': brokers, 'reactionners': reactionners,
            'receivers': receivers, 'pollers': pollers,
            }


def system_widget():
    user = app.get_user_auth()

    if not user:
        app.bottle.redirect("/user/login")

    schedulers = app.datamgr.get_schedulers()
    brokers = app.datamgr.get_brokers()
    reactionners = app.datamgr.get_reactionners()
    receivers = app.datamgr.get_receivers()
    pollers = app.datamgr.get_pollers()

    wid = app.request.GET.get('wid', 'widget_system_' + str(int(time.time())))
    collapsed = (app.request.GET.get('collapsed', 'False') == 'True')
    print "SYSTEM COLLAPSED?", collapsed, type(collapsed)

    got_childs = (app.request.GET.get('got_childs', 'False') == 'True')
    key = app.request.GET.get('key', 1)

    options = {}

    return {'app': app, 'user': user, 'wid': wid,
            'collapsed': collapsed, 'options': options,
            'base_url': '/widget/system', 'title': 'System Information',
            'schedulers': schedulers,
            'brokers': brokers, 'reactionners': reactionners,
            'receivers': receivers, 'pollers': pollers,
            }


def show_log():
    user = app.get_user_auth()

    if not user:
        app.bottle.redirect("/user/login")

    message,db = getdb('logs')
    if not db:
        return {
            'app': app,
            'user': user, 
            'message': message,
            'records': []
        }

    records=[]
    for feature in db.logs.find({'type': 'HOST NOTIFICATION' }).sort("time",1).limit(100):
        date = feature["time"]

        records.append({
            "date" : int(date),
            "host" : feature['host_name'],
            "service" : feature['service_description'],
            "message" : feature['message']
        })

    return {
        'app': app,
        'user': user, 
        'message': 'Data fetched from DB ...',
        'records': records
    }


widget_desc = '''<h4>System state</h4>
Show an aggregated view of all Shinken daemons.
'''

pages = {system_page: {'routes': ['/system', '/system/'], 'view': 'system', 'static': True},
         system_widget: {'routes': ['/widget/system'], 'view': 'system_widget', 'static': True, 'widget': ['dashboard'], 'widget_desc': widget_desc, 'widget_name': 'system', 'widget_picture': '/static/system/img/widget_system.png'},
         show_log: {'routes': ['/system/logs'], 'view': 'log', 'static': True},
         }

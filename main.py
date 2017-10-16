from google.appengine.ext import ndb
import webapp2
import json
import logging
'''
Assignment: REST Planning and Implementation
Author: Samuel Hudson
Course: CS496
Date: 10/15/17
'''
class Boat(ndb.Model):
    id = ndb.StringProperty()
    name = ndb.StringProperty()
    type = ndb.StringProperty()
    length = ndb.IntegerProperty()
    at_sea = ndb.BooleanProperty()

class Slip(ndb.Model):
    id = ndb.StringProperty()
    number = ndb.IntegerProperty()
    current_boat = ndb.StringProperty()
    arrival_date = ndb.StringProperty()
    departure_history = ndb.JsonProperty()

class BoatHandler(webapp2.RequestHandler):
    def post(self):
        boat_data = json.loads(self.request.body)
        new_boat = Boat(name=boat_data['name'], type=boat_data['type'],
                        length=boat_data['length'],at_sea=True)
        new_boat.put()
        new_boat.id = new_boat.key.urlsafe()
        new_boat.put()
        boat_dict = new_boat.to_dict()
        boat_dict['_self'] = "/boat/"+new_boat.key.urlsafe()
        self.response.write(json.dumps(boat_dict))
    def get(self, id=None):
        #returning boat entity by identifier
        if id:
            b = ndb.Key(urlsafe=id).get()
            b_d = b.to_dict()
            b_d['self'] = "/boat" + id
            self.response.write(json.dumps(b.to_dict()))
        else:
            #returning all boat entities
            self.response.write(json.dumps([b.to_dict() 
                                            for b in Boat.query().fetch()]))
    def delete(self, id=None):
        if id:
            b = ndb.Key(urlsafe=id).get()
            #extra credit would need to handle update to all departures
            if not b.at_sea and len(Slip.query(Slip.current_boat == b.id).get())> 0:
                s = Slip.query(Slip.current_boat == b.id).get()
                s.arrival_date = None
                s.current_boat = None
                s.put()
            b.key.delete()
            self.response.write("Boat "+id+" deleted")
    def patch(self, id=None):
        if id:
            b = ndb.Key(urlsafe=id).get()
            boat_data = json.loads(self.request.body)
            #managing departure
            if not b.at_sea:
                if boat_data['at_sea']:
                    s = Slip.query(Slip.current_boat == b.id).get()
                    s.arrival_date = None
                    s.current_boat = None
                    # for extra credit s.departure_history
                    s.put()
            for key in boat_data:
                setattr(b, key, boat_data[key])
            b.put()
    def put(self, id=None):
        if id:
            b = ndb.Key(urlsafe=id).get()
            boat_data = json.loads(self.request.body)
            #managing departure
            if not b.at_sea:
                if boat_data['at_sea']:
                    s = Slip.query(Slip.current_boat == b.id).get()
                    s.arrival_date = None
                    s.current_boat = None
                    # for extra credit s.departure_history
                    s.put()
            for key in boat_data:
                setattr(b, key, boat_data[key])
            b.put()
class SlipHandler(webapp2.RequestHandler):
    def post(self):
        slip_data = json.loads(self.request.body)
        new_slip = Slip(number=slip_data['number'])
        new_slip.put()
        new_slip.id = new_slip.key.urlsafe()
        new_slip.put()
        slip_dict = new_slip.to_dict()
        slip_dict['self'] = '/slip/' + new_slip.key.urlsafe()
        self.response.write(json.dumps(slip_dict))
    def get(self, id=None):
        if id:
            s = ndb.Key(urlsafe=id).get()
            s_d = s.to_dict()
            s_d['self'] = "/slip" + id
            self.response.write(json.dumps(s.to_dict()))
        else:
            #returning all slip entities
            self.response.write(json.dumps([s.to_dict() 
                                            for s in Slip.query().fetch()]))
    def delete(self, id=None):
        if id:
            s = ndb.Key(urlsafe=id).get()
            #checking if boat needs updating to at sea
            if s.current_boat:
                b = Boat.query(Boat.id == s.current_boat).get()
                b.at_sea = True
                b.put()
            s.key.delete()
            self.response.write("Slip "+id+" deleted")
    def patch(self, id=None):
        if id:
            s = ndb.Key(urlsafe=id).get()
            slip_data = json.loads(self.request.body)
            #managing arrival
            if not s.current_boat:
                b = ndb.Key(urlsafe=slip_data['current_boat']).get()
                b.at_sea = False
                b.put()
            else:
                #returning 403
                self.response.write("Error: 403 Forbidden message")
                self.response.set_status(403)

            for key in slip_data:
                setattr(s, key, slip_data[key])
            s.put()
    def put(self, id=None):
        if id:
            s = ndb.Key(urlsafe=id).get()
            slip_data = json.loads(self.request.body)
            for key in slip_data:
                setattr(s, key, slip_data[key])
            s.put()
class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write("REST Planning and Implementation by Sam Hudson")
allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods
    
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/slip', SlipHandler),
    ('/slip/(.*)', SlipHandler),    
    ('/boat', BoatHandler),
    ('/boat/(.*)', BoatHandler)
], debug=True)
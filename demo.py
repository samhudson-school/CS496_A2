from google.appengine.ext import ndb
import webapp2

class MainPage(webapp2.RequestHandler):

    def get(self):
        self.response.write("Hello World!")
allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods
    
app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
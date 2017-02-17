#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape= True)



class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Post(db.Model):
    title = db.StringProperty(required = True)
    txt = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

    def render(self):
        self.render_text = self.content.replace('\n', '<br>')
        return render_str("base.html", p = self)

class MainPage(Handler):
    def get(self):

        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5")

        self.render("base.html", posts=posts, heading = "My Blogs")


class NewPost(Handler):
    def render_front(self, title ="", txt="", error=""):
        posts = db.GqlQuery("SELECT * FROM Post "
                            "ORDER BY created DESC "

                               )
        self.render("newpost.html", title=title, txt=txt, error=error, posts=posts,heading="New Post")

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        txt = self.request.get("txt")

        if title and txt:
            # creates new instance of Post
            post = Post(title = title, txt = txt)
            #puts new instance in database
            post.put()
            self.render_front()
            post_id = str(post.key().id())
            self.redirect("/blog/"+post_id)
        else:
            error = "Must enter title and text"
            self.render_front(title, txt, error)

class ViewPostHandler(Handler):
    def get(self, id):
        post_id = Post.get_by_id(int(id))
        if not post_id:
            error = "Sorry, we couldn't find what you were looking for"
            self.redirect("/blog?error="+ error)
        self.render("viewpost.html", post_id = post_id)


app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    # ('/blog?page=')
    ('/blog/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)

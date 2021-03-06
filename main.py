from lib import bottle
from lib.bottle import route, template, request, error, debug, static_file
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.app_identity import get_default_version_hostname
import lib.db
from lib.html import addLineBreaks
from google.appengine.api import users
import datetime
import logging

today=datetime.datetime.today
class Object():
    pass

@route('/')
def index():
    if not users.is_current_user_admin():
        q = lib.db.q("SELECT * FROM Page WHERE published = True ORDER BY timestamp DESC")
        #q = lib.db.Page.all()
        result = [[p.url, p.title] for p in q.run()]
        output = template('templates/index', rows=result, users=users)
    else:
        #result = lib.db.q("SELECT * FROM Page")
        q = lib.db.Page.all()
        q.order('-timestamp')
        todo = lib.db.Todo.all()
        result = [[p.url, p.title, p.published] for p in q.run()]
        output = template('templates/admin', rows=result, users=users, todo=todo)
    return output


@route('/show/:name')
def show(name):
    if not users.is_current_user_admin():
        pass
    q = lib.db.Page.gql("WHERE url = :1", name)
    p = q.get()
    if not p:
        p = Object()
        p.title = "Unknown Page"
        p.content = "This page does not exist."
    title = p.title
    content = addLineBreaks(p.content)
    return template('templates/show_page.tpl', title=title, body=content)
    #content = convertList(lst)

@route('/view/:name')
def view(name):
    q = lib.db.Page.gql("WHERE url = :1", name)
    p = q.get()
    if not p:
        p = Object()
        p.title = "Unknown Page"
        p.content = "This page does not exist."
    title = p.title
    content = addLineBreaks(p.content)
    return template('templates/view_page.tpl', title=title, body=content)
    #content = convertList(lst)

@route('/new', method='GET')
def new():
    return template('templates/new_preview.tpl')

@route('/new', method='POST')
def new_post():
    if request.POST.get('save','').strip():
        title = request.POST.get('title', '').strip()
        data = request.POST.get('data', '').strip()
        url = lib.db.getUrlString()
        lib.db.Page(title=title, content=data, url=url, published=False, timestamp=today()).put()

        message =  '<p>The new page was inserted into the database, \
            the ID is %s</p>' % (url)

        return template('templates/submit.tpl', body=message, 
            data=addLineBreaks(data), title=title, url=url)
    elif request.POST.get('publish','').strip():
        title = request.POST.get('title', '').strip()
        data = request.POST.get('data', '').strip()
        url = lib.db.getUrlString()
        lib.db.Page(title=title, content=data, url=url, published=True, timestamp=today()).put()

        message =  '<p>The new page was inserted into the database, \
            the ID is %s</p>' % (url)

        return template('templates/submit.tpl', body=message, 
            data=addLineBreaks(data), title=title, url=url)

@route('/todo', method='GET')
def new():
    body = '''
<p>Add a new task to the ToDo list:</p>
<form action="/todo" method="POST">
Title: <br>
<input type="text" name="title"><br>
Body: <br>
<textarea name="data" cols="80" rows="20">
</textarea>
<br />
<input type="submit" name="save" value="save">
</form>
    '''
    return template('templates/simple.tpl', body=body)

@route('/todo', method='POST')
def new_post():
    if request.POST.get('save','').strip():
        title = request.POST.get('title', '').strip()
        data = request.POST.get('data', '').strip()
        lib.db.Todo(title=title, content=data, open=True).put()

        message =  '<p>The new task was inserted into the database</p>'

        return template('templates/simple.tpl', body=message)


@route('/edit/:name', method='GET')
def edit(name):
    q = lib.db.Page.gql("WHERE url = :1", name)
    p = q.get()
    if not p:
        p = Object()
        p.title = ""
        p.content = ""
    title = p.title
    content = p.content
    #lib.db.d(p)
    return template('templates/edit_preview.tpl', name=name, body=content, url=name, title=title, data=addLineBreaks(content))

#@route('/edit_old/:name', method='GET')
#def edit(name):
#    q = lib.db.Page.gql("WHERE url = :1", name)
#    p = q.get()
#    title = p.title
#    content = p.content
#    return template('templates/edit_active.tpl', name=name, body=content, url=name, title=title)

@route('/edit/:name', method='POST')
def edit_post(name):
    if request.POST.get('save','').strip():
        title = request.POST.get('title', '').strip()
        data = request.POST.get('data', '').strip()
        url = request.POST.get('url', '').strip()

        q = lib.db.Page.gql("WHERE url = :1", name)
        p = q.get()
        lib.db.d(p)

        if url == name:
            message = '<p>The ID %s was successfully updated</p>' % (url)
            #lib.db.q('UPDATE Page SET url = ?, data = ? WHERE url = :1', url)
        else:
            message =  '<p>The new task was inserted into the database, the ID is %s</p>' % (url)
            #lib.db.Page(title=title, content=data, url=url).put()

        lib.db.Page(title=title, content=data, url=url, published=False, timestamp=today()).put()

        return template('templates/submit.tpl', body=message, 
            data=addLineBreaks(data), title=title, url=url)
    elif request.POST.get('publish','').strip():
        title = request.POST.get('title', '').strip()
        data = request.POST.get('data', '').strip()
        url = request.POST.get('url', '').strip()

        q = lib.db.Page.gql("WHERE url = :1", name)
        p = q.get()
        lib.db.d(p)

        if url == name:
            message = '<p>The ID %s was successfully updated</p>' % (url)
            #lib.db.q('UPDATE Page SET url = ?, data = ? WHERE url = :1', url)
        else:
            message =  '<p>The new task was inserted into the database, the ID is %s</p>' % (url)
            #lib.db.Page(title=title, content=data, url=url).put()

        lib.db.Page(title=title, content=data, url=url, published=True, timestamp=today()).put()

        return template('templates/submit.tpl', body=message, 
            data=addLineBreaks(data), title=title, url=url)

@route('/help')
def help():
    static_file('help.html', root='.')

@route('/static/<filename>')
def static(filename):
    return static_file(filename, root='static')

@route('/json:json#[1-9]+#')
def show_json(json):

    conn = sqlite3.connect('math.db')
    c = conn.cursor()
    c.execute("SELECT data FROM paste WHERE id LIKE ?", (json))
    result = c.fetchall()
    c.close()

    if not result:
        return {'task':'This item number does not exist!'}
    else:
        return {'Task': result[0]}
 
def main():
    #Find a way to check if dev server.
    if get_default_version_hostname() == 'localhost:8080':
        debug(True)
    else:
        @error(500)
        def Error500(code):
            logging.error('There was an internal server error')
            message = 'Internal Server Error'
            return template('templates/simple.tpl', body=message)
         

    
    run_wsgi_app(bottle.default_app())
 
@error(403)
def Error403(code):
    logging.warning('There was a 403')
    message = 'Get your codes right dude, you caused some error!'
    return template('templates/simple.tpl', body=message)
 
@error(404)
def Error404(code):
    logging.warning('There was a 404')
    message = 'Stop cowboy, what are you trying to find?'
    return template('templates/simple.tpl', body=message)
 
if __name__=="__main__":
    main()
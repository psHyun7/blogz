from flask import request, redirect, render_template, session, flash
from app import app, db
from models import Blog, User
from hashutils import check_pw_hash
import cgi


#Routes
@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'static']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

#Automatically Redirect to /blog
@app.route('/')
def main_page():
    return render_template('index.html')

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    #Check for Blank Title or Body
    if request.method == 'POST':
        error = False
        title = request.form['post_title']
        body = request.form['post_body']
        if not title:
            flash("Please fill in the title", "title_error")
            error = True
        if not body:
            flash("Please fill in the body", "body_error")
            error = True
        if error:
            #redirect using POST method to preserve title or body
            return redirect ('/new-post', code=307)
        #Create new entry to database
        new_post = Blog(title, body)
        db.session.add(new_post)
        db.session.commit()
        new_post = Blog.query.order_by(Blog.id.desc()).first()
        new_id = new_post.id
        new_url = "/blog?id=" + str(new_id)
        return redirect(new_url)
    #Check for Post # or Show all post.
    post_num = request.args.get("id")
    if post_num:
        posts = Blog.query.filter_by(id=post_num).all()
        for post in posts:
            title_page = post.title
        return render_template('blog.html', title=title_page, posts=posts, title_page=title_page, post_num=post_num)
    else:
        posts = Blog.query.order_by(Blog.id.desc()).all()
    return render_template('blog.html', title='Build A Blog', posts=posts, title_page="Build A Blog", post_num=post_num)

@app.route('/new-post', methods=['POST', 'GET'])
def add_post():
    if request.method == 'POST':
        title = request.form['post_title']
        body = request.form['post_body']
        return render_template('new-post.html', title="Add Blog Entry", title_value=title, body_value=body)
    else:
        return render_template('new-post.html', title="Add Blog Entry")

@app.route('/signup')
def signup():
    #correct signup = redirect to /new-post with new username stored in session
    #any field is blank / invalid = return to /signup with error message/s
    #username already exists = return to /signup with error message (user already exists)
    #password + verify password
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    #correct login = redirect to /new-post
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['email'] = email
            flash("Logged in")
            return redirect('/')
    #incorrect password = return to /login with error message (incorrect password)
    #username not in database = return to /login with error message (username does not exist)
    #user clicks register = redirect to /signup
    flash("error")
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    #delete user from session
    return redirect('/blog')

@app.route('/index')
def index():
    return render_template('index.html')


if __name__=='__main__':
    app.run()
from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy
import hashlib, random, string


#Setup
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:MyPassword@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'B6*c12eNojsv#PG5'


#Create Classes
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    pw_hash = db.Column(db.String(30))
    posts = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)


#Functions
def make_pw_hash(password, salt=None):
    if not salt:
        salt = make_salt
    hash = hashlib.sha256(str.encode(password + salt)).hexdigest()
    return '{0},{1}'.format(hash,salt)

def make_salt():
    return ''.join([random.choice(string.ascii_letters) for x in range(5)])

def check_pw_hash(password, hash):
    sale = hash.split(',')[1]
    if make_pw_hash(password, salt) == hash:
        return True
    return False


#Routes
@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'static']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

#Automatically Redirect to /blog
@app.route('/')
def main_redirect():
    return redirect('/blog')

@app.route('/blog', methods=['POST', 'GET'])
def index():
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
    return None



@app.route('/login')
def signup():
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
    return None

@app.route('/logout', methods=['POST'])
def logout():
    #delete user from session
    return redirect('/blog')

@app.route('/index')
def index():
    return None


if __name__=='__main__':
    app.run()
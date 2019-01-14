from flask import request, redirect, render_template, session, flash
from app import app, db
from models import Blog, User
from hashutils import check_pw_hash
import cgi


#Allowed Routes with Auto Redirect
@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'list_blogs', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        flash("You must first Log In", "main_flash")
        return redirect('/login')

#Automatically Redirect to /blog
@app.route('/')
def index():
    userlist = User.query.order_by(User.username).all()
    return render_template('index.html', users=userlist)

@app.route('/blog', methods=['POST', 'GET'])
def list_blogs():
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
        #Create new entry to database with user id
        owner = User.query.filter_by(username=session['username']).first()
        new_post = Blog(title, body, owner)
        db.session.add(new_post)
        db.session.commit()
        new_url = "/blog?id=" + str(new_post.id)
        return redirect(new_url)
    #Check for Post # or Show all post.
    post_num = request.args.get("id")
    user = request.args.get("user")
    if request.args.get("page"):
        page_num = int(request.args.get("page"))
    else:
        page_num = 1
    if post_num:
        post = Blog.query.get(post_num)
        title_page = post.title
        return render_template('blog.html', title=title_page, post=post, title_page=title_page, post_num=post_num)
    elif user:
        owner = User.query.filter_by(id=user).first()
        posts = Blog.query.filter_by(owner=owner).order_by(Blog.id.desc()).paginate(per_page=5, page=page_num, error_out=False)
        title_page = "All Posts by " + owner.username
    else:
        posts = Blog.query.order_by(Blog.id.desc()).paginate(per_page=5, page=page_num, error_out=False)
        title_page = "All Posts"
    return render_template('blog.html', title='Blogz', posts=posts, title_page=title_page, post_num=post_num, user=user)

@app.route('/new-post', methods=['POST', 'GET'])
def add_post():
    if request.method == 'POST':
        title = request.form['post_title']
        body = request.form['post_body']
        return render_template('new-post.html', title="Add Blog Entry", title_value=title, body_value=body)
    else:
        return render_template('new-post.html', title="Add Blog Entry")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    no_spec_char = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    
    if request.method == 'GET':
        return render_template('signup.html')

    if request.method == 'POST':

        #Set Variables
        username = request.form['username_name']
        password = request.form['password_name']
        v_password = request.form['v_password_name']
        username_error = False
        password_error = False
        v_password_error = False

        #Error Messages and Conditions
        if username:
            for char in username:
                if char not in no_spec_char:
                    username_error = True
                    flash("Not Valid: Use Only Alphabet and Numbers.", "username_error")
            if len(username) < 3 or len(username) > 20:
                username_error = True
                flash("Username must be between 3-20 characters.", "username_error")
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                username_error = True
                flash("Username is already in use", "username_error")
        else:
            username_error = True
            flash("Username field is Blank.", "username_error")

        if not password:
            password_error = True
            flash("Password field is Blank.", "password_error")
            if len(password) > 16:
                password_error = True
                flash("Not Valid: Password between the length of 1-16.", "password_error")
            elif " " in password:
                password_error = True
                flash("Not Valid: Do not use space in Password.", "password_error")
        
        if not v_password:
            v_password_error = True
            flash("Verify Password field is Blank", "v_password_error")    
            if " " in v_password:
                v_password_error = True
                flash("Not Valid: Do not use space in Password.", "v_password_error")
        
        if password and v_password and v_password != password:
            v_password_error = True
            flash("The Passwords do not match.", "v_password_error")

        #Successful Entry with No Error    
        if not username_error and not password_error and not v_password_error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/new-post')

    return render_template('signup.html', username_value=username)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form["username_name"]
        password = request.form["password_name"]
        if username and not password:
            flash("Password field is blank", "password_error")
        elif username and password:
            user = User.query.filter_by(username=username).first()
            if user and check_pw_hash(password, user.pw_hash):
                session['username'] = username
                flash("Logged in", "main_flash")
                return redirect('/new-post')
            elif user:
                flash("Password is incorrect", "password_error")
            else:
                flash("Username does not exist", "username_error")
        elif not username:
            flash("Username field is blank", "username_error")
            if not password:
                flash("Password field is blank", "password_error")

        return render_template('login.html', username_value=username)
    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['username']
    flash("Logged Out", "main_flash")
    return redirect('/blog')

if __name__=='__main__':
    app.run()
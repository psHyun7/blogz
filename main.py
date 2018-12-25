from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy

#Setup
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'zGLM6z7w*65NhR4$'

#Create Blog Class
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)

    def __init__(self, title, body):
        self.title = title
        self.body = body

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

if __name__=='__main__':
    app.run()
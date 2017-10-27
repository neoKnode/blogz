from flask import Flask, request, render_template, redirect, send_from_directory,flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


####################################
#          Blog Database           #
####################################
class Blogs(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blogtitle = db.Column(db.String(30))
    blogtext = db.Column(db.String(500))
    completed = db.Column(db.Boolean)

    def __init__(self, blogtitle, blogtext):
        self.blogtitle = blogtitle
        self.blogtext = blogtext
        self.completed = False


####################################
#          User Database           #
####################################
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))

    def __init__(self, email, password):
        self.email = email
        self.password = password


####################################
#             Register             #
####################################
@app.route('/register', methods=['POST', 'GET'])
def register():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's data

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            # TODO - "Remember" the user 
            return redirect('/blog')
        else:
            # TODO - user better response messaging
            return '<h1>Duplicate users</h1>'
    return render_template('signup.html')




####################################
#              Login               #
####################################
@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
            # TODO - Validate the user
        if user and user.password == password:
            # TODO - "REMEMBER" THAT THE USER HAS LOGGED IN
            return redirect('/blog')
        else: 
            # TODO - explain why login failed
            return '<h1>Error!</h1>'
    return render_template('login.html')


####################################
#              Logout              #
####################################
#@app.route('/logout')
#def logout():
#    return render_template('blog.html')


####################################
#              Index               #
####################################
#@app.route('/index')
#def index():
#    return render_template('home.html')


####################################
#              Styles              #
####################################
@app.route('/styles.css')
def styles():
    return send_from_directory(os.path.join(app.root_path,'static/css'),'styles.css')


####################################
#           Post list              #
####################################
@app.route('/blog', methods=['POST', 'GET'])
def blog_list():

    blogged = Blogs.query.filter_by(completed=False).all()
    deleted_blogs = Blogs.query.filter_by(completed=True).all()

    return render_template('blog.html', title='Build a Blog', 
            blogged=blogged, deleted_blogs=deleted_blogs)


####################################
#            Add a post            #
####################################
@app.route('/newpost', methods=['POST', 'GET'])
def add_blog():

    return render_template('newpost.html', title='Create Blog')


####################################
#           Delete post            #
####################################
@app.route('/delete-blog', methods=['GET','POST'])
def delete_blog():

    blog_id = int(request.form['blog-id'])
    blog = Blogs.query.get(blog_id)
    blog.completed = True
    db.session.add(blog)
    db.session.commit()

    blogged = Blogs.query.filter_by(completed=False).all()
    deleted_blogs = Blogs.query.filter_by(completed=True).all()

    return render_template('blog.html', title='Build a Blog', 
            blogged=blogged, deleted_blogs=deleted_blogs)
    

####################################
#          Validate post           #
####################################
@app.route('/validate-blog', methods=['POST'])
def valid_blog():

    title_error = ''
    blog_error = ''

    if request.method == 'POST':
        title_of_blog = request.form['blogtitle']
        body_of_blog = request.form['blogtext']
        new_entry = Blogs(title_of_blog,body_of_blog)

    if title_of_blog == '':
        title_error = 'Please enter a title'

    if body_of_blog == '':
        blog_error = 'Please write some words'

    if not title_error and not blog_error:
        db.session.add(new_entry)
        db.session.commit()
        last_entry = Blogs.query.order_by('-id').first()
        id = str(last_entry.id)
        return redirect('/page?id=' + id)
    else:
        return render_template('/newpost.html', title='Create Blog', 
            title_of_blog=title_of_blog, body_of_blog=body_of_blog, 
            title_error=title_error, blog_error=blog_error)


####################################
#          View a Post             #
####################################
@app.route('/page')
def new_post_page():

    if request.args:
        id = request.args.get('id')
        new_entry = Blogs.query.filter_by(id=id).first()
        new_title = new_entry.blogtitle
        new_body = new_entry.blogtext
    return render_template('post.html', title="Blog Entry", new_title=new_title, new_body=new_body)



if __name__ == '__main__':
    app.run()

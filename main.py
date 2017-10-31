from flask import Flask, request, render_template, redirect, send_from_directory, flash, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zPQB'


####################################
#              Styles              #
####################################
@app.route('/styles.css')
def styles():
    return send_from_directory(os.path.join(app.root_path,'static/css'),'styles.css')


####################################
#          Blog Database           #
####################################
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blogtitle = db.Column(db.String(50))
    blogtext = db.Column(db.String(1000))
    completed = db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, blogtitle, blogtext, owner):
        self.blogtitle = blogtitle
        self.blogtext = blogtext
        self.completed = False
        self.owner = owner


####################################
#          User Database           #
####################################
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(30))
    blogs = db.relationship('Blog', backref='owner')


    def __init__(self, username, password):
        self.username = username
        self.password = password



####################################
#          Before_Request          #
####################################
@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'index', 'blog_list']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('login')


####################################
#              Login               #
####################################
@app.route('/login', methods=['POST', 'GET'])
def login():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_error = ''
        username_error = ''
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            username_error = 'Username does not exist'
        if username == '':
            username_error = 'Please enter username'
        if existing_user and existing_user.password != password:
            password_error = 'Incorrect password'
        if existing_user and existing_user.password == password:
            session['username'] = username
            flash('Logged in!')
            return redirect('/newpost')
        else:
            return render_template('login.html', 
                password_error=password_error, 
                username_error=username_error,
                username=username
                )
    return render_template('login.html')


####################################
#             Register             #
####################################
@app.route('/register', methods=['POST', 'GET'])
def register():

    if request.method == 'POST':
        password = request.form['password']
        verify_password = request.form['verify']
        username = request.form['username']

    ########################
    #  validate user data  #
    ########################
        password_error = ''
        verify_error = ''
        username_error = ''

        if len(username) < 3 or len(username) > 20 or ' ' in username:
            username_error = 'Username too short/long'
        
        if len(password) < 3 or len(password) > 120 or ' ' in password:
            password_error = 'Password too short/long'

        if verify_password == '':
            verify_error = 'Please retype your password'

        if password != verify_password:
            verify_error = 'Passwords do not match!'

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            username_error = 'Username already exists'

        if not existing_user and not username_error and not verify_error and not password_error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            return render_template('signup.html', 
                password_error=password_error, 
                verify_error=verify_error, 
                username_error=username_error,
                username=username
                )
    return render_template('signup.html')


####################################
#              Logout              #
####################################
@app.route('/logout') #, methods=['POST', 'GET'])?
def logout():
    del session['username']
    return redirect('/blog')


####################################
#              Index               #
####################################
@app.route("/") #, methods=['POST', 'GET'])?
def index():
    users = User.query.all()
    return render_template('index.html', users=users)


####################################
#           Post list              #
####################################
@app.route('/blog')
def blog_list():
    
    blogged = Blog.query.filter_by(completed=False).all()

    return render_template('blog.html', 
        title='Build a Blog',
        blogged=blogged, 
        )


####################################
#            Add a post            #
####################################
@app.route('/newpost', methods=['POST', 'GET'])
def add_blog():

    owner = User.query.filter_by(username=session['username']).first()
    title_error = ''
    blog_error = ''

    if request.method == 'POST':
        title_of_blog = request.form['blogtitle']
        body_of_blog = request.form['blogtext']
        new_entry = Blog(title_of_blog,body_of_blog, owner)

        if title_of_blog == '':
            title_error = 'Please enter a title'

        if body_of_blog == '':
            blog_error = 'Please write some words'

        if not title_error and not blog_error:
            db.session.add(new_entry)
            db.session.commit()
            last_entry = Blog.query.order_by('-id').first()
            id = str(last_entry.id)
            return redirect('/page?id=' + id)
        else:
            return render_template('/newpost.html', 
                title='Create Blog',
                title_of_blog=title_of_blog, 
                body_of_blog=body_of_blog, 
                title_error=title_error, 
                blog_error=blog_error
                )

    return render_template('newpost.html', title='Create Blog')


####################################
#           Delete post            #
####################################
@app.route('/delete-blog', methods=['GET','POST'])
def delete_blog():

    blog_id = int(request.form['blog-id'])
    blog = Blog.query.get(blog_id)
    blog.completed = True
    db.session.add(blog)
    db.session.commit()

    return redirect('/blog')
    

####################################
#          View a Post             #
####################################
@app.route('/page')
def new_post_page():

    if request.args:
        id = request.args.get('id')
        new_entry = Blog.query.filter_by(id=id).first()
        new_title = new_entry.blogtitle
        new_body = new_entry.blogtext
    return render_template('post.html', 
        title="Blog Entry", 
        new_title=new_title, 
        new_body=new_body
    )

####################################
#         Single User Posts        #
####################################
@app.route('/user')
def user_posts():


    if request.args:
        id = request.args.get('user')

        blogged = Blog.query.filter_by(owner_id=id, completed=False).all()


    return render_template('singleUser.html', 
        title='User Blogs',
        blogged=blogged, 
        )



if __name__ == '__main__':
    app.run()
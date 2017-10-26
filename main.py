from flask import Flask, request, render_template, redirect, send_from_directory,flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


####################################
#            Database              #
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
#              Styles              #
####################################
@app.route('/styles.css')
def styles():
    return send_from_directory(os.path.join(app.root_path,'static/css'),'styles.css')


####################################
#           Blog list              #
####################################
@app.route('/', methods=['POST', 'GET'])
def index():

    blogged = Blogs.query.filter_by(completed=False).all()
    deleted_blogs = Blogs.query.filter_by(completed=True).all()

    return render_template('blog.html', title='Build a Blog', 
            blogged=blogged, deleted_blogs=deleted_blogs)


####################################
#            Add a blog            #
####################################
@app.route('/newpost', methods=['POST', 'GET'])
def add_blog():

    return render_template('newpost.html', title='Create Blog')


####################################
#           Delete blog            #
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
#          Validate blog           #
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
        return redirect('/page?id={0}'.format(new_entry))
    else:
        return render_template('/newpost.html', title='Create Blog', 
            title_of_blog=title_of_blog, body_of_blog=body_of_blog, 
            title_error=title_error, blog_error=blog_error)


####################################
#             New Post             #
####################################
@app.route('/page?id=')
def new_post_page():
    
    blog_id = int(request.form['blog-id'])
    blog = Blogs.query.get(blog_id)

    blogpost = Blogs.query.filter_by(id={blog_id}).max(blog_id)

    return render_template('/post.html')


if __name__ == '__main__':
    app.run()

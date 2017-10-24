from flask import Flask, request, render_template, redirect, send_from_directory
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

    tasks = Blogs.query.filter_by(completed=False).all()
    completed_tasks = Blogs.query.filter_by(completed=True).all()

    return render_template('blog.html', title='Build a Blog', 
            tasks=tasks, completed_tasks=completed_tasks)


####################################
#           Delete blog            #
####################################
@app.route('/delete-task', methods=['GET','POST'])
def delete_blog():

    task_id = int(request.form['task-id'])
    task = Blogs.query.get(task_id)
    task.completed = True
    db.session.add(task)
    db.session.commit()

    tasks = Blogs.query.filter_by(completed=False).all()
    completed_tasks = Blogs.query.filter_by(completed=True).all()

    return render_template('blog.html', title='Build a Blog', 
            tasks=tasks, completed_tasks=completed_tasks)
    

####################################
#            Add a blog            #
####################################
@app.route('/newpost', methods=['POST', 'GET'])
def add_blog():

    tasks = Blogs.query.filter_by(completed=False).all()
    completed_tasks = Blogs.query.filter_by(completed=True).all()
    title_error = ''
    blog_error = ''

    
    if request.method == 'POST':
        title_name = request.form['blogtitle']
        blogtext_name = request.form['blogtext']
        new_entry = Blogs(title_name,blogtext_name)
        db.session.add(new_entry)
        db.session.commit()
    
        if title_name == '':
            title_error = 'Please enter a title'

        if blogtext_name == '':
            blog_error = 'Please write some words'

    if not title_error and not blog_error:
        return render_template('/newpost.html', title='Build a Blog', 
            tasks=tasks, completed_tasks=completed_tasks)
    else:
        return render_template('/newpost.html', title='Create Blog', 
        tasks=tasks, completed_tasks=completed_tasks, title_error=title_error, 
        blog_error=blog_error)



if __name__ == '__main__':
    app.run()


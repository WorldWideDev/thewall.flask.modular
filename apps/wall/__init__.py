from flask import Flask, render_template, redirect, flash, request as req, session, Blueprint
from mysqlconnection import MySQLConnector

app = Flask(__name__)
mysql = MySQLConnector(app, 'the_wall')

wall = Blueprint('wall', __name__, template_folder='../templates', static_folder='static')

# def format_datetime(value, format='medium'):
#     if format == 'full':
#         format="EEEE, d. MMMM y 'at' HH:mm"
#     elif format == 'medium':
#         format="EE dd.MM.y HH:mm"
#     return babel.dates.format_datetime(value, format)
#
# jinja_env.filters['datetime'] = format_datetime


def getPostsWithUsers():
    post_query = "SELECT posts.*, users.first_name, users.last_name FROM posts \
                  LEFT JOIN users ON users.id = posts.user_id"
    posts = mysql.query_db(post_query)
    return posts

def getComments():
    comment_query = "SELECT comments.*, users.first_name, users.last_name FROM comments \
                    LEFT JOIN users ON users.id = comments.user_id \
                    LEFT JOIN posts ON posts.id = comments.post_id"
    comments = mysql.query_db(comment_query)
    return comments

def getPostsWithComments():
    comments = getComments()
    posts = getPostsWithUsers()
    commentList = {}
    postsWithComment = []

    for comment in comments:
        commentData = {
            "post_id": comment['post_id'],
            "created_at": comment['created_at'],
            "first_name": comment['first_name'],
            "last_name": comment['last_name'],
            "comment_text": comment['comment_text']
        }
        if comment['post_id'] in commentList:
            commentList[comment['post_id']].append(commentData)
        else:
            commentList[comment['post_id']] = [commentData]
    print commentList, 'is commentList'

    print posts, 'in getPostsWithComments'
    for post in posts:
        postData = {
            "created_at": post['created_at'].strftime('%Y-%m-%d %I:%M%p'),
            "post_id": post['id'],
            "first_name": post['first_name'],
            "last_name": post['last_name'],
            "post_text": post['post_text']
        }

        if post['id'] in commentList:
            postData['comments'] = commentList[post['id']]
        postsWithComment.append(postData)
        
    return postsWithComment


@wall.route('/wall')
def index():

    posts = getPostsWithComments()
    return render_template('wall.html', posts=posts)



@wall.route('/wall/post', methods=['POST'])
def createPost():
    query = "INSERT INTO posts (post_text, user_id, created_at, updated_at) \
            VALUES (:post_text, :id, NOW(), NOW())"
    data = {
        'post_text': req.form['content'],
        'id': session['id']
    }
    newPost = mysql.query_db(query, data)
    return redirect('/wall')

@wall.route('/wall/comment', methods=['POST'])
def createComment():
    query = "INSERT INTO comments (comment_text, user_id, post_id, created_at, updated_at) \
            VALUES (:comment_text, :user_id, :post_id, NOW(), NOW())"
    data = {
        'comment_text': req.form['content'],
        'user_id': session['id'],
        'post_id': req.form['post_id']
    }
    newPost = mysql.query_db(query, data)
    return redirect('/wall')

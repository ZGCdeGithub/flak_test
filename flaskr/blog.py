from flask import (Blueprint, flash, g, redirect, render_template, request, url_for)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db


bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()

    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET','POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        error = None

        if not title:
            error = '请输入帖子标题'
        elif not body:
            error = '请编辑帖子内容'
        
        if error is None:
            db = get_db()
            db.execute(
                'insert into post(title,body,author_id) values(?,?,?)',(title,body,g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))
        flash(error)
    else:
        return render_template('blog/create.html')


def get_post(id,check_author=True):
    post = get_db().execute(
        'select * from post where id=?',(id,)
    ).fetchone()
    if not post:
        abort(404,'id 为 {0} 的帖子不存在'.format(id))
    
    if check_author and post['author_id'] != g.user['id']:
        abort(403)
    return post


@bp.route('/update/<int:id>',methods=('GET','POST'))
def update(id):
    post = get_post(id)
    if not post:
        abort(404, 'id 为 {0} 的帖子不存在'.format(id))
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        error = None

        if not title:
            error = '请输入帖子标题'
        elif not body:
            error = '请编辑帖子内容'

        if error is None:
            db = get_db()
            db.execute(
                'update post set title=?,body=? where id=?',(title,body,id)
            )
            db.commit()
            return redirect(url_for('blog.index'))
        flash(error)
    else:
        return render_template('blog/update.html', post=post)


@bp.route('/delete/<int:id>',methods=('POST',))
def delete(id):
    post = get_post(id)
    if not post:
        abort(404, 'id 为 {0} 的帖子不存在'.format(id))
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))

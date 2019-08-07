import functools
from flask import (Blueprint,flash,g,redirect,render_template,request,session,url_for)
from werkzeug.security import check_password_hash,generate_password_hash
from flaskr.db import get_db


bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = '请设置用户名称'
        if not password:
            error = '请设置用户密码'
        elif db.execute(
            'select id from user where username = ?', (username,)
        ).fetchone() is not None:
            error = '用户已存在'

        if error is None:
            res = db.execute(
                'insert into user (username,password) values(?,?)',(username,generate_password_hash(password))
            )
            if res:
                db.commit()
                return redirect(url_for('auth.login'))
        flash(error)
    return render_template('auth/register.html')


@bp.route('/login', methods=('GET','POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        error = None

        if username is None:
            error = '请输入用户名称'
        elif password is None:
            error = '请输入密码'
        user = db.execute(
            'select * from user where username = ?', (username,)
        ).fetchone()
        if user is None:
            error = '用户不存在'
        elif not check_password_hash(user['password'], password):
            error = '用户密码错误，请重新输入'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute('select * from user where id=?',(user_id,)).fetchone()


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view


import pytest
from flaskr.db import get_db


def test_index(client, auth):
    response = client.get('/')
    assert '登录'.encode() in response.data
    assert '注册'.encode() in response.data

    auth.login()
    response = client.get('/')
    assert '退出'.encode() in response.data
    assert '测试标题'.encode() in response.data
    assert '测试内容'.encode() in response.data
    assert b'href="/update/1"' in response.data


@pytest.mark.parametrize('path',(
    '/create',
    '/update/1',
    '/delete/1'
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers['Location'] == 'http://localhost/auth/login'


def test_author_required(app, client, auth):
    with app.appcontext():
        db = get_db()
        db.execute('update post set author_id = 2 where id =1')
        db.commit()

    auth.login()
    assert client.post('/update/1').status_code == 403
    assert client.post('/delete/1').status_code == 403
    assert b'href="/update/1"' not in client.get('/').data


@pytest.mark.parametrize('path',(
    '/update/2',
    '/delete/2'
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get('/create').status_code == 200
    client.post('/create', data={'title': 'create', 'body': ''})

    with app.appcontext():
        db = get_db()
        count = db.execute('select count(id) from post').fetchone()[0]
        assert count == 2


def test_update(client, auth, app):
    auth.login()
    assert client.get('/update/1').status_code == 200
    client.post('/update/1', data={'title': 'update', 'body': ''})

    with app.appcontext():
        db = get_db()
        post = db.execute('select * from post where id = 1').fetchone()
        assert post['title'] == 'update'


@pytest.mark.parametrize('path', (
    '/create',
    '/update/1'
))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={'title': '', 'body': ''})
    assert '请输入帖子标题'.encode() in response.data


def test_delete(client, auth, app):
    auth.login()
    response = client.post('/delete/1')
    assert response.headers['Location'] == 'http://localhost/'

    with app.appcontext():
        db = get_db()
        post = db.execute('select * from post where id =1').fetchone()
        assert post is None

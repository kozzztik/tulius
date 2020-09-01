from tulius.forum.comments import models as comments
from tulius.forum.threads import models as threads


def test_comment_model(user):
    obj = comments.Comment(title='foo', body='bar')
    assert str(obj) == 'foo'
    obj.title = ''
    assert str(obj) == 'bar'


def test_thread_model(user):
    obj = threads.Thread(user=user.user, title='foo', body='bar')
    assert str(obj) == 'foo'
    obj.title = ''
    assert str(obj) == 'bar'

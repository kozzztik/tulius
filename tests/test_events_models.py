from tulius.events import models


def test_notification_model():
    obj = models.Notification(name='foo')
    assert str(obj) == 'foo'


def test_user_notification_model(user):
    obj = models.UserNotification(
        user=user.user, notification=models.Notification(name='foo'))
    assert str(obj) == 'John Doe - foo'

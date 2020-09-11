from tulius.forum import models
from tulius.forum.other import models as other_models
from tulius.forum.comments import models as comment


def test_upload_file_model(user):
    obj = models.UploadedFile(
        user=user.user,
        name='foo',
        mime='image/jpeg'
    )
    assert obj.is_image()
    assert str(obj) == 'foo'
    obj.mime = 'binary'
    assert not obj.is_image()


def test_voting(user):
    obj = other_models.VotingVote(
        user=user.user, choice=1, comment=comment.Comment(title='bar'))
    assert str(obj) == 'bar - 1(John Doe)'

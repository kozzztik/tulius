from unittest import mock

from tulius.forum.comments import views


def test_delete_comments_pagination(room_group, thread, user):
    with mock.patch.object(views.CommentsBase, 'COMMENTS_ON_PAGE', 1):
        # post first comment
        response = user.post(
            thread['url'] + 'comments_page/', {
                'reply_id': thread['first_comment_id'],
                'title': 'hello', 'body': 'comment1', 'media': {}})
        assert response.status_code == 200
        data = response.json()
        assert len(data['comments']) == 1
        comment1 = data['comments'][0]
        assert comment1['page'] == 2
        # post second comment
        response = user.post(
            thread['url'] + 'comments_page/', {
                'reply_id': thread['first_comment_id'],
                'title': 'hello', 'body': 'comment2', 'media': {}})
        assert response.status_code == 200
        data = response.json()
        assert len(data['comments']) == 1
        comment2 = data['comments'][0]
        assert comment2['page'] == 3
        # check comment2 is on 3 page
        response = user.get(thread['url'] + 'comments_page/?page=3')
        assert response.status_code == 200
        data = response.json()
        assert len(data['comments']) == 1
        assert data['comments'][0]['id'] == comment2['id']
    # delete first comment
    with mock.patch.object(views.CommentsBase, 'COMMENTS_ON_PAGE', 1):
        response = user.delete(comment1['url'] + '?comment=wow')
        assert response.status_code == 200
        # check second comment now on page 2
        response = user.get(thread['url'] + 'comments_page/?page=2')
    assert response.status_code == 200
    data = response.json()
    assert len(data['comments']) == 1
    assert data['comments'][0]['id'] == comment2['id']

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from ..models import Board, Post, Topic
from ..views import PostUpdateView


class PostUpdateViewTestCase(TestCase):
    '''
    Base test case to be used in all postUpdateView 
    '''

    def setUp(self):
        self.board=Board.objects.create(name='django',description='Django board')
        self.username='john'
        self.password='123'

        user=User.objects.create_user(username=self.username,email='john@gmail.com',password=self.password)
        self.topic=Topic.objects.create(subject='Hello, world',board=self.board, starter=user)
        self.post=Post.objects.create(message='this is a test message',topic=self.topic, created_by=user)
        self.url=reverse('edit_post',kwargs={
            'pk':self.board.pk,
            'topic_pk':self.topic.pk,
            'post_pk':self.post.pk
        })
    
class LoginRequiredPostUpdateViewTests(PostUpdateViewTestCase):

    def test_redirection(self):
        '''test if only logged in users can edit the posts'''

        login_url=reverse('login')
        response=self.client.get(self.url)
        self.assertRedirects(response,'{login_url}?next={url}'.format(login_url=login_url, url=self.url))

class UnauthorizedPostUpdteViewTests(PostUpdateViewTestCase):

    def setUp(self):
        '''create a new user different from the one who posted'''

        super().setUp()
        username='Rock'
        password='321'
        user=User.objects.create_user(username=username, email='rock@gmail.com', password=password)
        self.client.login(username=username, password=password)
        self.response=self.client.get(self.url)
    
    def test_status_code(self):
        '''A topic should be edited only by the owner
        unauthorized users should get a 404 response '''

        self.assertEquals(self.response.status_code, 404)

        
from django.test import TestCase, Client
from django.utils import timezone
import json

from .models import *
from .views import get_followage

class NetworkTest(TestCase):

    def setUp(self):
        #Test User 1
        user1 = User.objects.create_user(username = "user1", password = "user1")
        #Test User 2
        User.objects.create_user(username = "user2", password = "user2")
        #Test Post 
        Post.objects.create(user = user1, post = "This is a test", timestamp = timezone.now(), likes = 0)

    def test_follow(self):
        user1 = User.objects.get(username = 'user1')
        user2 = User.objects.get(username = 'user2')
        user1.follow(user2)
        
        self.assertEqual(Follow.objects.count(), 1)
        self.assertTrue(Follow.objects.get(followers = user1, following = user2))

    def test_unfollow(self):
        user1 = User.objects.get(username = 'user1')
        user2 = User.objects.get(username = 'user2')
        Follow.objects.create(followers = user1, following = user2)
        user1.unfollow(user2)

        self.assertEqual(Follow.objects.count(), 0)
        self.assertRaises(Follow.DoesNotExist, Follow.objects.get, followers = user1, following = user2)

    def test_get_likes(self):
        user2 = User.objects.get(username = 'user2')
        post = Post.objects.get(post = "This is a test")
        Like.objects.create(liker = user2, post = post)

        self.assertEqual(post.get_likes(), [user2])

    def test_index(self):
        client = Client()
        response = client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].paginator.count, 1)

    def test_login_page(self):
        client = Client()
        response = client.get("/login")

        self.assertEqual(response.status_code, 200)

    def test_valid_login(self):
        client = Client()
        response = client.post('/login', {
            'username': 'user1',
            'password': 'user1'
        })

        self.assertRedirects(response, '/', fetch_redirect_response=False)

    def test_invalid_login(self):
        client = Client()
        response = client.post('/login', {
            'username': 'user1',
            'password': 'user2'
        })

        self.assertEqual(response.status_code, 200)

    def test_logout_page(self):
        client = Client()
        response = client.get('/logout')

        self.assertEquals(response.status_code, 302)

    def test_register_page(self):
        client = Client()
        response = client.get('/register')

        self.assertEquals(response.status_code, 200)

    def test_valid_register(self):
        client = Client()
        response = client.post('/register', {
            'username': 'user3',
            'email': '',
            'password': 'user3',
            'confirmation': 'user3'
        })

        self.assertEquals(response.status_code, 302)

    def test_invalid_register(self):
        client = Client()
        response = client.post('/register', {
            'username': 'user3',
            'email': '',
            'password': 'user3',
            'confirmation': 'user2'
        })

        self.assertEquals(response.status_code, 200)

    def test_taken_register(self):
        client = Client()
        response = client.post('/register', {
            'username': 'user2',
            'email': '',
            'password': 'user3',
            'confirmation': 'user3'
        })

        self.assertEquals(response.status_code, 200)

    def test_post(self):
        client = Client()
        client.login(username = 'user1', password = 'user1')
        response = client.post('/newpost', json.dumps({'post': 'Test Post'}), 'json')
        client.logout()

        self.assertEquals(response.status_code, 201)
        self.assertEquals(json.loads(response.content)['message'], "Post created successfully.")

    def test_post_with_GET_request(self):
        client = Client()
        response = client.get('/newpost')

        self.assertEquals(json.loads(response.content)['error'], "POST request required.")
        self.assertEquals(response.status_code, 400)

    def test_post_with_user_not_logged_in(self):
        client = Client()
        response = client.post('/newpost', json.dumps({'post': 'Test Post'}), 'json')

        self.assertEquals(json.loads(response.content)['error'], "You should be logged in.")
        self.assertEquals(response.status_code, 400)

    def test_post_with_empty_post(self):
        client = Client()
        client.login(username = 'user1', password = 'user1')
        response = client.post('/newpost', json.dumps({'post': ''}), 'json')
        client.logout()

        self.assertEquals(json.loads(response.content)['error'], "Post can't have more than 280 characters or less than 1")
        self.assertEquals(response.status_code, 400)

    def test_post_with_more_than_280_chars(self):
        post_content = ''
        for i in range (281):
            post_content += 'a'
        client = Client()
        client.login(username = 'user1', password = 'user1')
        response = client.post('/newpost', json.dumps({'post': post_content}), 'json')
        client.logout()
        self.assertEquals(json.loads(response.content)['error'], "Post can't have more than 280 characters or less than 1")
        self.assertEquals(response.status_code, 400)

    def test_get_followage(self):
        user1 = User.objects.get(username = 'user1')
        user2 = User.objects.get(username = 'user2')
        user1.follow(user2)

        #0 Followers and Following 1 user
        self.assertEquals(get_followage('user1'), (0,1))

    def test_get_profile(self):
        user1 = User.objects.get(username='user1')
        client = Client()
        response = client.get(f'/user/{user1.username}')

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['user_profile'], user1)
        self.assertEquals(response.context['following'], False)
        self.assertEquals(response.context['followers'], 0)
        self.assertEquals(response.context['following_number'], 0)

    def test_get_self_profile(self):
        user1 = User.objects.get(username='user1')
        client = Client()
        client.login(username = 'user1', password = 'user1')
        response = client.get(f'/user/{user1.username}')

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['user_profile'], user1)
        self.assertEquals(response.context['owner'], True)
        self.assertEquals(response.context['followers'], 0)
        self.assertEquals(response.context['following_number'], 0)

    def test_get_invalid_profile(self):
        client = Client()
        response = client.get('/user/user3')

        self.assertEquals(response.status_code, 404)
        self.assertEquals(json.loads(response.content)['error'], 'User Not Found.')

    def test_follow_page(self):
        user1 = User.objects.get(username = 'user1')
        user2 = User.objects.get(username = 'user2')
        user1.follow(user2)

        client = Client()
        client.login(username = 'user1', password = 'user1')
        response = client.get('/following')

        self.assertEqual(response.context['page_obj'].paginator.count, 0)
        self.assertEqual(response.status_code, 200)

    def test_follow_page_not_logged_in(self):
        client = Client()
        response = client.get('/following')

        #It should be 302 because it redirects to a 404 NotFound default page because of the @login_required decorator
        self.assertEqual(response.status_code, 302)

    def test_update_post(self):
        post = Post.objects.get(post = 'This is a test')

        client = Client()
        client.login(username = 'user1', password = 'user1')
        response = client.put(f'/update/{post.id}', json.dumps({'post': 'Edited Post.'}), 'json')

        self.assertEqual(json.loads(response.content)['message'], "Email updated successfully."),
        self.assertEqual(response.status_code, 201)

    def test_update_invalid_post(self):
        client = Client()
        client.login(username = 'user1', password = 'user1')
        response = client.put(f'/update/9', json.dumps({'post': 'Edited Post.'}), 'json')

        self.assertEqual(json.loads(response.content)['error'], "Post not found."),
        self.assertEqual(response.status_code, 404)
    
    def test_update_post_with_GET_method(self):
        client = Client()
        client.login(username = 'user1', password = 'user1')
        response = client.get('/update/1')

        self.assertEqual(json.loads(response.content)['error'], "PUT request required."),
        self.assertEqual(response.status_code, 400)

    def test_update_post_with_POST_method(self):
        client = Client()
        client.login(username = 'user1', password = 'user1')
        response = client.post('/update/1')

        self.assertEqual(json.loads(response.content)['error'], "PUT request required."),
        self.assertEqual(response.status_code, 400)

    def test_update_with_empty_post(self):
        client = Client()
        client.login(username = 'user1', password = 'user1')
        response = client.put('/update/1', json.dumps({'post': ''}), 'json')
        client.logout()

        self.assertEquals(json.loads(response.content)['error'], "Post can't have more than 280 characters or less than 1")
        self.assertEquals(response.status_code, 400)

    def test_update_post_with_more_than_280_chars(self):
        post_content = ''
        for i in range (281):
            post_content += 'a'
        client = Client()
        client.login(username = 'user1', password = 'user1')
        response = client.put('/update/1', json.dumps({'post': post_content}), 'json')
        client.logout()

        self.assertEquals(json.loads(response.content)['error'], "Post can't have more than 280 characters or less than 1")
        self.assertEquals(response.status_code, 400)

    def test_update_post_not_logged_in(self):
        client = Client()
        response = client.put('/update/1')

        #It should be 302 because it redirects to a 404 NotFound default page because of the @login_required decorator
        self.assertEqual(response.status_code, 302)

    def test_like(self):
        post = Post.objects.get(post = "This is a test")

        client = Client()
        client.login(username = 'user1', password = 'user1')
        response = client.put(f'/like/{post.id}', json.dumps({'like': True}), 'json')
        client.logout()

        self.assertEqual(json.loads(response.content)['message'], "Email updated successfully.")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Like.objects.count(), 1)

    def test_dislike(self):
        post = Post.objects.get(post = "This is a test")
        user = User.objects.get(username = 'user1')
        Like.objects.create(liker = user, post = post)

        client = Client()
        client.login(username = 'user1', password = 'user1')
        response = client.put(f'/like/{post.id}', json.dumps({'like': False}), 'json')
        client.logout

        self.assertEqual(json.loads(response.content)['message'], "Email updated successfully.")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Like.objects.count(), 0)

    def test_like_with_invalid_post(self):
        client = Client()
        client.login(username = 'user1', password = 'user1')
        response = client.put('/like/6', json.dumps({'like': True}), 'json')
        client.logout()

        self.assertEqual(json.loads(response.content)['error'], "Post not found.")
        self.assertEqual(response.status_code, 404)

    def test_like_with_GET_method(self):
        client = Client()
        client.login(username = 'user1', password = 'user1')
        response = client.get('/like/1')
        client.logout

        self.assertEqual(json.loads(response.content)['error'], "PUT request required.")
        self.assertEqual(response.status_code, 400)

    def test_like_with_POST_method(self):
        client = Client()
        client.login(username = 'user1', password = 'user1')
        response = client.post('/like/1', json.dumps({'like': True}), 'json')
        client.logout

        self.assertEqual(json.loads(response.content)['error'], "PUT request required.")
        self.assertEqual(response.status_code, 400)

    def test_like_not_logged_in(self):
        client = Client()
        response = client.put('/like/1', json.dumps({'like': True}), 'json')

        #It should be 302 because it redirects to a 404 NotFound default page because of the @login_required decorator
        self.assertEqual(response.status_code, 302)
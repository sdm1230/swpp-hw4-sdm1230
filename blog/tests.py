from django.test import TestCase, Client
import json
from .models import Article,Comment
from django.contrib.auth.models import User

class BlogTestCase(TestCase):

    def setUp(self):
        user1 = User.objects.create_user(username='username1', password='password1')
        user2 = User.objects.create_user(username='username2', password='password2')
        article1 = Article.objects.create(id=1,title="title1",content='content1',author=user1)
        article2 = Article.objects.create(id=2,title="title2",content='content2',author=user2)
        Comment.objects.create(id=1,article=article1,content='comment1',author=user1)
        Comment.objects.create(id=2,article=article1,content='comment2',author=user2)
        Comment.objects.create(id=3,article=article2,content='comment3',author=user1)
        Comment.objects.create(id=4,article=article2,content='comment4',author=user2)

    def test_csrf(self):
        # By default, csrf checks are disabled in test client
        # To test csrf protection we enforce csrf checks here
        client = Client(enforce_csrf_checks=True)

        # Request without csrf token returns 403 response
        response = client.post('/api/signup/', json.dumps({'username': 'test_username', 'password': 'test_password'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 403)  

        response = client.post('/api/signin/', json.dumps({'username': 'test_username', 'password': 'test_password'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 403)  

        response = client.post('/api/article/', json.dumps({'title': 'test_title', 'content': 'test_content'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 403)  

        response = client.post('/api/article/1/comment/', json.dumps({'content': 'test_comment'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 403)  


        response = client.put('/api/article/1/', json.dumps({'title': 'test_edit_title', 'content': 'test_edit_content'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 403)  

        response = client.delete('/api/article/1/', 
                               content_type='application/json')
        self.assertEqual(response.status_code, 403)  

        response = client.put('/api/comment/1/', json.dumps({'content': 'test_edit_comment'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 403)  

        response = client.delete('/api/comment/1/',
                               content_type='application/json')
        self.assertEqual(response.status_code, 403) 


         # Pass csrf protection

        response = client.get('/api/token/')
        self.assertEqual(response.status_code, 204)
        csrftoken = response.cookies['csrftoken'].value  # Get csrf token from cookie
        response = client.post('/api/signup/', json.dumps({'username': 'test_username', 'password': 'test_password'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 201) 

        response = client.get('/api/token/')
        csrftoken = response.cookies['csrftoken'].value 
        response = client.post('/api/signin/', json.dumps({'username': 'test_username', 'password': 'test_password'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 204)  

        response = client.get('/api/token/')
        csrftoken = response.cookies['csrftoken'].value 
        response = client.post('/api/article/', json.dumps({'title': 'test_title', 'content': 'test_content'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 201)  

        response = client.get('/api/token/')
        csrftoken = response.cookies['csrftoken'].value 
        response = client.post('/api/article/3/comment/', json.dumps({'content': 'test_comment'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 201)  

        response = client.get('/api/token/')
        csrftoken = response.cookies['csrftoken'].value 
        response = client.put('/api/article/3/', json.dumps({'title': 'test_edit_title', 'content': 'test_edit_content'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 200)  

        response = client.get('/api/token/')
        csrftoken = response.cookies['csrftoken'].value 
        response = client.put('/api/comment/5/', json.dumps({'content': 'test_edit_comment'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 200)  

        response = client.get('/api/token/')
        csrftoken = response.cookies['csrftoken'].value 
        response = client.delete('/api/comment/5/',
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 200)  

        response = client.get('/api/token/')
        csrftoken = response.cookies['csrftoken'].value 
        response = client.delete('/api/article/3/', 
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 200)


    def test_method_impossible(self):
        client = Client()

        response = client.delete('/api/token/')
        self.assertEqual(response.status_code,405)
        
        response = client.get('/api/signup/')
        self.assertEqual(response.status_code,405)

        response = client.get('/api/signin/')
        self.assertEqual(response.status_code,405)

        response = client.delete('/api/signout/')
        self.assertEqual(response.status_code,405)

        response = client.delete('/api/article/')
        self.assertEqual(response.status_code,405)

        response = client.post('/api/article/1/')
        self.assertEqual(response.status_code,405)

        response = client.delete('/api/article/1/comment/')
        self.assertEqual(response.status_code,405)

        response = client.post('/api/comment/1/')
        self.assertEqual(response.status_code,405)

    def test_signin_fail(self):
        client = Client()
        response = client.post('/api/signin/', json.dumps({'username': 'none_username', 'password': 'none_password1'}),
                               content_type='application/json')
        self.assertEqual(response.status_code,401)

    def test_signout(self):
        client = Client()
        response = client.post('/api/signin/', json.dumps({'username': 'username1', 'password': 'password1'}),
                               content_type='application/json')
        response = client.get('/api/signout/')
        self.assertEqual(response.status_code,204)
        response = client.get('/api/signout/')
        self.assertEqual(response.status_code,401)

    def test_authentication_false(self):
        client = Client()

        response = client.get('/api/article/', 
                               content_type='application/json')
        self.assertEqual(response.status_code, 401)  

        response = client.get('/api/article/1/', 
                               content_type='application/json')
        self.assertEqual(response.status_code, 401)  

        response = client.get('/api/article/1/comment/', 
                               content_type='application/json')
        self.assertEqual(response.status_code, 401)  

        response = client.get('/api/comment/1/', 
                               content_type='application/json')
        self.assertEqual(response.status_code, 401)  

        response = client.post('/api/article/', json.dumps({'title': 'test_title', 'content': 'test_content'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 401)  

        response = client.post('/api/article/1/comment/', json.dumps({'content': 'test_comment'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 401)  


        response = client.put('/api/article/1/', json.dumps({'title': 'test_edit_title', 'content': 'test_edit_content'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 401)  

        response = client.delete('/api/article/1/', 
                               content_type='application/json')
        self.assertEqual(response.status_code, 401)  

        response = client.put('/api/comment/1/', json.dumps({'content': 'test_edit_comment'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 401)  

        response = client.delete('/api/comment/1/',
                               content_type='application/json')
        self.assertEqual(response.status_code, 401)  

    def test_get_method_well(self):
        client = Client()
        response = client.post('/api/signin/', json.dumps({'username': 'username1', 'password': 'password1'}),
                                content_type='application/json')
        
        response = client.get('/api/article/', 
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)  

        response = client.get('/api/article/1/', 
                               content_type='application/json')
        self.assertEqual(response.status_code, 200) 
        self.assertIn('1',response.content.decode())

        response = client.get('/api/article/1/comment/', 
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)  
        self.assertIn('1',response.content.decode())

        response = client.get('/api/comment/1/', 
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)  
        self.assertIn('1',response.content.decode())

    def test_notfound(self):
        client = Client()
        response = client.post('/api/signin/', json.dumps({'username': 'username1', 'password': 'password1'}),
                                content_type='application/json')

        response = client.get('/api/article/10/', 
                               content_type='application/json')
        self.assertEqual(response.status_code, 404) 

        response = client.get('/api/article/10/comment/', 
                               content_type='application/json')
        self.assertEqual(response.status_code, 404)  

        response = client.get('/api/comment/10/', 
                               content_type='application/json')
        self.assertEqual(response.status_code, 404)

        response = client.put('/api/article/10/', json.dumps({'title': 'test_notfound_edit_title', 'content': 'test_notfound_edit_content'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 404)  

        response = client.delete('/api/article/10/', 
                               content_type='application/json')
        self.assertEqual(response.status_code, 404)  

        response = client.put('/api/comment/10/', json.dumps({'content': 'test_notfound_edit_comment'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 404)  

        response = client.delete('/api/comment/10/',
                               content_type='application/json')
        self.assertEqual(response.status_code, 404)

        response = client.post('/api/article/10/comment/', json.dumps({'content': 'test_notfound_comment'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 404)

        response = client.put('/api/comment/10/', json.dumps({'content': 'test_notfound_edit_comment'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 404)  


    def test_forbidden(self):
        client = Client()
        response = client.post('/api/signin/', json.dumps({'username': 'username1', 'password': 'password1'}),
                                content_type='application/json')

        response = client.put('/api/article/2/', json.dumps({'title': 'test_forbidden_edit_title', 'content': 'test_forbidden_edit_content'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 403)  

        response = client.delete('/api/article/2/', 
                               content_type='application/json')
        self.assertEqual(response.status_code, 403)  

        response = client.put('/api/comment/2/', json.dumps({'content': 'test_forbidden_edit_comment'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 403)  

        response = client.delete('/api/comment/2/',
                               content_type='application/json')
        self.assertEqual(response.status_code, 403)
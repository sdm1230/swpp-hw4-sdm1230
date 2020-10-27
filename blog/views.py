from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest, JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie
import json

from .models import Article,Comment
from django.contrib.auth import authenticate,login,logout

def signup(request):
    if request.method == 'POST':
        req_data = json.loads(request.body.decode())
        username = req_data['username']
        password = req_data['password']
        User.objects.create_user(username=username, password=password)
        return HttpResponse(status=201)
        
    else:
        return HttpResponseNotAllowed(['POST'])


def signin(request):
    if request.method == 'POST':
        
        req_data = json.loads(request.body.decode())
        username = req_data['username']
        password = req_data['password']
        
        user = authenticate(request,username=username, password=password)

        if user is not None:
            login(request,user)
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=401)

    else:
        return HttpResponseNotAllowed(['POST'])


def signout(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            logout(request)
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=401)

    else:
        return HttpResponseNotAllowed(['GET'])


def article(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        else:
            article_all_list = [{'id':article.id,'title':article.title,'content':article.content,'author':article.author.id} 
                                    for article in Article.objects.all()]
            return JsonResponse(article_all_list,safe=False,status=200)
        
   
    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        else:
            body = request.body.decode()
            article_title = json.loads(body)['title']
            article_content = json.loads(body)['content']
            article_author = request.user

            article = Article(title=article_title, content = article_content, author = article_author)
            article.save()

            response_dict = {'id':article.id,'title': article.title, 'content':article.content, 'author': article.author.id}
            return JsonResponse(response_dict,status=201)

    else:
        return HttpResponseNotAllowed(['GET','POST'])
    

def article_info(request, article_id=0):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        else:
            if not Article.objects.filter(id=article_id).exists():
                return HttpResponse(status=404)

            else:   
                article = Article.objects.get(id=article_id)
                return JsonResponse({'id':article.id,'title':article.title,'content':article.content,'author':article.author.id},status=200)

    elif request.method == 'PUT':
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        else:
            if not Article.objects.filter(id=article_id).exists():
                return HttpResponse(status=404)

            else:    
                article = Article.objects.get(id=article_id)
                
                if request.user.id != article.author.id:
                    return HttpResponse(status=403)

                else:
                    body = request.body.decode()
                    article_title = json.loads(body)['title']
                    article_content = json.loads(body)['content']

                    
                    article.title = article_title
                    article.content = article_content
                    article.save()

                    response_dict={'id':article.id,'title':article.title,'content':article.content,'author':article.author.id}
                    return JsonResponse(response_dict,status=200)

    elif request.method == 'DELETE':
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        else:
            if not Article.objects.filter(id=article_id).exists():
                return HttpResponse(status=404)

            else:   
                article = Article.objects.get(id=article_id)
                
                if request.user.id != article.author.id:
                    return HttpResponse(status=403)

                else:
                    article.delete()
                    return HttpResponse(status=200)

    else:
        return HttpResponseNotAllowed(['GET','PUT','DELETE'])


def article_comments(request,article_id=0):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        else:
            if not Article.objects.filter(id=article_id).exists():
                return HttpResponse(status=404)

            else:   
                comment_all_list = [{'id':comment.id,'article':comment.article.id,'content':comment.content,'author':comment.author.id} 
                                                    for comment in Comment.objects.filter(article_id = article_id)]
                return JsonResponse(comment_all_list,safe=False,status=200)

    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        else:
            if not Article.objects.filter(id=article_id).exists():
                return HttpResponse(status=404)

            else:
                body = request.body.decode()
                comment_content = json.loads(body)['content']
                
                comment_article = Article.objects.get(id=article_id)
                comment_author = request.user

                comment = Comment(article=comment_article, content = comment_content, author = comment_author)
                comment.save()

                response_dict = {'id':comment.id,'article': comment.article.id, 'content':comment.content, 'author': comment.author.id}
                return JsonResponse(response_dict,status=201)

    else:
        return HttpResponseNotAllowed(['GET','POST'])


def comment(request,comment_id=0):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        else:
            if not Comment.objects.filter(id=comment_id).exists():
                return HttpResponse(status=404)

            else:  
                comment = Comment.objects.get(id=comment_id)
                return JsonResponse({'id':comment.id,'article':comment.article.id,'content':comment.content,'author':comment.author.id},status=200)
    

    elif request.method == 'PUT':
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        else:
            if not Comment.objects.filter(id=comment_id).exists():
                return HttpResponse(status=404)

            else:   
                comment = Comment.objects.get(id=comment_id)
                
                if request.user.id != comment.author.id:
                    return HttpResponse(status=403)

                else:
                    body = request.body.decode()
                    comment_content = json.loads(body)['content']
                    
                    comment.content = comment_content
                    comment.save()

                    response_dict={'id':comment.id,'article':comment.article.id,'content':comment.content,'author':comment.author.id}
                    return JsonResponse(response_dict,status=200)
    

    elif request.method == 'DELETE':
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        else:
            if not Comment.objects.filter(id=comment_id).exists():
                return HttpResponse(status=404)

            else:  
                comment = Comment.objects.get(id=comment_id)
                
                if request.user.id != comment.author.id:
                    return HttpResponse(status=403)

                else:
                    comment.delete()
                    return HttpResponse(status=200)
    
    else:
        return HttpResponseNotAllowed(['GET','PUT','DELETE'])


@ensure_csrf_cookie
def token(request):
    if request.method == 'GET':
        return HttpResponse(status=204)
    else:
        return HttpResponseNotAllowed(['GET'])

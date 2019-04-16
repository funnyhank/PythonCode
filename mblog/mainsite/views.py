from django.shortcuts import render
from django.http import HttpResponse
from .models import Post

# Create your views here.
def homepage(request):
    posts = Post.objects.all()
    post_list = list()
    for count, post in enumerate(posts):
        post_list.append("No.{}:".format(str(count))+str(post)+"<hr>")
        post_list.append("<small>"+str(post.body.encode('utf-8'))+"</small><br><br>")
    return HttpResponse(post_list)
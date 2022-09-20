import re
import urllib.request as urllib2
from random import choice
from urllib.error import URLError, HTTPError

from django.core.files.base import File
from django.core.files.temp import NamedTemporaryFile
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from pytils.translit import slugify
from randomfilestorage.storage import RandomFileSystemStorage
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from blog.models import Post


class Index(TemplateView):
    template_name = 'theme/page/index.html'

    def get_context_data(self, **kwargs):
        slider = Post.objects.order_by('-date').order_by("?")[0:4]
        post = Post.objects.order_by('-date')[0:6]

        context = {
            'slider': slider,
            'post': post
        }
        return context


class PostDetail(TemplateView):
    template_name = 'theme/page/detail.html'

    def get_context_data(self, **kwargs):
        post = Post.objects.get(slug=kwargs['slug'])
        share = Post.objects.order_by('-date').order_by("?")[0:8]
        share_left = Post.objects.order_by('-date').order_by("?")[0:5]
        context = {
            'post': post,
            'share': share,
            'share_left': share_left,
        }
        return context


class YandexTurbo(ListView):
    template_name = 'theme/addon/yandex_turbo/turbo.xml'
    model = Post
    context_object_name = 'turbo'
    paginate_by = 1000


random_storage = RandomFileSystemStorage(location='/media/')


class ParceObjects(APIView):
    image = []

    def get(self, request, *args, **kwargs):
        try:
            return Response("")
        except:
            return Response("")

    def post(self, request):

        try:
            if len(self.image) >= 10:
                self.image.remove(self.image[0])

            form = request.data
            title = form['title']
            new_string = re.sub(r'[^\w\s]', '', title)
            slug = slugify(new_string)

            count = Post.objects.all().count()
            current_slug = f'{slug}-{int(count) + 1}'

            self.image.append(form['image'])
            img_temp = NamedTemporaryFile()
            img_temp.write(urllib2.urlopen(form['image']).read())
            img_temp.flush()
            Post.objects.create(title=form['title'], content=form['content'], image=File(img_temp, name=f'{title}.jpg'),
                                slug=current_slug)
            return Response('', status=status.HTTP_201_CREATED)
        except (ValueError, OSError, URLError, HTTPError):
            form = request.data
            form['image'] = choice(self.image)
            title = form['title']
            new_string = re.sub(r'[^\w\s]', '', title)
            slug = slugify(new_string)

            count = Post.objects.all().count()
            current_slug = f'{slug}-{int(count) + 1}'

            img_temp = NamedTemporaryFile()
            img_temp.write(urllib2.urlopen(form['image']).read())
            img_temp.flush()

            Post.objects.create(title=form['title'], content=form['content'], image=File(img_temp, name=f'{title}.jpg'),
                                slug=current_slug)
            return Response('', status=status.HTTP_201_CREATED)
        except:
            return Response('Invalid data ', status=status.HTTP_200_OK)

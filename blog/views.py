import re
import urllib.request as urllib2
from random import choice
from urllib.error import URLError, HTTPError
from django.core.files.base import File
from django.core.files.temp import NamedTemporaryFile
from django.views.generic import ListView, TemplateView
from django.views.decorators.csrf import csrf_protect
from pytils.translit import slugify
from randomfilestorage.storage import RandomFileSystemStorage
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from blog.models import Post, Galery


class Index(TemplateView):
    """
    Класс отображения главной страницы
    использует методы контекстной обработки модели
    """
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
    """
    Класс отображения страницы детального просмотра поста
    использует методы контекстной обработки модели
    """
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
    """
    Класс отображения страницы плагина yandex_turbo
    использует методы стандартный метод обработки модели
    и пагинацию на условии: 1000 постов на 1 странице
    """
    template_name = 'theme/addon/yandex_turbo/turbo.xml'
    model = Post
    context_object_name = 'turbo'
    paginate_by = 1000


# Объявление переменной для библиотеки django-random-filestorage
random_storage = RandomFileSystemStorage(location='/media/')


class ParceObjects(APIView):
    """
    Класс DRF создания поста в блог используя API
    """

    def change_content(self, galery: list, post):
        content = post.content.split('\n')
        for tag in range(len(content)):
            for image_link in galery:
                if 'itemprop' in content[tag]:
                    content[tag] = (
                        f'<p><span itemprop="image" itemscope=""><img itemprop="url image" loading="lazy" class="size-full wp-image-4784 aligncenter" src={image_link} alt="" width="600" height="800" sizes="(max-width: 600px) 100vw, 600px"><meta itemprop="width" content="600"><meta itemprop="height" content="800"></span></p>')

        content = "".join(content)

        print(f"================================================")

        Post.objects.filter(id=post.id).update(content=content)

    def save_images_to_galery(self, title, images: list, post):
        count = 0
        galery = []
        for image in images:  # получаю список с ссылками на фото
            count += 1
            img_temp = NamedTemporaryFile()
            img_temp.write(urllib2.urlopen(image).read())
            img_temp.flush()
            photo = Galery.objects.create(image=File(img_temp, name=f'{title}-{count}.jpg'), post=post)
            galery.append(photo.image.url)

        self.change_content(galery, post)

    def post(self, request):
        try:
            form = request.data
            title = form['title']

            slug = slugify(title)

            amount_of_posts = Post.objects.all().count()
            slug = f'{slug}-{int(amount_of_posts) + 1}'

            img_temp = NamedTemporaryFile()
            img_temp.write(urllib2.urlopen(form['image']).read())
            img_temp.flush()
            post = Post.objects.create(title=form['title'], content=form['content'],
                                       image=File(img_temp, name=f'{title}.jpg'),
                                       slug=slug)

            self.save_images_to_galery(title, form['img_list'], post)

            return Response('', status=status.HTTP_201_CREATED)
        except:
            return Response('Invalid data', status=status.HTTP_400_BAD_REQUEST)

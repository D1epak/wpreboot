from django.core.paginator import Paginator
from django.shortcuts import render

from blog.models import Post


def custom_sitemap(request):
    contact_list = Post.objects.all()
    paginator = Paginator(contact_list, 5)  # Show 25 contacts per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'theme/addon/custom_sitemap/sitemap.html', {'page_obj': page_obj})

from django.core.paginator import Paginator

from .constants import MAX_POSTS


def paginator_func(request, posts):
    paginator = Paginator(posts, MAX_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj

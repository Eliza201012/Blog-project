from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import EmailPostForm
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseRedirect

def post_list(request):
    post_list = Post.published.all()
    # Посторінкова розбивка з 3 постами на сторінку
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)

    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # Якщо page_number не ціле число, то
        # показати першу сторінку
        posts = paginator.page(1)
    except EmptyPage:
        # Якщо page_number знаходиться поза межами діапазону, то
        # показати останню сторінку
        posts = paginator.page(paginator.num_pages)

    return render(request, "blog/post/list.html", {"posts" : posts})

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, status=Post.Status.PUBLISHED, slug=post,
                             publish__year = year,
                             publish__month = month,
                             publish__day = day)
    return render(request, "blog/post/detail.html", {"post" : post})

def post_share(request, post_id):
    # Отримати пост за ідентифікатором id
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent=False

    if request.method == "POST":
        # Форма була передана на обробку
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Поля форми успішно пройшли валідацію
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " \
                    f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                    f"{cd['name']}\'s ({cd['email']}) \ncomments: {cd['comments']}"
            send_mail(subject, message, settings.EMAIL_HOST_USER,
                      [cd['to']])
            sent = True
            # ... надіслати електронний лист
        return HttpResponseRedirect("/")
    else:
        form = EmailPostForm()
        return render(request, 'blog/post/share.html', {'post':post, 'form':form, 'sent':sent})
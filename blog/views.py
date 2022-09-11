from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.mail import send_mail
from .models import Post, Comment
from .forms import EmailForm, CommentForm
from taggit.models import Tag


def post_list(request ,tag_slug = None):
    posts = Post.publish.all()
    tag = None 

    if tag_slug:
        tag = get_object_or_404(Tag,slug = tag_slug)
        posts = posts.filter(tags__in = [tag])


    paginator = Paginator(posts, 3)
    page = request.GET.get("page")
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, "pages/posts.html", {"page": page, "posts": posts,'tag':tag})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        slug=post,
        status="published",
        published__year=year,
        published__month=month,
        published__day=day,
    )

    comments = post.comments.filter(active=True)
    new_comment = None

    if request.method == "POST":
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()
    return render(
        request,
        "pages/post_detail.html",
        {
            "post": post,
            "comments": comments,
            "new_comment": new_comment,
            "comment_form": comment_form,
        },
    )


def share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status="published")
    sent = False
    if request.method == "POST":
        form = EmailForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absloute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}'s comments: {cd['comments']}"
            )
            send_mail(subject, message, "sender", "receiver")
            sent = True
    else:
        form = EmailForm()
    return render(
        request, "pages/share_post.html", {"post": post, "form": form, "sent": sent}
    )

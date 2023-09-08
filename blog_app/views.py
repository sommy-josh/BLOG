from django.shortcuts import render,get_object_or_404
from django.core.paginator import Paginator,EmptyPage,\
                                PageNotAnInteger
from .models import Post,Comment
from .forms import EmailForm,CommentForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count



# class PostListView(ListView):
#     queryset=Post.objects.all()
#     context_object_name='posts'
#     paginate_by=3
#     template_name='post_share.html'

def post_list(request,tag_slug=None):
    Post_list=Post.objects.all()
    tag=None
    if tag_slug:
        tag=get_object_or_404(Tag, slug=tag_slug)
        Post_list=Post_list.filter(tags__in=[tag])
    paginator=Paginator(Post_list, 3)
    page_number=request.GET.get('page', 1)
    try:

        posts=paginator.page(page_number)
    except PageNotAnInteger:
        posts=paginator.page(1)
    except EmptyPage:
        posts=paginator.page(paginator.num_pages)

    return render(request,
                  'post_list.html',
                  {'posts':posts,'tag':tag})








def post_detail(request,year,month,day,post):
    post=get_object_or_404(Post,
                           slug=post,
                           publish__year=year,
                           publish__month=month,
                           publish__day=day)
    
    #list of active comments for this post
    comments=post.comments.filter(active=True)
    
    #form for users to comment
    form=CommentForm()
    #list of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts=Post.objects.filter(tags__in=post_tags_ids)\
                                .exclude(id=post.id)
    similar_posts=similar_posts.annotate(same_tags=Count('tags'))\
                                .order_by('-same_tags', '-publish')[:4]


    return render(request,'post_detail.html',{'post':post,'comments':comments,'form':form, 'similar_posts':similar_posts})


def post_share(request,post_id):
    post=get_object_or_404(Post,id=post_id)
    sent=False
    if request.method=='POST':
        form=EmailForm(request.POST)
        if form.is_valid():
            cd=form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url())
            subject=f"{cd['name']} recommends you read " \
                    f"{post.title}"
            message=f"Read{post.title} at {post_url}\n\n" \
                    f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject,message, 'chisomzzy1@gmail',
                      [cd['to']])
            sent=True
    else:
            form=EmailForm()
    return render(request, 'post_share.html',{'form':form,
                                                  'post':post,
                                                  'sent':sent})


@require_POST
def post_comment(request,post_id):
    post=get_object_or_404(Post, id=post_id)
    comment=None
    #A comment was posted
    form=CommentForm(data=request.POST)
    if form.is_valid():
        #create a comment object without saving it to the db
        comment=form.save(commit=False)
        #Assign the post to the comment
        comment.post=post
        #save the comment to the db
        comment.save()
    return render(request, 'comment.html', {'post':post,'form':form,'comment':comment})





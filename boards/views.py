from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse,Http404
from .models import Board,Topic, Post
from django.contrib.auth.models import User
from .forms import NewTopicForm, PostForm
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.views.generic import UpdateView
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.urls import reverse
# Create your views here.

# def home(request):

#     boards=Board.objects.all()
#     boards_names=list()

#     for board in boards:
#         boards_names.append(board.name)
#     return render(request,'home.html',{'boards':boards})

class BoardListView(ListView):
    model=Board
    context_object_name='boards'
    template_name='home.html'

# def board_topics(request,pk):
#     board = get_object_or_404(Board, pk=pk)
#     topics = board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
#     return render(request, 'topics.html',{'board':board,'topics':topics})

class TopicListView(ListView):
    model=Topic
    context_object_name='topics'
    template_name='topics.html'
    paginate_by=10

    def get_context_data(self, **kwargs):
        kwargs['board']=self.board
        return super().get_context_data(**kwargs)
    
    def get_queryset(self):
        self.board=get_object_or_404(Board,pk=self.kwargs.get('pk'))
        queryset=self.board.topics.order_by('-last_updated').annotate(replies=Count('posts')-1)
        return queryset
    
@login_required
def new_topic(request,pk):
    board = get_object_or_404(Board, pk=pk)

    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = request.user
            topic.save()
            post = Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=request.user
            )
            return redirect('board_topics', pk=board.pk,)  # TODO: redirect to the created topic page #topic_pk=topic.pk
    else:
        form = NewTopicForm()
    return render(request, 'new_topic.html', {'board': board, 'form': form})


def topic_posts(request,pk,topic_pk):
    topic=get_object_or_404(Topic,board__pk=pk,pk=topic_pk)
    topic.views +=1
    topic.save()
    return render(request,'topics_posts.html',{'topic':topic})


class PostListView(ListView):
    model=Post
    context_object_name='posts'
    template_name='topics_posts.html'
    paginate_by=2

    def get_context_data(self, **kwargs):
        session_key = 'viewed_topic_{}'.format(self.topic.pk)  # <-- here
        if not self.request.session.get(session_key, False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True           # <-- until here
        kwargs['topic']=self.topic
        return super().get_context_data(**kwargs)
    
    def get_queryset(self):
        self.topic=get_object_or_404(Topic, board__pk=self.kwargs.get('pk'),pk=self.kwargs.get('topic_pk'))
        queryset=self.topic.posts.order_by('created_at')
        return queryset

@login_required
def reply_topic(request, pk, topic_pk):
    topic=get_object_or_404(Topic, board__pk=pk, pk=topic_pk)

    if request.method=='POST':
        form =PostForm(request.POST)
        if form.is_valid():
            post=form.save(commit=False)
            post.topic=topic
            post.created_by=request.user
            post.save()

            topic.last_updated=timezone.now()
            topic.save()

            topic_url=reverse('topic_posts',kwargs={'pk':pk,'topic_pk':topic_pk})
            topic_post_url='{url}?page={page}#{id}'.format(
                url=topic_url,
                id=post.pk,
                page=topic.get_page_count()
            )
            return redirect(topic_post_url)
        
    else:
        form=PostForm()
    return render(request,'reply_topic.html',{'topic':topic,'form':form})

@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model=Post
    fields=('message',)
    template_name='edit_post.html'
    pk_url_kwarg='post_pk'
    context_object_name='post'

    def get_queryset(self):
        queryset=super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post=form.save(commit=False)
        post.updated_by=self.request.user
        post.updated_at=timezone.now()
        post.save()
        return redirect('topic_posts',pk=post.topic.board.pk,topic_pk=post.topic.pk)
    


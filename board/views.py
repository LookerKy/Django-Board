from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import UpdateView, ListView
from .models import Board, Topic, Post
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .forms import NewTopicForm, PostForm
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Create your views here.
# def home(request):
#     boards = Board.objects.all()
#     print(boards)
#     return render(request, 'home.html', {'boards': boards})


class BoardListView(ListView):
    model = Board
    context_object_name = 'boards'
    template_name = 'home.html'


# FBV
# def board_topics(request, pk):
#     board_list = get_object_or_404(Board, pk=pk)
#     queryset = board_list.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
#     page = request.GET.get('page', 1)
#
#     paginator = Paginator(queryset, 20)
#     try:
#         topics = paginator.page(page)
#     except PageNotAnInteger:
#         topics = paginator.page(1)
#     except EmptyPage:
#         topics = paginator.page(paginator.num_pages)
#
#     return render(request, 'topics.html', {'board': board_list, 'topics': topics})

# GCBV
class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'topics.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        kwargs['board'] = self.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        queryset = self.board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
        print(queryset)
        return queryset


@login_required(login_url='/login/')
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        user = request.user
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = user
            topic.save()

            post = Post.objects.create(
                topic=topic,
                message=form.cleaned_data.get('message'),
                created_by=user
            )
            return redirect('topic_posts', pk=pk, topic_pk=topic.pk)
    else:
        form = NewTopicForm()

    return render(request, 'new_topic.html', {'board': board, 'form': form})


# def topic_posts(request, pk, topic_pk):
#     topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
#     topic.views += 1
#     topic.save()
#     return render(request, 'topic_posts.html', {'topic': topic})


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'topic_posts.html'
    paginate_by = 2

    def get_context_data(self, *, object_list=None, **kwargs):
        session_key = 'viewed_topic_{}'.format(self.topic.pk)
        if not self.request.session.get(session_key, False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True
        # res??? topic ??????
        kwargs['topic'] = self.topic
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        # topic ??????
        self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        # context_object_name ??? res ?????? ?????? ?????? ?????? ????????? model.objects.all()??? ???
        queryset = self.topic.posts.order_by('created_by')
        return queryset


@login_required(login_url='/login/')
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()

            topic.last_updated = timezone.now()
            topic.save()
            return redirect('topic_posts', pk=pk, topic_pk=topic_pk)
    else:
        form = PostForm()

    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ['message', ]
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)

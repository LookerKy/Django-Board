from django.shortcuts import render, get_object_or_404, redirect
from django.http.response import HttpResponse
from .models import Board, Topic, Post
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import NewTopicForm
from django.http import Http404


# Create your views here.
def home(request):
    boards = Board.objects.all()
    print(boards)
    return render(request, 'home.html', {'boards': boards})


def board_topics(request, pk):
    board_list = get_object_or_404(Board, pk=pk)
    return render(request, 'topics.html', {'board': board_list})


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
            return redirect('board_topics', pk=board.pk)
    else:
        form = NewTopicForm()

    return render(request, 'new_topic.html', {'board': board, 'form': form})


def topic_posts(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    print(topic.posts.all())
    return render(request, 'topic_posts.html', {'topic': topic})

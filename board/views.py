from django.shortcuts import render, get_object_or_404, redirect
from django.http.response import HttpResponse
from .models import Board, Topic, Post
from django.contrib.auth.models import User
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


def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    user = User.objects.first()
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
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

    return render(request, 'new_topic.html', {'board': board, 'form': form })

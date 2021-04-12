# 안녕하세요 

## 도와주세요

```python
import os

from django.shortcuts import render, get_object_or_404
from django.http.response import HttpResponse
from .models import Board
from django.http import Http404


# Create your views here.
def home(request):
    boards = Board.objects.all()
    return render(request, 'home.html', {'boards': boards})


def board_topics(request, pk):
    topics = get_object_or_404(Board, pk=pk)
    return render(request, 'topics.html', {'topics': topics})
```

**하이** 


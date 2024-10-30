from django.shortcuts import render
from django.http import HttpResponse
from .models import Board

# Create your views here.

def home(request):

    boards=Board.objects.all()
    boards_names=list()

    for board in boards:
        boards_names.append(board.name)
    return render(request,'home.html',{'boards':boards})
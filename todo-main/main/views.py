from django.shortcuts import render, redirect
from .models import Todo
from .form import TodoForm


# Create your views here.
def home(request):
    items = Todo.objects.all()
    return render(request, 'home.html', {'items': items})


# About page
def about(request):
    return render(request, 'about.html', {})


# Add task
def addItem(request):
    form = TodoForm()
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    return render(request, 'add.html', {'form': form})


# Task details
def detailItem(request, pk):
    item = Todo.objects.get(id=pk)
    return render(request, 'details.html', {'item': item})


# Update task
def updateItem(request, pk):
    item = Todo.objects.get(id=pk)
    form = TodoForm(instance=item)
    if request.method == 'POST':
        form = TodoForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        return render(request, 'update.html', {'form': form})


# Delete task
def deleteItem(request, pk):
    item = Todo.objects.get(id=pk)
    item.delete()
    return redirect('home')

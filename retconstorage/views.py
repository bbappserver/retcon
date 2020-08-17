from django.shortcuts import render

# Create your views here.

def edit_collection(request):
   return render(request, 'collection-builder.html', {})
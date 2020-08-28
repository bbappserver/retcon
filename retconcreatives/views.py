from django.shortcuts import render,HttpResponse

from .forms import BulkCreateEpisodeForm

def create_placeholder_episodes(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = BulkCreateEpisodeForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            form.save(commit=True)
            return HttpResponse('OK')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = BulkCreateEpisodeForm()
   
    return render(request, 'creatives/bulkepisodes.html', {'form': form})

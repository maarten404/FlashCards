from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse ("flashcards:index"))

def register(request):
    """Register a new user."""
    if request.method != 'POST':
        # Display blank registration from.
        form = UserCreationForm()
    else:
        #Process completed form
        form = UserCreationForm(data=request.POST)

        if form.is_valid():
            new_user = form.save()
            # Log the user in and then redirect to index
            authenticated_user = authenticate(username=new_user.username,
                password=request.POST['password1'])
            login(request, authenticated_user)
            return HttpResponseRedirect(reverse('flashcards:index'))

    context = {'form': form}
    return render(request, 'users/register.html', context)
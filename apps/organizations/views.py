# Create your views here.
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
#from django.views.decorators import require_post
from .forms import OrganizationForm, UserCardForm
from .models import Organization, Membership, UserCard

@login_required
def org_new(request):
    if request.method == 'POST':
        form = OrganizationForm(request.POST, request.FILES)
        if form.is_valid():
            org = form.save()
            org.set_user_status(request.user, Membership.Status.OWNER)
            return redirect(org.get_absolute_url())
    else:
        form = OrganizationForm()
    return render(request, 'organizations/new.html', {'form': form})


def main(request, pk, tab='documents'):
    try:
        org = Organization.objects.get(pk=pk)
    except Organization.DoesNotExist:
        raise Http404

    my_status = org.get_user_status(request.user)
    am_owner = my_status == Membership.Status.OWNER
    am_member = am_owner or my_status == Membership.Status.REGULAR

    return render(request, 'organizations/main.html', {
            'org': org,
            'tab': tab,
            'my_status': my_status,
            'am_owner': am_owner,
            'am_member': am_member,
        })

def user_card(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        raise Http404
    card, created = UserCard.objects.get_or_create(pk=user.pk)
    return render(request, 'organizations/user_card.html', {
            'card': card,
        })


@login_required
def edit(request, pk):
    try:
        org = Organization.objects.get(pk=pk)
    except Organization.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = OrganizationForm(request.POST, request.FILES, instance=org)
        if form.is_valid():
            org = form.save()
            return redirect(org.get_absolute_url())
    else:
        form = OrganizationForm(instance=org)
    return render(request, 'organizations/edit.html', {'form': form})


@login_required
def user_edit(request):
    card, created = UserCard.objects.get_or_create(pk=request.user.pk)
    if request.method == 'POST':
        form = UserCardForm(request.POST, request.FILES, instance=card)
        if form.is_valid():
            card = form.save()
            return redirect(card.get_absolute_url())
    else:
        form = UserCardForm(instance=card)
    return render(request, 'organizations/edit_user.html', {'form': form})


@login_required
def join(request, pk):
    try:
        org = Organization.objects.get(pk=pk)
    except Organization.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        org.set_user_status(request.user, Membership.Status.PENDING)
        return redirect('organizations_members', org.pk)

    return render(request, 'organizations/join.html', {'org': org})

@login_required
#@POST_required
def membership(request, pk):
    try:
        org = Organization.objects.get(pk=pk)
    except Organization.DoesNotExist:
        raise Http404

    try:
        user = User.objects.get(pk=request.POST['user'])
    except KeyError, User.DoesNotExist:
        pass
    else:
        if user != request.user:
            action = request.POST.get('action')
            if action:
                if action == 'remove':
                    action = None
                org.set_user_status(user, action)
    return redirect('organizations_members', org.pk)


def organizations(request):
    return render(request, "organizations/organizations.html", {
        'organizations': Organization.objects.all(),
    })

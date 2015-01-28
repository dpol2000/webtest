# -*- coding: utf-8 -*-

import datetime
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from models import Student


def authorize(request):

    f1 = request.GET['first_name']
    f2 = request.GET['last_name']
    f3 = request.GET['photo']

#    path = request.get_full_path()
#    n1 = path.find('first_name=')
#    n2 = path.find('last_name=')
#    n_end = path.find('photo=')

#    first_name = urllib.unquote(path[n1+len('first_name='):n2-1]).decode('windows-1251').encode('utf-8')
#    last_name = urllib.unquote(path[n2+len('last_name='):n_end-1]).decode('windows-1251').encode('utf-8')

    first_name = f1 # urllib.unquote(f1).decode('windows-1251').encode('utf-8')
    last_name = f2 # urllib.unquote(f2).decode('windows-1251').encode('utf-8')
    photo = str(f3)

    fname = first_name + '_' + last_name
    if len(fname)<22:
        username = fname + '@vk.com'
    else:
        username = fname[:22] + '@vk.com'

    try:
        user = User.objects.get(username=username)

    # новый юзер
    except User.DoesNotExist:

        password = User.objects.make_random_password()
        now = datetime.datetime.now()

        user = User(
            username=username,
            email=username,
            first_name = first_name[:30],
            last_name = last_name[:30],
            is_staff=False,
            is_active=True,
            is_superuser=False,
            last_login=now,
            date_joined=now)

        user.set_password(password)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        user.save()

        student = Student(user = user, facebook_id = '123')
        student.save()


    else:
        student = Student.objects.get(user = user.id)
        if not student.photo:
            student.photo = photo
            student.save()

        user.backend = 'django.contrib.auth.backends.ModelBackend'

#    user = auth.authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            auth.login(request, user)
            return HttpResponseRedirect('/students/' + str(student.id))
        else:
            return HttpResponse('Login is invalid.')

    return HttpResponse('Login failed, user is disabled .')

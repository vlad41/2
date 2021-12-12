import io

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
# from models import Person, QueueConscripts

from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .models import QueueConscripts
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.crypto import get_random_string
from django.core.signing import BadSignature

from .utilities import signer
import sqlite3
from . import forms
from .models import PostUser
from .forms import RegisterForm


# Create your views here.
def index(request):
    return render(request, 'main/mainpage.html')


def current_query(request):
    base = {}
    queryset = QueueConscripts.objects.all()
    time = [i.time for i in queryset]
    busy = [i.busy for i in queryset]
    base['time'] = time
    base['busy'] = busy
    # base = QueueConscripts.objects.all()
    # time = QueueConscripts.time
    # time = time.objects.all()

    test = queryset.filter(department='dar').filter(week_day='tu')

    return render(request, "main/current_query.html", {'time': time, 'busy': busy})


#
# def register(request):
#     if request.method == 'POST':
#         form_reg = RegisterForm(request.POST)
#         if form_reg.is_valid():
#             form_reg.save()
#             email = form_reg.cleaned_data['email']
#             name = form_reg.cleaned_data['name']
#             msg_html = render_to_string('authorization/msg.html', {'name': name})
#             mail = send_mail('Ви зареєстровані на сайті', 'Вітаємо, Ваші дані у нас!', 'test1mysite@gmail.com',
#                              [email], fail_silently=False)
#             if mail:
#                 messages.success(request, 'Вы успешно зарегистрировались, Вам отправлено письмо для активации аккаунта')
#             else:
#                 messages.error(request, 'Ошибка отправки')
#         else:
#             messages.error(request, 'Ошибка регистрации')
#     else:
#         form_reg = RegisterForm()
#     return render(request, 'registration/register.html', {"form_reg": form_reg})


class RegisterUserView(CreateView):
    model = PostUser
    template_name = 'registration/register_user.html'
    form_class = forms.RegisterForm
    success_url = reverse_lazy('main:login')


def generate_api_token():
    """token to access api info
    if token already exists, try again"""
    token = get_random_string(length=32)
    if PostUser.objects.filter(api_token=token):
        generate_api_token()
    else:
        return token


def user_activate(request, sign):
    # solved test this
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'errors/bad_signature.html')
    user = get_object_or_404(PostUser, username=username)
    if user.is_activated:
        template = 'registration/user_is_activated.html'
    else:
        template = 'registration/activation_done.html'
        user.is_active = True
        user.is_activated = True
        user.api_token = generate_api_token()
        print(f'token: {user.api_token}')
        user.save()
    return render(request, template)


# region login
class UserLoginView(LoginView):
    template_name = 'login/login.html'


class UserLogoutView(LoginRequiredMixin, LogoutView):
    template_name = login = 'login/logout.html'


# p
def profile_posts(request):

    # todo Save local area and day
    f = open("temp.txt", "r")
    read = f.read()
    if not read:
        f = open("temp.txt", "w")
        f.write("dar tu")
    f.close()
    f = open("temp.txt", "r")
    temp_area_day = f.read().split(" ")
    f.close()

    area = request.POST.getlist("area") or [temp_area_day[0]]
    day = request.POST.getlist("day") or [temp_area_day[1]]

    f = open("temp.txt", "w")
    f.write(area[0] + " " + day[0])





    add_time = request.POST.getlist("add_time")
    remove_time = request.POST.getlist("remove_time")

    print(add_time, remove_time, area, day)
    username = None
    people_id = None

    if request.user.is_authenticated:
        username = request.user.username
        people_id = request.user.id

    alltime = ['09:00', '09:15', '09:30', '09:45',
               '10:00', '10:15', '10:30', '10:45',
               '11:00', '11:15', '11:30', '11:45',
               '12:00', '12:15', '12:30', '12:45',
               '13:00']

    def get_filtered_queue():
        return list(QueueConscripts.objects.filter(week_day=day[0], department=area[0]).all())

    def get_converted_list(raw_queue):
        busy_times = [rq.time for rq in raw_queue]

        queueList = []
        for time in alltime:
            isBusy = "Вільно"
            user = ''
            if time in busy_times:
                isBusy = "Зайнято"
                user = ''
                for queue in raw_queue:
                    if queue.time == time:
                        user = queue.people

            anItem = dict(time=time, isBusy=isBusy, user=user)
            queueList.append(anItem)

        return queueList

    raw_queue = get_filtered_queue();
    busy_times = get_converted_list(raw_queue)
    print(raw_queue)

    people_in_queue_times = 0
    for i in raw_queue:
        if i.people_id == people_id:
            people_in_queue_times +=1

    if add_time != []:
        for time in busy_times:
            if add_time[0] == time["time"] and time["isBusy"] == 'Вільно' and people_in_queue_times <= 1 :

                QueueConscripts.objects.create(week_day=day[0], department=area[0], time=add_time[0], people=PostUser.objects.filter(id=people_id).first(), busy="Зайнято")


    if remove_time != []:
        postUser = PostUser.objects.filter(id=people_id).first()
        for time in busy_times:
            if remove_time[0] == time["time"] and time["isBusy"] == 'Зайнято' and time["user"] == postUser:
                temp = QueueConscripts.objects.filter(week_day=day[0], department=area[0], time=remove_time[0],
                                               people=postUser).first()

                if temp != None:
                    QueueConscripts.objects.filter(pk=temp.id).delete()

    table = get_converted_list(get_filtered_queue())
    context = {'queryList': table, 'day': day, 'area': area, 'times': alltime, 'surname': username}
    return render(request, 'main/current_query.html', context)


# region api_token
@login_required
def api_token(request):
    return render(request, 'main/profile_api_key.html')


def index(request):
    return render(request, 'main/current_query.html')

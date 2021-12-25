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

from django.contrib import messages


# Create your views here.
def mainpage(request):
    messages.add_message(request, messages.SUCCESS, 'СООБЩЕние')
    return render(request, 'main/mainpage.html', {'current_path': request.path})


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
        username = request.user.username # username текущего пользователя
        people_id = request.user.id # id текущего пользователя (для получения его email)

    alltime = ['09:00', '09:15', '09:30', '09:45',
               '10:00', '10:15', '10:30', '10:45',
               '11:00', '11:15', '11:30', '11:45',
               '12:00', '12:15', '12:30', '12:45',
               '13:00']

    if str(request.user) == "AnonymousUser":
        current_user_fio = []
    else:
        current_user_fio = [request.user.name, request.user.surname, request.user.fname]

    # Возвращает данные из таблицы для всех очередей
    def get_all_queues():
        return list(QueueConscripts.objects.all())

    # Возвращает текущие данные из таблицы для выбранной очереди
    def get_filtered_queue():
        return list(QueueConscripts.objects.filter(week_day=day[0], department=area[0]).all())

    # Возвращает конвертированный список для текущей очереди, который мы уже можем использовать
    def get_converted_list(raw_queue):
        busy_times = [rq.time for rq in raw_queue] # Из текущей очереди отбираем занятое время

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

    raw_queue = get_all_queues() # Текущие данные из таблицы для всех очередей
    busy_times = get_converted_list(raw_queue) # Конвертированный список для всех очередей, который мы уже можем использовать
    print("Текущие данные из таблицы для всех очередей: ", raw_queue, "\n")

    people_in_queue_times = 0 # Сколько пользователей с текущим именем уже записаны в очередь
    for i in raw_queue:
        if i.people_id == people_id:
            people_in_queue_times += 1

    if add_time != []:
        if people_in_queue_times > 0:
            print('Ви вже записані у чергу! Ваша черга: ', add_time[0])
        else:
            print(add_time)
            for time in busy_times:
                if add_time[0] == time["time"] and time["isBusy"] == 'Зайнято':
                    print('Це місце вже зайнято! Оберіть інше.')

                if add_time[0] == time["time"] and time["isBusy"] == 'Вільно' and people_in_queue_times < 1:
                    QueueConscripts.objects.create(week_day=day[0], department=area[0], time=add_time[0], people=PostUser.objects.filter(id=people_id).first(), busy="Зайнято")


    if remove_time != []:
        postUser = PostUser.objects.filter(id=people_id).first()
        print('postUser: ', postUser)
        for time in busy_times:
            if remove_time[0] == time["time"] and time["isBusy"] == 'Зайнято' and time["user"] == postUser:
                temp = QueueConscripts.objects.filter(week_day=day[0], department=area[0], time=remove_time[0], people=postUser).first()

                if temp != None:
                    QueueConscripts.objects.filter(pk=temp.id).delete()

    table = get_converted_list(get_filtered_queue())

    current_user_queue = list(QueueConscripts.objects.filter(people=people_id).all())
    if not current_user_queue:  # Если пользователь не записан в очередь - True
        print("current_user_queue:", current_user_queue)  # Пользователь не в очереди
        current_user_queue = ''
    else:
        print("current_user_queue:", current_user_queue[0])  # Текущая очередь пользователя
        current_user_queue = str(current_user_queue[0]).split(' ')

    context = {'queryList': table, 'day': day[0], 'area': area[0], 'times': alltime,
               'username': username, 'current_user_queue': current_user_queue, 'current_user_fio': current_user_fio}
    return render(request, 'main/current_query.html', context)


# region api_token
@login_required
def api_token(request):
    return render(request, 'main/profile_api_key.html')


def index(request):
    return render(request, 'main/current_query.html')

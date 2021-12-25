from django import forms
from django.contrib.auth import password_validation
from .apps import user_registered
from django import forms
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
from .models import PostUser, QueueConscripts
from phonenumber_field.modelfields import PhoneNumberField

class RegisterForm(UserCreationForm):
    passport = forms.CharField(label='Паспорт',
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Паспорт'}))
    name = forms.CharField(label='Ім\'я',
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ім\'я'}))
    surname = forms.CharField(label='Прізвище',
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Прізвище'}))
    fname = forms.CharField(label='По-батькові',
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'По-батькові'}))
    phoneNumber = forms.RegexField(label='Номер телефону',
                                   widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Номер телефону'}),
                                   regex=r'^\+?1?\d{9,15}$')
    email = forms.EmailField(label='E-mail',
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-mail'}))
    age = forms.IntegerField(label='Вік')
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Пароль'}))
    password2 = forms.CharField(label='Повторіть пароль', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Пароль'}))

    is_active = False

    def clean(self):
        """
        По умолчанию в модели User поле email не является уникальным,
        в случае совпадения функция очищает поле и добавляет к сообщениям
        об ошибках новую строку. exists() возвращает True, если QuerySet
        содержит какие-либо результаты, и False, если нет.
        """
        cleaned_data = super().clean()
        if PostUser.objects.filter(email=cleaned_data.get('email')).exists():
            self.add_error('email', 'така пошта вже зареєстрована')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = True
        user.is_activated = True
        if commit:
            user.save()
            # solved email send activation letter
        # user_registered.send(RegisterForm, instance=user)
        return user

    class Meta:
        model = PostUser
        fields = ('passport', 'name', 'surname', 'fname', 'phoneNumber', 'email', 'age', 'password1', 'password2')


class Queue(forms.ModelForm):
    class Meta:
        model = QueueConscripts
        fields = '__all__'
        widgets = {'author': forms.HiddenInput}

from django import forms
from django.contrib.auth import password_validation
from .apps import user_registered
from django import forms
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
from .models import PostUser, QueueConscripts
from phonenumber_field.modelfields import PhoneNumberField


class RegisterForm(UserCreationForm):
    passport = forms.CharField(label='passport',
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your passport *'}))
    username = forms.CharField(label='username',
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your name *'}))
    surname = forms.CharField(label='surname',
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your surname *'}))
    fname = forms.CharField(label='fname',
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your frame *'}))
    phoneNumber = PhoneNumberField()
    email = forms.EmailField(label='E-mail',
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your email *'}))
    age = forms.IntegerField()
    password1 = forms.CharField(label='password1', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Your password *'}))
    password2 = forms.CharField(label='password2', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Your password *'}))

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
            self.add_error('email', 'такая почта уже зарегистрирована')
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
        fields = ('passport', 'username', 'surname', 'fname', 'phoneNumber', 'email', 'age', 'password1', 'password2',
                  'is_active')


class Queue(forms.ModelForm):
    class Meta:
        model = QueueConscripts
        fields = '__all__'
        widgets = {'author': forms.HiddenInput}

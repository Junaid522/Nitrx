from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'name': "uname", 'class': 'fadeIn second', 'placeholder': 'User Name'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'name': "psw", 'class': 'fadeIn third', 'placeholder': 'Password'}))

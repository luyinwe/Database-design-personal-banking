from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.template import RequestContext
from django import forms
from .models import user as User
from .models import account

# form
class UserForm(forms.Form):
    username = forms.CharField(label='Username',max_length=100)
    password = forms.CharField(label='Password',widget=forms.PasswordInput())
    name = forms.CharField(label='Name',max_length=100)
    address = forms.CharField(label='Address',max_length=100)
    ssn = forms.CharField(label = 'ssn', max_length = 18)

class UserFormLogin(forms.Form):
    username = forms.CharField(label='Username',max_length=100)
    password = forms.CharField(label='Password',widget=forms.PasswordInput())

#register
def regist(req):
    if req.method == 'POST':
        uf = UserForm(req.POST)
        if uf.is_valid():
            #get form data
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
            name = uf.cleaned_data['name']
            address = uf.cleaned_data['address']
            ssn = uf.cleaned_data['ssn']
            #add to database
            User.objects.create(username= username,password=password, Name = name, residential_address = address, ssn = ssn)
            response = HttpResponseRedirect('/index/')
            response.set_cookie('username', username, 3600)
            return response
    else:
        uf = UserForm()
    return render(req, 'regist.html',{'uf':uf})

#login
def login(req):
    if req.method == 'POST':
        uf = UserFormLogin(req.POST)
        if uf.is_valid():
            #get username and password from cookie
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
            #compare the data with the database
            user = User.objects.filter(username = username,password = password)
            if user:
                response = HttpResponseRedirect('/index/')
                #write username to cookie
                response.set_cookie('username',username,3600)
                return response
            else:
                #failed, go to login
                return render(req, 'login.html',{
                    'error_message': ' Login Failed! Enter the username and password correctly',
                    'uf':uf,
                } )
                # return HttpResponseRedirect('/login/')
    else:
        uf = UserFormLogin()
    return render(req, 'login.html',{'uf':uf})

def user_account(req):

    pass
#register successful
def user_account_regist(req):
    pass

def index(req):
    username = req.COOKIES.get('username','')
    try:
        acc = account.objects.get(username=username)
        text = "Your account:"
        href = "http://localhost:8000/account/"
        acc_no = acc.account_number

        return render(req, 'index.html' ,{'username':username, 'text':text, 'href':href, 'account_no':acc_no,})
    except:
        text = "You don't have an account now."
        href = "http://localhost:8000/account_regist/"
        return render(req,'index.html', {'username':username,'text':text,'href':href, 'account_no': 'Apply for one!' })

#log out
def logout(req):
    response = HttpResponse('logout !!')
    #clear username kept in the form
    response.delete_cookie('username')
    return response
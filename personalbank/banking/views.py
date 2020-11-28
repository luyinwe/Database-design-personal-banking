from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.template import RequestContext
from django import forms
from .models import user as User
from .models import account, transaction, operator,loan
import time
from faker import Faker
import numpy.random as random

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

class UserFormTransact(forms.Form):
    amount = forms.FloatField(label = 'Amount')
    choicelist = (('Alcoholic', 'Alcoholic'),
               ('Snacks', 'Snacks'),
               ('Health & Wellness', 'Health & Wellness'),
               ('Household Items', 'Household Items'),
               ('Entertainment', 'Entertainment'),
               ('Beverages', 'Beverages'),
               ('Beauty', 'Others'))
    purpose = forms.TypedChoiceField(choices = choicelist)
    payee_account_no = forms.CharField(max_length = 15)

class UserFormAccount(forms.Form):
    balance = forms.FloatField(label = 'Initial balance')

# functions
# register
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
    username = req.COOKIES.get('username','')
    acc = account.objects.filter(username = username)
    return render(req, 'account.html', {'account':acc})

#register successful
def user_account_regist(req):
    if req.method == 'POST':
        uf = UserFormAccount(req.POST)
        if uf.is_valid():
            fake = Faker()
            while(1):
                account_no = fake.credit_card_number(card_type = None)
                if not account.objects.filter(account_number = account_no).exists():
                    break
            username = req.COOKIES.get('username', '')
            state = 'pending'
            balance = uf.cleaned_data['balance']
            rating = 'initial'
            operator_list = operator.objects.all()
            account.objects.create(account_number = account_no, username = User.objects.get(username = username),
                                    state = state, operator_name = random.choice(operator_list),
                                   balance = balance, rating = rating)
            return render(req, 'account_application.html', {'uf': uf, 'error_message': "account successfully created"})

    else:
        uf = UserFormAccount()
        return render(req, 'account_application.html', {'uf': uf})

class UserLoanForm(forms.Form):
    amount = forms.FloatField(label = "Loan Amount")

def loan_app(req):
    if req.method == 'POST':
        uf = UserLoanForm(req.POST)
        if uf.is_valid():
            username = req.COOKIES.get('username', '')
            account_no = account.objects.get(username=username)
            if account_no.state != 'successful':
                return render(req, 'loan.html', {
                    'error_message': 'Your account is not valid!',
                    'uf': uf,
                })
            loan_app_no = loan.objects.count()
            amount = uf.cleaned_data['amount']
            state = 'pending'
            operator_list = operator.objects.all()
            due_date = time.strftime('%Y-%m-%d %H:%m:%S', time.localtime(time.time()))
            loan.objects.create(loan_application_number = loan_app_no,
                               amount = amount,
                               state = state,
                               account_number = account_no,
                               operator_name = random.choice(operator_list),
                               due_date = due_date)
            return render(req, 'loan.html', {
                'error_message': 'Successfully submit loan application!',
                'uf': uf,
            })
    else:
        uf = UserLoanForm()
        return render(req, 'loan.html', {
                    'error_message':  '',
                    'uf': uf,
                })

def transact(req):
    if req.method == 'POST':
        uf = UserFormTransact(req.POST)
        if uf.is_valid():
            username = req.COOKIES.get('username', '')
            payer_account_no = account.objects.get(username=username)
            if payer_account_no.state != 'successful':
                return render(req, 'transaction.html', {
                    'error_message': 'Your account is not valid!',
                    'uf': uf,
                })
            balance = payer_account_no.balance
            amount = uf.cleaned_data['amount']
            if amount>balance:
                return render(req, 'transaction.html', {
                    'error_message': ' Transact Failed! Enter a smaller amount!',
                    'uf': uf,
                })
            else:
                try:
                    payee_account_no = uf.cleaned_data['payee_account_no']
                    # check whether the payee exist or not
                    payee_existance = account.objects.get(account_number = payee_account_no)
                    # get payee's balance
                    payee_balance = payee_existance.balance
                    account.objects.filter(account_number = payee_account_no).update(balance = payee_balance+amount)

                    transaction_no = transaction.objects.count()
                    transaction_date = time.strftime('%Y-%m-%d %H:%m:%S', time.localtime(time.time()))

                    account.objects.filter(username=username).update(balance = balance - amount)
                    purpose = uf.cleaned_data['purpose']

                    transaction.objects.create(transaction_no = transaction_no,
                                               transaction_date = transaction_date,
                                               amount = amount,
                                               purpose = purpose,
                                               payer_account_no = payer_account_no,
                                               payee_account_no = payee_existance)

                    return render(req, 'transaction.html', {
                        'error_message': 'transaction success!',
                        'uf': uf,
                    })
                except Exception as e:
                    print(e)
                    return render(req, 'transaction.html', {
                        'error_message': 'Payee doesn\'t exist!',
                        'uf': uf,
                    })
    else:
        uf = UserFormTransact()
        return render(req, 'transaction.html', {'uf': uf})




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
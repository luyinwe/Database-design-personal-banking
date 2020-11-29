from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.template import RequestContext
from django import forms
from .models import user as User
from .models import account, transaction, operator, loan, wire_transfer
import time
from faker import Faker
import numpy.random as random
from alpha_vantage.foreignexchange import ForeignExchange

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
    purpose = forms.TypedChoiceField(choices = choicelist,label = 'purpose')
    payee_account_no = forms.CharField(max_length = 15)

class UserFormAccount(forms.Form):
    balance = forms.FloatField(label = 'Initial balance')

class UserLoanForm(forms.Form):
    amount = forms.FloatField(label = "Loan Amount")

class UserFormWireTransfer(forms.Form):
    choicelist = (('AUD','AUD'),('BRL','BRL'),('BGN','BGN'),('CAD','CAD'),('CNY','CNY'),('HRK','HRK'),
                  ('CYP','CYP'),('CZK','CZK'),('DKK','DKK'),('EEK','EEK'),('EUR','EUR'),('HKD','HKD'),
                  ('HKD','HKD'),('HUF','HUF'),('ISK','ISK'),('IDR','IDR'),('JPY','JPY'),('KRW','KRW'),
                  ('LVL','LVL'),('LTL','LTL'),('MYR','MYR'),('PLN','PLN'),('RON','RON'),('MTL','MTL'),
                  ('NZD','NZD'),('NOK','NOK'),('PHP','PHP'),('RUB','RUB'),('SGD','SGD'),('SKK','SKK'),
                  ('SEK','SEK'),('THB','THB'),('TRY','TRY'),('USD','USD'),('GBP','GBP'),('CHF','CHF'),
                  ('ZAR','ZAR'),('SIT','SIT'))
    currency_type = forms.TypedChoiceField(choices = choicelist,label = 'Currency_type')
    amount = forms.FloatField(label = 'Amount')
    payee_name = forms.CharField(label = 'Payee\'s name', max_length = 100)
    payee_bank_name = forms.CharField(label = 'Payee\'s bank name', max_length = 100)
    payee_account_no = forms.CharField(label = 'Payee\'s account number', max_length = 50)
    payee_swift_code = forms.CharField(label = 'Payee\'s swift code', max_length = 100)

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
            loan_hist = loan.objects.filter(account_number = account_no)
            return render(req, 'loan.html', {
                'error_message': 'Successfully submit loan application!',
                'uf': uf,
                'loan_hist':loan_hist,
            })
    else:
        uf = UserLoanForm()
        username = req.COOKIES.get('username','')
        acc = account.objects.filter(username = username)
        try:
            loan_hist = loan.objects.filter(account_number__in = acc)
        except Exception as e:
            print(e)
            loan_hist = ''
        return render(req, 'loan.html', {
                    'error_message':  '',
                    'uf': uf,
                    'loan_hist': loan_hist,
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



def wire_trans(req):
    if req.method == 'POST':
        uf = UserFormWireTransfer(req.POST)
        if uf.is_valid():
            username = req.COOKIES.get('username', '')
            payer_account_no = account.objects.get(username=username)
            if payer_account_no.state != 'successful':
                return render(req, 'loan.html', {
                    'error_message': 'Your account is not valid!',
                    'uf': uf,
                })
            balance = payer_account_no.balance
            currency_type = uf.cleaned_data['currency_type']
            amount = uf.cleaned_data['amount']
            rate = get_exchange_rate('USD',currency_type)
            amount_in_USD = amount/float(rate)
            if amount_in_USD>balance:
                return render(req, 'wire_transfer.html', {
                    'error_message': ' Operation Failed! Enter a smaller amount!',
                    'uf': uf,
                })
            else:
                wt_no = wire_transfer.objects.count()
                date = time.strftime('%Y-%m-%d %H:%m:%S', time.localtime(time.time()))
                state = 'pending'
                operator_list = operator.objects.all()
                wire_transfer.objects.create(wt_transaction_no = wt_no,
                                             date = date,
                                             currency_type = currency_type,
                                             amount = amount_in_USD,
                                             account_number = payer_account_no,
                                             state = state,
                                             operator_name = random.choice(operator_list),
                                             payee_name=uf.cleaned_data['payee_name'],
                                             payee_bank_name = uf.cleaned_data['payee_bank_name'],
                                             payee_account_no = uf.cleaned_data['payee_account_no'],
                                             payee_swift_code = uf.cleaned_data['payee_swift_code'])
                return render(req, 'wire_transfer.html', {
                    'error_message': 'Operation Success! Needs to be handled by the operator. ' ,
                    'uf': uf,
                })
    else:
        uf = UserFormWireTransfer()
        return render(req, 'wire_transfer.html',{'uf':uf})
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

# other function
def get_exchange_rate(f, t):
    cc = ForeignExchange('MGFW88UHCJKCUEA8')
    data, _ = cc.get_currency_exchange_rate(f, t)
    rate = data['5. Exchange Rate']
    return rate

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
from django.utils import timezone
import datetime
from django.db.models import Sum


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
    payee_account_no = forms.CharField(max_length = 100)

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
                response.set_cookie('username',username,36000)
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
            date = time.strftime('%Y-%m-%d %H:%m:%S', time.localtime(time.time()))
            operator_list = operator.objects.all()
            loan.objects.create(loan_application_number = loan_app_no,
                               amount = amount,
                               state = state,
                               date = date,
                               account_number = account_no,
                               operator_name = random.choice(operator_list),
                               )
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
    username = req.COOKIES.get('username', '')
    acc = account.objects.filter(username=username)
    trans_hist = transaction.objects.filter(payer_account_no__in=acc)

    if req.method == 'POST':
        uf = UserFormTransact(req.POST)
        if uf.is_valid():
            acc = account.objects.get(username = username)
            if acc.state != 'successful':
                return render(req, 'transaction.html', {
                    'error_message': 'Your account is not valid!',
                    'uf': uf,
                    'transact': trans_hist
                })
            balance = acc.balance
            amount = uf.cleaned_data['amount']
            if amount>balance:
                return render(req, 'transaction.html', {
                    'error_message': ' Transact Failed! Enter a smaller amount!',
                    'uf': uf,
                    'transact':trans_hist
                })
            else:
                try:
                    payee_no = uf.cleaned_data['payee_account_no']
                    # check whether the payee exist or not
                    payee_existance = account.objects.get(account_number = payee_no)
                    # get payee's balance
                    payee_balance = payee_existance.balance
                    account.objects.filter(account_number = payee_no).update(balance = payee_balance+amount)

                    transaction_no = transaction.objects.count()
                    transaction_date = time.strftime('%Y-%m-%d %H:%m:%S', time.localtime(time.time()))

                    account.objects.filter(username=username).update(balance = balance - amount)
                    purpose = uf.cleaned_data['purpose']

                    transaction.objects.create(transaction_no = transaction_no,
                                               transaction_date = transaction_date,
                                               amount = amount,
                                               purpose = purpose,
                                               payer_account_no = acc,
                                               payee_account_no = payee_existance)

                    return render(req, 'transaction.html', {
                        'error_message': 'transaction success!',
                        'uf': uf,
                        'transact': trans_hist
                    })
                except Exception as e:
                    print(e)
                    return render(req, 'transaction.html', {
                        'error_message': 'Payee doesn\'t exist!',
                        'uf': uf,
                        'transact':trans_hist
                    })
    else:
        uf = UserFormTransact()
        return render(req, 'transaction.html', {'uf': uf,'transact':trans_hist})

class searchTransForm(forms.Form):
    transact_no = forms.CharField(label = 'transaction no', required = False, empty_value = None)
    payee_no = forms.CharField(label = 'payee\' account no', required = False, empty_value = None)
    purpose_choice = (('None','None'),('Alcoholic', 'Alcoholic'),
               ('Snacks', 'Snacks'),
               ('Health & Wellness', 'Health & Wellness'),
               ('Household Items', 'Household Items'),
               ('Entertainment', 'Entertainment'),
               ('Beverages', 'Beverages'),
               ('Beauty', 'Beauty'))
    purpose = forms.TypedChoiceField(choices = purpose_choice)
    from_date = forms.DateTimeField(label = 'Date from', widget = forms.DateInput(attrs = {'type':'date'}), required = False)
    to_date = forms.DateTimeField(label = 'Date to', widget = forms.DateInput(attrs = {'type':'date'}), required = False)


def search_transaction(req):
    username = req.COOKIES.get('username','')
    acc = account.objects.filter(username = username)
    trans_hist = transaction.objects.filter(payer_account_no__in = acc)
    transact_sum = transaction.objects.filter(payer_account_no__in=acc).aggregate(Sum('amount'))
    if req.method == 'POST':
        uf = searchTransForm(req.POST)
        if uf.is_valid():
            transaction_no = uf.cleaned_data['transact_no']
            if transaction_no is not None:
                trans_hist = trans_hist.filter(transaction_no = transaction_no)
            payee_no = uf.cleaned_data['payee_no']
            if payee_no is not None:
                acc = account.objects.filter(account_number=payee_no)
                if not acc:
                    return render(req, 'transaction_history.html',
                                  {'transact': trans_hist, 'uf': uf, 'error_message': 'The payee doesn\'t exist!'})

                trans_hist = trans_hist.filter(payee_account_no__in = acc)
            purpose = uf.cleaned_data['purpose']
            if purpose != 'None':
                trans_hist = trans_hist.filter(purpose = purpose)
            from_date = uf.cleaned_data['from_date']
            if from_date is not None:
                trans_hist = trans_hist.filter(transaction_date__gte = from_date)
            to_date = uf.cleaned_data['to_date']
            if to_date is not None:
                trans_hist = trans_hist.filter(transaction_date__lt = to_date)
            transact_sum = trans_hist.aggregate(Sum('amount'))
            return render(req, 'transaction_history.html', {'transact': trans_hist, 'uf': uf,'amount_sum':transact_sum['amount__sum']})
    else:
        uf = searchTransForm()
        return render(req,'transaction_history.html',{'transact': trans_hist,'amount_sum':transact_sum['amount__sum'],'uf':uf,})


def wire_trans(req):
    username = req.COOKIES.get('username', '')
    acc = account.objects.filter(username = username)
    wt_hist = wire_transfer.objects.filter(account_number__in = acc)
    if req.method == 'POST':
        uf = UserFormWireTransfer(req.POST)
        if uf.is_valid():

            payer_account_no = account.objects.get(username=username)
            if payer_account_no.state != 'successful':
                return render(req, 'loan.html', {
                    'error_message': 'Your account is not valid!',
                    'uf': uf,
                    'wt_hist':wt_hist
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
                    'wt_hist':wt_hist
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
                    'wt_hist':wt_hist
                })
    else:
        uf = UserFormWireTransfer()
        return render(req, 'wire_transfer.html',{'uf':uf,'wt_hist':wt_hist})


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

## operator form
class OperatorAccountForm(forms.Form):
    acc_no = forms.CharField(label = 'account number')
    choicelist = (('successful','successful'),('failed','failed'))
    state = forms.TypedChoiceField(choices = choicelist)
    rating_list = (('initial','initial'),('good','good'),
                   ('very good','very good'),('excellent','excellent'),
                   ('VIP','VIP'))
    rating = forms.TypedChoiceField(choices = rating_list)

class OperatorLoanForm(forms.Form):
    loan_no = forms.CharField(label = 'loan application number')
    choicelist = (('successful','successful'),('failed','failed'))
    state = forms.TypedChoiceField(choices = choicelist)
    due_date = forms.DateTimeField(label = 'Due Date(YYYY-MM-DD HH:MM:SS)')

class OperatorWTForm(forms.Form):
    wt_no = forms.CharField(label = 'wire transfer application number')
    choicelist = (('successful','successful'),('failed','failed'))
    state = forms.TypedChoiceField(choices = choicelist)

## operator function
def operatorLogin(req):
    if req.method == 'POST':
        uf = UserFormLogin(req.POST)
        if uf.is_valid():
            #get username and password from cookie
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
            #compare the data with the database
            op = operator.objects.filter(username = username,password = password)
            if op:
                response = HttpResponseRedirect('/operatorAccount/')
                #write username to cookie
                response.set_cookie('username',username,3600)
                return response
            else:
                #failed, go to login
                return render(req, 'operatorLogin.html',{
                    'error_message': ' Login Failed! Enter the username and password correctly',
                    'uf':uf,
                } )
                # return HttpResponseRedirect('/login/')
    else:
        uf = UserFormLogin()
        return render(req, 'operatorLogin.html',{'uf':uf})

def operatorAccount(req):
    username = req.COOKIES.get('username','')
    return render(req,'operatorAccount.html',{'username':username})

def operatorAccountProcess(req):
    username = req.COOKIES.get('username','')
    op = operator.objects.filter(username = username)
    account_list = account.objects.filter(operator_name__in = op, state = 'pending')

    if req.method == 'POST':
        uf = OperatorAccountForm(req.POST)
        if uf.is_valid():
            acc_no = uf.cleaned_data['acc_no']
            state = uf.cleaned_data['state']
            rating = uf.cleaned_data['rating']
            account.objects.filter(account_number = acc_no).update(state = state, rating = rating)
            return render(req, 'process_account_application.html',{'account':account_list,'error_message':'successfully operated!','uf':uf})

    else:
        uf = OperatorAccountForm()
        return render(req, 'process_account_application.html', {'account': account_list,'uf':uf})

def evaluate_credit(req):

    username = req.COOKIES.get('username','')
    op = operator.objects.filter(username = username)
    account_list = account.objects.filter(operator_name__in = op, state = 'successful')
    if req.method == 'POST':
        for acc in account_list:
            flow = 0
            # startdate = timezone.now() - datetime.timedelta(days=180)
            payer_flow = transaction.objects.filter(payer_account_no = acc)
            payee_flow = transaction.objects.filter(payee_account_no = acc)
            loan_flow = loan.objects.filter(account_number = acc, state = 'successful')
            wt_flow = wire_transfer.objects.filter(account_number = acc, state = 'successful')
            for payer in payer_flow:
                flow += payer.amount
            for payee in payee_flow:
                flow += payee.amount
            for loan_f in loan_flow:
                flow += loan_f.amount
            for wt in wt_flow:
                flow += wt.amount
            if flow< 1e4:
                account.objects.filter(account_number = acc.account_number).update(rating = 'initial')
            elif flow<1e5:
                account.objects.filter(account_number=acc.account_number).update(rating='good')
            elif flow<1e6:
                account.objects.filter(account_number = acc.account_number).update(rating = 'very good')
            elif flow<1e7:
                account.objects.filter(account_number = acc.account_number).update(rating = 'excellent')
            else:
                account.objects.filter(account_number = acc.account_number).update(rating = 'VIP')
    account_list = account.objects.filter(operator_name__in=op, state='successful')
    return render(req, 'evaluate_credit.html',{'account':account_list})

def operatorLoanProcess(req):
    username = req.COOKIES.get('username', '')
    op = operator.objects.filter(username=username)
    loan_list = loan.objects.filter(operator_name__in=op, state='pending')
    rate = []
    for lo in loan_list:
        rate.append(account.objects.get(account_number = lo.account_number_id).rating)

    if req.method == 'POST':
        uf = OperatorLoanForm(req.POST)
        if uf.is_valid():
            loan_no = uf.cleaned_data['loan_no']
            state = uf.cleaned_data['state']
            due_date = uf.cleaned_data['due_date']
            if state == 'successful':
                acc_no = loan.objects.get(loan_application_number = loan_no).account_number_id
                balance = account.objects.get(account_number = acc_no).balance
                loan_amount = loan.objects.get(loan_application_number = loan_no).amount
                account.objects.filter(account_number = acc_no).update(balance = balance + loan_amount)
            loan.objects.filter(loan_application_number = loan_no).update(state = state, due_date = due_date)
            loan_list = loan.objects.filter(operator_name__in = op, state = 'pending')
            rate = []
            for lo in loan_list:
                rate.append(account.objects.get(account_number = lo.account_number_id).rating)
            return render(req, 'process_loan_application.html',{'loan_list':loan_list,'uf':uf, 'error_message':'successfully operated!','rate':rate})

    else:
        uf = OperatorLoanForm()
        return render(req, 'process_loan_application.html', {'loan_list': loan_list,'uf':uf,'rate':rate})

# TODO
# the rating should based on the transaction flow. when the transaction flow is smaller than 10^4, initial, 10^5, 10^6, 10^7, 10^8
# also needs to consider about how to decide the state(why the operator agree with the loan)


def operatorWTProcess(req):
    username = req.COOKIES.get('username', '')
    op = operator.objects.filter(username=username)
    wt_list = wire_transfer.objects.filter(operator_name__in=op, state='pending')
    if req.method == 'POST':
        uf = OperatorWTForm(req.POST)
        if uf.is_valid():
            wt_no = uf.cleaned_data['wt_no']
            state = uf.cleaned_data['state']
            if state == 'successful':
                acc_no = wire_transfer.objects.get(wt_transaction_no = wt_no).account_number_id
                balance = account.objects.get(account_number = acc_no).balance
                wt_amount = wire_transfer.objects.get(wt_transaction_no = wt_no).amount
                if wt_amount<balance:
                    account.objects.filter(account_number = acc_no).update(balance = balance - wt_amount)
                    wire_transfer.objects.filter(wt_transaction_no = wt_no).update(state = state)
                    return render(req, 'process_wt_application.html',{'wire_transact': wt_list,'uf':uf, 'error_message':'successfully operated!'})
                else:
                    return render(req, 'process_wt_application.html',
                                  {'wire_transact': wt_list, 'uf': uf, 'error_message': 'Can not choose successful, because the user doesn\'t have enough balance in his or her account!' })
            else:
                wire_transfer.objects.filter(wt_transaction_no=wt_no).update(state=state)
                return render(req, 'process_wt_application.html',
                              {'wire_transact': wt_list, 'uf': uf, 'error_message': 'successfully operated!'})

    else:
        uf = OperatorWTForm()
        return render(req, 'process_wt_application.html', {'wire_transact': wt_list,'uf':uf})

def logout(req):
    response = HttpResponseRedirect('/login/')
    #clear username kept in the form
    response.delete_cookie('username')
    return response
# other function

def get_exchange_rate(f, t):
    cc = ForeignExchange('MGFW88UHCJKCUEA8')
    data, _ = cc.get_currency_exchange_rate(f, t)
    rate = data['5. Exchange Rate']
    return rate

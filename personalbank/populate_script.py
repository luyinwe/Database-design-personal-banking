import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE","personalbank.settings")
django.setup()

from faker import Faker
from banking.models import *
import numpy.random as random
# have models like operator, user, account, loan, wire_transfer, transaction

N = 1000
def create_user(N, operator_name_list):
    record_username = {}
    fake = Faker()
    for _ in range(N):
        try:
            username = fake.user_name()
            pwd = fake.password(length = random.randint(8,20))
            name = fake.name()
            address = fake.address()
            identity = fake.ssn()
            user.objects.create(username = username,
                                password = pwd,
                                Name = name,
                                residential_address = address,
                                ssn = identity
                                )

            account_no = fake.credit_card_number(card_type = None)
            operator_name = random.choice(operator_name_list)
            balance = round(random.rand()*1e6,2)
            rating = random.choice(['initial','good','very good','excellent','VIP'])
            account.objects.create(account_number =account_no,
                                   username = user.objects.get(username = username),
                                   state = 'successful',
                                   operator_name = operator.objects.get(username = operator_name),
                                   balance = balance,
                                   rating = rating
            )
            record_username[username] = account_no
        except:
            continue
    return record_username

def create_operator(N=5):
    fake = Faker()
    operator_username = []
    for _ in range(N):
        username = fake.user_name()
        operator_username.append(username)
        pwd = fake.password(length = random.randint(8,20))
        name = fake.name()
        operator.objects.create(username=username,
                                password = pwd,
                                Name = name
                            )
    return operator_username

def create_loan(N, username_account, operator_username):
    fake = Faker()
    for i in range(N):
        loan_no = i
        amount = round(random.rand()*1e5,2)
        state = random.choice(['successful','pending','failed'])
        account_no = random.choice(list(username_account.values()))
        operator_name = random.choice(operator_username)
        due_date = fake.date_time(tzinfo = None)
        loan.objects.create(loan_application_number = loan_no,
                            amount = amount,
                            state = state,
                            account_number = account.objects.get(account_number = account_no),
                            operator_name = operator.objects.get(username = operator_name),
                            due_date = due_date)

def create_wt(N, username_account):
    fake = Faker()
    for i in range(N):
        wt_no = i
        date = fake.date_time()
        currency_type = fake.currency_code()
        amount = round(random.rand() * 1e5,2)
        account_no = random.choice(list(username_account.values()))
        state = random.choice(['successful', 'pending', 'failed'])
        operator_name = random.choice(operator_username)
        payee_name = fake.name()
        payee_bank_name = fake.credit_card_provider(card_type = None)
        payee_account_no = fake.credit_card_number(card_type = None)
        payee_swift_code = fake.swift()

        wire_transfer.objects.create(wt_transaction_no=wt_no,
            date=date, currency_type=currency_type,
            amount = amount, account_number = account.objects.get(account_number = account_no),
            state = state, operator_name=operator.objects.get(username = operator_name),
            payee_name = payee_name, payee_bank_name = payee_bank_name,
            payee_account_no = payee_account_no, payee_swift_code = payee_swift_code)

def create_transaction(N, username_account):
    fake = Faker()
    for i in range(N):
        transaction_no = i
        transaction_date = fake.date_time()
        amount = random.rand()*1e4

        purpose = random.choice(['Alcoholic','Snacks','Health & Wellness','Household Items','Entertainment','Beverages',
                                 'Beauty','Others'])
        payer_account_no = random.choice(list(username_account.values()))
        payee_account_no = random.choice(list(username_account.values()))
        transaction.objects.create(transaction_no = transaction_no,
                                   transaction_date = transaction_date,
                                   amount = amount,
                                   purpose = purpose,
                                   payer_account_no = account.objects.get(account_number = payer_account_no),
                                   payee_account_no= account.objects.get(account_number = payee_account_no)
                                   )




operator_username = create_operator(20)
username_account = create_user(N, operator_username)
create_loan(int(N/4), username_account, operator_username)
create_wt(int(N/10), username_account)
create_transaction(int(N/2), username_account)


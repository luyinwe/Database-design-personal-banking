from django.db import models

# Create your models here.
class system_user(models.Model):
    username = models.CharField(max_length = 100, null = False, primary_key = True, unique = True)
    password = models.CharField(max_length = 100, null = False)
    Name = models.CharField(max_length = 100, null = False)

class operator(system_user):
    pass

class user(system_user):
    residential_address = models.CharField(max_length = 100)
    identification_information = models.CharField(max_length = 100)

class account(models.Model):
    account_number = models.CharField(max_length = 12, primary_key = True, unique = True)
    username = models.ForeignKey(user, on_delete = models.CASCADE)
    operator_name = models.ForeignKey(operator, on_delete = models.CASCADE)
    balance = models.IntegerField(default = 0)
    rating = models.IntegerField(default = 0)
class payee_account(account):
    pass
class payer_account(account):
    pass

class loan(models.Model):
    loan_application_number = models.CharField(max_length = 9, primary_key = True)
    amount = models.IntegerField(default = 0)
    state = models.BooleanField(default = False)
    account_number = models.ForeignKey(account, on_delete = models.CASCADE)
    opreator_name = models.ForeignKey(operator, on_delete = models.CASCADE)
    due_date = models.DateTimeField()

class wire_trasfer(models.Model):
    wt_transaction_no = models.CharField(max_length = 9, primary_key = True)
    date = models.DateTimeField()
    currency_type = models.CharField(max_length = 10)
    amount = models.IntegerField(default = 0)
    account_number = models.ForeignKey(account, on_delete = models.CASCADE)
    state = models.BooleanField(default = False)
    operator_name = models.ForeignKey(operator, on_delete = models.CASCADE)
    payee_name = models.CharField(max_length = 100)
    payee_bank_name = models.CharField(max_length = 100)
    payee_account_no = models.CharField(max_length = 100)
    payee_swift_code = models.CharField(max_length = 100)

class transaction(models.Model):
    transaction_no = models.CharField(max_length = 12, primary_key = True)
    transaction_date = models.DateTimeField()
    amount = models.IntegerField(default = 0)
    purpose = models.CharField(max_length = 10)
    payer_account_no = models.ForeignKey(payer_account, on_delete = models.CASCADE)
    payee_account_no = models.ForeignKey(payee_account, on_delete = models.CASCADE)


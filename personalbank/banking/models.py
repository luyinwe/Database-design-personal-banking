from django.db import models


# Create your models here.

class operator(models.Model):
    username = models.CharField(max_length=100, primary_key=True)
    password = models.CharField(max_length=100)
    Name = models.CharField(max_length=100)

class user(models.Model):
    username = models.CharField(max_length=100, primary_key=True, unique=True)
    password = models.CharField(max_length=100)
    def __unicode__(self):
        return self.username
    Name = models.CharField(max_length=100)
    residential_address = models.CharField(max_length = 100)
    ssn = models.CharField(max_length = 18)

class account(models.Model):
    account_number = models.CharField(max_length = 15, primary_key = True, unique = True)
    username = models.ForeignKey(user, on_delete = models.CASCADE)
    state = models.CharField(max_length = 100, choices=(('successful','successful'),('pending','pending'),('failed','failed')),default='pending')
    operator_name = models.ForeignKey(operator, on_delete = models.CASCADE)
    balance = models.FloatField(default = 0)
    rating = models.CharField(max_length = 100, choices=(('initial','initial'),('good','good'),('very good','very good'), ('excellent','excellent'), ('VIP','VIP')),default='initial')

class loan(models.Model):
    loan_application_number = models.CharField(max_length = 9, primary_key = True)
    amount = models.FloatField(default = 0)
    state = models.CharField(max_length = 100, choices=(('successful','successful'),('pending','pending'),('failed','failed')),default = 'pending')
    account_number = models.ForeignKey(account, on_delete = models.CASCADE)
    operator_name = models.ForeignKey(operator, on_delete = models.CASCADE)
    due_date = models.DateTimeField()

class wire_transfer(models.Model):
    wt_transaction_no = models.CharField(max_length = 9, primary_key = True)
    date = models.DateTimeField()
    currency_type = models.CharField(max_length = 10)
    amount = models.FloatField(default = 0)
    account_number = models.ForeignKey(account, on_delete = models.CASCADE)
    state = models.CharField(max_length = 100, choices=(('successful','successful'),('pending','pending'),('failed','failed')),default = 'pending')
    operator_name = models.ForeignKey(operator, on_delete = models.CASCADE)
    payee_name = models.CharField(max_length = 100)
    payee_bank_name = models.CharField(max_length = 100)
    payee_account_no = models.CharField(max_length = 100)
    payee_swift_code = models.CharField(max_length = 100)


class transaction(models.Model):
    transaction_no = models.CharField(max_length = 12, primary_key = True)
    transaction_date = models.DateTimeField()
    amount = models.FloatField(default = 0)
    purpose = models.CharField(max_length = 20)
    payer_account_no = models.ForeignKey(account, related_name = "payer_account_no", on_delete = models.CASCADE)
    payee_account_no = models.ForeignKey(account, related_name = "payee_account_no", on_delete = models.CASCADE)
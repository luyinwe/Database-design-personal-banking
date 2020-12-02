from django.urls import path
from banking import views
from django.conf.urls import url

urlpatterns = [
    url(r'^$', views.login, name='login'),
    url(r'^login/$', views.login, name='login'),
    url(r'^regist/$', views.regist, name='regist'),
    url(r'^index/$', views.index, name='index'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^account/$', views.user_account, name='account'),
    url(r'^transaction/$', views.transact, name='transaction'),
    url(r'^account_regist/$', views.user_account_regist, name='account_regist'),
    url(r'^loan/$', views.loan_app, name='loan'),
    url(r'^wire_transfer/$', views.wire_trans, name='wire_transfer'),
    url(r'^operatorLogin/$', views.operatorLogin, name='operatorLogin'),
    url(r'^operatorAccount/$', views.operatorAccount, name='operatorAccount'),
    url(r'^process_account_application/$', views.operatorAccountProcess, name='process_account_application'),
    url(r'^process_loan_application/$', views.operatorLoanProcess, name='process_loan_application'),
    url(r'^process_wire_transfer_application/$', views.operatorWTProcess, name='process_wire_transfer_application'),
    url(r'^search_transaction/$', views.search_transaction, name='search_transaction'),
    url(r'^evaluated_credit/$', views.evaluate_credit, name='evaluated_credite'),
    # url(r'^operator_account_check/$', views.operator_account_check, name='operator_account_check')
]
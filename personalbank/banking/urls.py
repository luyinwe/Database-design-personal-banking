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
]
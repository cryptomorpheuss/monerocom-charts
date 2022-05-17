from django.urls import path
#from django.conf.urls import url
from . import views

urlpatterns = [
    # Useful functions
    path('charts/get_prices/<str:symbol>/', views.get_prices, name='get_prices'),
    path('charts/generate_data/', views.generate_data, name='generate_data'),
    path('charts/erase_coins/', views.erase_coins, name='erase_coins'),
    path('charts/erase_data/', views.erase_data, name='erase_data'),
    path('charts/erase_database/', views.erase_database, name='erase_database'),
    path('charts/maintenance/', views.maintenance, name='maintenance'),

    # Charts pages
    path('charts/sf/<str:scale>/', views.sf, name='sf'),
    path('charts/price/<str:scale>/', views.price, name='price'),
    path('charts/price_btc/<str:scale>/', views.price_btc, name='price_btc'),
    path('charts/cycle', views.cycle, name='cycle'),
    path('charts/sfmultiple', views.sfmultiple, name='sfmultiple'),
    path('charts/inflationfractal', views.inflationfractal, name='inflationfractal'),
    path('charts/golden', views.golden, name='golden'),
    path('charts/competitors', views.competitors, name='competitors'),
    path('charts/inflationreturn', views.inflationreturn, name='inflationreturn'),
    path('charts/shielded', views.shielded, name='shielded'),
    path('charts/total_transactions', views.total_transactions, name='total_transactions'),


    # Old functions, activate in case we run into some king of error with previous functions
    #path('charts/sf/<str:scale>/', views.sf_old, name='sf'),
    #path('charts/price/<str:scale>/', views.price_old, name='price_old'),
    #path('charts/price_btc/<str:scale>/', views.price_btc_old, name='price_btc_old'),
    #path('charts/cycle', views.cycle_old, name='cycle'),
    #path('charts/total_transactions', views.total_transactions_old, name='total_transactions_old'),
]

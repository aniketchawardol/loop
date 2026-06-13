from django.urls import path
from . import views

urlpatterns = [
    path('api/credits', views.credits_balance),
    path('api/credits/history', views.credits_history),
    path('api/rewards', views.rewards_list),
    path('api/rewards/<int:pk>/claim', views.claim_reward),
]

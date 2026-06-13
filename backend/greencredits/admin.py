from django.contrib import admin
from .models import GreenCreditAccount, CreditTransaction, Reward, RewardClaim

admin.site.register(GreenCreditAccount)
admin.site.register(CreditTransaction)
admin.site.register(Reward)
admin.site.register(RewardClaim)

from django.db import models
from django.conf import settings
from core.models import TimeStamped

class GreenCreditAccount(TimeStamped):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="green_credits")
    balance = models.PositiveIntegerField(default=0)

class CreditTransaction(TimeStamped):
    account = models.ForeignKey(GreenCreditAccount, on_delete=models.CASCADE, related_name="transactions")
    amount = models.IntegerField()  # positive = earn, negative = spend
    type = models.CharField(max_length=30)
    description = models.CharField(max_length=200)
    reference_id = models.PositiveIntegerField(null=True)

class Reward(TimeStamped):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    cost = models.PositiveIntegerField()
    icon = models.CharField(max_length=10)
    active = models.BooleanField(default=True)

class RewardClaim(TimeStamped):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    credits_spent = models.PositiveIntegerField()

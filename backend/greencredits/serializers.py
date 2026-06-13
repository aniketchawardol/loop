from rest_framework import serializers
from .models import GreenCreditAccount, CreditTransaction, Reward, RewardClaim

class GreenCreditAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = GreenCreditAccount
        fields = ['balance']

class CreditTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditTransaction
        fields = ['amount', 'type', 'description', 'created_at']

class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = ['id', 'title', 'description', 'cost', 'icon', 'active']

class RewardClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardClaim
        fields = ['reward', 'credits_spent', 'created_at']

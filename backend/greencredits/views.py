from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import GreenCreditAccount, CreditTransaction, Reward, RewardClaim
from .serializers import (
    GreenCreditAccountSerializer,
    CreditTransactionSerializer,
    RewardSerializer,
    RewardClaimSerializer,
)
from django.db import transaction

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def credits_balance(request):
    account, _ = GreenCreditAccount.objects.get_or_create(user=request.user)
    # Mock impact stats for now
    impact = {
        "items_saved_from_landfill": 3,
        "co2_avoided_kg": 4.7,
        "km_saved": 1400,
    }
    data = GreenCreditAccountSerializer(account).data
    data["impact"] = impact
    data["total_earned"] = sum(t.amount for t in account.transactions.filter(amount__gt=0))
    data["total_spent"] = sum(-t.amount for t in account.transactions.filter(amount__lt=0))
    data["balance"] = account.balance
    return Response(data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def credits_history(request):
    account, _ = GreenCreditAccount.objects.get_or_create(user=request.user)
    txs = account.transactions.order_by("-created_at")[:50]
    return Response(CreditTransactionSerializer(txs, many=True).data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def rewards_list(request):
    rewards = Reward.objects.filter(active=True)
    return Response(RewardSerializer(rewards, many=True).data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def claim_reward(request, pk):
    account, _ = GreenCreditAccount.objects.get_or_create(user=request.user)
    try:
        reward = Reward.objects.get(pk=pk, active=True)
    except Reward.DoesNotExist:
        return Response({"success": False, "message": "Reward not found."}, status=404)
    if account.balance < reward.cost:
        return Response({"success": False, "message": f"Not enough credits (need {reward.cost - account.balance} more)"}, status=400)
    with transaction.atomic():
        account.balance -= reward.cost
        account.save()
        CreditTransaction.objects.create(
            account=account,
            amount=-reward.cost,
            type="REWARD_CLAIM",
            description=f"Claimed {reward.title}",
        )
        RewardClaim.objects.create(
            user=request.user,
            reward=reward,
            credits_spent=reward.cost,
        )
    return Response({"success": True, "new_balance": account.balance, "message": "Reward claimed!"})

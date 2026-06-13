from greencredits.models import GreenCreditAccount, CreditTransaction

def award_credits(user, amount, type, description, reference_id=None):
    if not user:
        return
    account, _ = GreenCreditAccount.objects.get_or_create(user=user)
    account.balance += amount
    account.save()
    CreditTransaction.objects.create(
        account=account,
        amount=amount,
        type=type,
        description=description,
        reference_id=reference_id,
    )

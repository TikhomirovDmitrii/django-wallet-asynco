from django.db import models
import uuid

class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    class Meta:
        db_table = 'wallets'

    def __str__(self):
        return f"Wallet {self.id} - Balance: {self.balance}"
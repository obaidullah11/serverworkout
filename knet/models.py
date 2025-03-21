from django.db import models
from django.utils import timezone

# class KnetPayment(models.Model):
#     STATUS_CHOICES = (
#         ('PENDING', 'Pending'),
#         ('SUCCESS', 'Success'),
#         ('FAILED', 'Failed'),
#         ('CANCELLED', 'Cancelled'),
#     )

#     tracking_id = models.CharField(max_length=50, unique=True)
#     amount = models.DecimalField(max_digits=10, decimal_places=3)
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
#     payment_id = models.CharField(max_length=50, null=True, blank=True)
#     result = models.CharField(max_length=50, null=True, blank=True)
#     payment_data = models.JSONField(null=True, blank=True)
#     created_at = models.DateTimeField(default=timezone.now)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.tracking_id} - {self.amount} KWD"

#     class Meta:
#         ordering = ['-created_at']


from django.db import models

class KnetTransaction(models.Model):
    track_id = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=3)
    status = models.CharField(max_length=20, default='INITIATED')  # Ensure this field exists
    result = models.CharField(max_length=20, blank=True, null=True)
    payment_id = models.CharField(max_length=50, blank=True, null=True)
    auth = models.CharField(max_length=50, blank=True, null=True)
    ref = models.CharField(max_length=50, blank=True, null=True)
    tran_id = models.CharField(max_length=50, blank=True, null=True)
    encrypted_response = models.TextField(blank=True, null=True)
    decrypted_response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.track_id

from django.db import models

# Create your models here.
from accounts.models import User
from plots.models import Plot

class Reservation(models.Model):

    STATUS = (
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Cancelled", "Cancelled"),
        ("Expired", "Expired"),
    )
    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reservations"
    )
    plot = models.ForeignKey(
        Plot,
        on_delete=models.CASCADE,
        related_name="reservations"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="Pending"
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.buyer.username} - {self.plot.plot_number}"
    

class Purchase(models.Model):
    STATUS = (
        ("Pending Payment","Pending Payment"),
        ("Paid","Paid"),
        ("Completed","Completed"),
        ("Cancelled","Cancelled"),
    )
    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="purchases"
    )
    plot = models.OneToOneField(
        Plot,
        on_delete=models.CASCADE,
        related_name="purchase"
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS,
        default="Pending Payment"
    )
    purchased_at = models.DateTimeField(
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    def __str__(self):
        return f"{self.buyer.username} - {self.plot.plot_number}"
    

class Payment(models.Model):
    PAYMENT_STATUS = (
        ("Pending","Pending"),
        ("Successful","Successful"),
        ("Failed","Failed"),
    )
    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    reference = models.CharField(
        max_length=100,
        unique=True
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default="Pending"
    )
    payment_date = models.DateTimeField(
        auto_now_add=True
    )
    def __str__(self):
        return self.reference
    

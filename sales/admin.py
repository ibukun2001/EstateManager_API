from django.contrib import admin

from .models import Payment, Purchase, Reservation

admin.site.register(Reservation)
admin.site.register(Purchase)
admin.site.register(Payment)

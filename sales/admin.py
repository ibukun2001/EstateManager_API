from django.contrib import admin

from .models import (
    Reservation,
    Purchase,
    Payment
)


admin.site.register(Reservation)
admin.site.register(Purchase)
admin.site.register(Payment)
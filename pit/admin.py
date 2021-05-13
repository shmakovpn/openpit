from django.contrib import admin
from pit.models import (
    TruckModel,
    Truck,
    Mineral,
    Storage,
    OtherStorageIncom,
    Trip,
)


# Register your models here.
admin.site.register(TruckModel)
admin.site.register(Truck)
admin.site.register(Storage)
admin.site.register(OtherStorageIncom)
admin.site.register(Mineral)
admin.site.register(Trip)

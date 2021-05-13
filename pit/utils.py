from .models import (
    TruckModel,
    Truck,
    Mineral,
    Storage,
    OtherStorageIncom,
    Trip,
)
from django.contrib.auth.models import User


def factory_reset(reset_admin=True) -> None:
    """ reset database to initial state """
    # clear all tables
    Trip.objects.all().delete()
    OtherStorageIncom.objects.all().delete()
    Storage.objects.all().delete()
    Mineral.objects.all().delete()
    Truck.objects.all().delete()
    TruckModel.objects.all().delete()

    if reset_admin:
        User.objects.all().delete()
        # create super user
        admin = User(
            is_superuser=True,
            username='admin',
            email='admin@admin.ru',
            is_active=True,
            is_staff=True
        )
        admin.set_password('admin')
        admin.save()

    # create TruckModels
    tm_belaz = TruckModel(title='БЕЛАЗ', max_weight=120)
    tm_belaz.save()
    tm_komatsu = TruckModel(title='Komatsu', max_weight=110)
    tm_komatsu.save()
    # create Trucks
    t_101 = Truck(number=101, truck_model=tm_belaz)
    t_101.save()
    t_102 = Truck(number=102, truck_model=tm_belaz)
    t_102.save()
    t_K103 = Truck(number='K103', truck_model=tm_komatsu)
    t_K103.save()
    # create Minerals
    m_101 = Mineral(weight=100, sio2=32, fe=67)
    m_101.save()
    m_102 = Mineral(weight=125, sio2=30, fe=65)
    m_102.save()
    m_K103 = Mineral(weight=120, sio2=35, fe=62)
    m_K103.save()
    m_storage = Mineral(weight=900, sio2=34, fe=65)
    m_storage.save()
    # create Trips
    trip_101 = Trip(truck=t_101, mineral=m_101)
    trip_101.save()
    trip_102 = Trip(truck=t_102, mineral=m_102)
    trip_102.save()
    trip_K103 = Trip(truck=t_K103, mineral=m_K103)
    trip_K103.save()
    # create Storages
    storage = Storage(
        title='Склад',
        territory='POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))',
    )
    storage.save()
    # create OtherStorageIncom
    storage_incom = OtherStorageIncom(mineral=m_storage, storage=storage)
    storage_incom.save()

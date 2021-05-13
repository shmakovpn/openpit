from django.test import TestCase
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.gis.geos import Point
from .models import (
    TruckModel,
    Truck,
    Mineral,
    Storage,
    OtherStorageIncom,
    Trip,
)
import pit.patterns as patterns


# Create your tests here.
class PatternsTest(TestCase):
    """ test for regex patterns """

    def test_xy(self):
        """ be sure that X Y point pattern works properly """
        match = patterns.XY.search('something wrong')
        self.assertIsNone(match)
        #
        match = patterns.XY.search('1d 20')
        self.assertIsNone(match)
        #
        match = patterns.XY.search('')
        self.assertIsNone(match)
        #
        match = patterns.XY.search('10 20')
        self.assertIsNotNone(match)
        self.assertEqual(match.group('x'), '10')
        self.assertEqual(match.group('y'), '20')
        #
        match = patterns.XY.search('+11 -22')
        self.assertIsNotNone(match)
        self.assertEqual(match.group('x'), '+11')
        self.assertEqual(match.group('y'), '-22')
        #
        match = patterns.XY.search('-11 +22')
        self.assertIsNotNone(match)
        self.assertEqual(match.group('x'), '-11')
        self.assertEqual(match.group('y'), '+22')
        #
        match = patterns.XY.search('.9 3.2')
        self.assertIsNotNone(match)
        self.assertEqual(match.group('x'), '.9')
        self.assertEqual(match.group('y'), '3.2')
        #
        match = patterns.XY.search('ad.9 3.2')
        self.assertIsNone(match)
        #
        match = patterns.XY.search('.9 3.2dsa')
        self.assertIsNone(match)


class TruckModelTest(TestCase):
    """ tests for the TruckModel model """

    def test_create(self) -> None:
        """ creation of a model of a truck """
        truck_model = TruckModel(title='Mongo', max_weight=120)
        truck_model.save()
        self.assertEqual(truck_model.pk, 1)

    def test_constraint_max_weight_not_null(self):
        """ max_weight cannot be NULL """
        try:
            truck_model = TruckModel(title='Postgres')
            truck_model.save()  # an exception here
            self.fail('"max_weight can be NULL"')
        except IntegrityError:
            pass

    def test_constraint_max_weight_not_0(self):
        """ max_weight cannot be 0 """
        try:
            truck_model = TruckModel(title='Maria', max_weight=0)
            truck_model.save()
            self.fail('"max_weight" can be 0')
        except IntegrityError:
            pass

    def test_constraint_max_weight_not_positive(self):
        """ max_weight cannot be < 0 """
        try:
            truck_model = TruckModel(title='Sqlite', max_weight=-32)
            truck_model.save()
            self.fail('"max_weight" can be < 0')
        except IntegrityError:
            pass

    def test_constraint_title_not_null(self):
        """ title cannot be NULL """
        try:
            truck_model = TruckModel(max_weight=10)
            truck_model.save()
            self.fail('"title" can be NULL')
        except IntegrityError:
            pass

    def test_constraint_title_not_empty(self):
        """ title cannot be an empty """
        try:
            truck_model = TruckModel(title='', max_weight=10)
            truck_model.save()
            self.fail('"title" can be an empty')
        except IntegrityError:
            pass

    def test_constraint_title_unique_ignore_case(self):
        """ title is unique ignore case """
        try:
            truck_model = TruckModel(title='Hello', max_weight=60)
            truck_model.save()
            truck_model2 = TruckModel(title='HellO', max_weight=123)
            truck_model2.save()
            self.fail("Unique constraint ignore case does not work")
        except IntegrityError:
            pass


class TruckTest(TestCase):
    """ tests for the Truck model """

    def setUp(self):
        TruckModel.objects.create(title='БЕЛАЗ', max_weight=120)
        TruckModel.objects.create(title='Komatsu', max_weight=110)

    def test_create(self):
        """ be shure that we can create trucks """
        tm_belaz = TruckModel.objects.get(title='БЕЛАЗ')
        Truck.objects.create(number=101, truck_model=tm_belaz)
        Truck.objects.create(number=102, truck_model=tm_belaz)
        tm_komatsu = TruckModel.objects.get(title='Komatsu')
        Truck.objects.create(number='K103', truck_model=tm_komatsu)

    def test_constraint_number_not_null(self):
        """ number cannot be NULL """
        tm_belaz = TruckModel.objects.get(title='БЕЛАЗ')
        try:
            truck = Truck(truck_model=tm_belaz)
            truck.save()
            self.fail('a truck number can be NULL')
        except IntegrityError:
            pass

    def test_constraint_number_not_empty(self):
        """ number cannot be an empty """
        tm_belaz = TruckModel.objects.get(title='БЕЛАЗ')
        try:
            truck = Truck(number='', truck_model=tm_belaz)
            truck.save()
            self.fail('"a truck number can be an empty"')
        except IntegrityError:
            pass

    def test_constraint_number_unique_ignore_case(self):
        """ number is unique ignore case """
        tm_belaz = TruckModel.objects.get(title='БЕЛАЗ')
        try:
            truck1 = Truck(number='Moscow', truck_model=tm_belaz)
            truck1.save()
            truck2 = Truck(number='MoSCow', truck_model=tm_belaz)
            truck2.save()
            self.fail('truck number unique ignore case does not work')
        except IntegrityError:
            pass

    def test_property_max_weight(self):
        """ max_weight must return truck_model.max_weight """
        tm_belaz = TruckModel.objects.get(title='БЕЛАЗ')
        truck = Truck(number=101, truck_model=tm_belaz)
        self.assertEqual(truck.max_weight, tm_belaz.max_weight)

    def test_property_model_title(self):
        """ model_title must return truck_model.title """
        tm_belaz = TruckModel.objects.get(title='БЕЛАЗ')
        truck = Truck(number=101, truck_model=tm_belaz)
        self.assertEqual(truck.model_title, tm_belaz.title)


class MineralTest(TestCase):
    """ tests for Mineral model """

    def test_create(self):
        """ be sure that we can create this """
        Mineral.objects.create(weight=100, sio2=32, fe=67)
        Mineral.objects.create(weight=125, sio2=30, fe=65)
        Mineral.objects.create(weight=120, sio2=35, fe=62)
        Mineral.objects.create(weight=900, sio2=34, fe=65)
        self.assertEqual(Mineral.objects.all().count(), 4)

    def test_constraint_weight_not_null(self):
        """ weight cannot be NULL """
        try:
            mineral = Mineral(sio2=40, fe=50)
            mineral.save()
            self.fail('Mineral weight can be NULL')
        except IntegrityError:
            pass

    def test_constraint_weight_not_empty(self):
        """ weight cannot be an empty """
        try:
            mineral = Mineral(weight=0, sio2=40, fe=60)
            mineral.save()
            self.fail('Mineral weight can be an empty')
        except IntegrityError:
            pass

    def test_constraint_weight_is_positive(self):
        """ weight cannot be < 0 """
        try:
            mineral = Mineral(weight=-432, sio2=40, fe=60)
            mineral.save()
            self.fail('Mineral weight can be < 0')
        except IntegrityError:
            pass

    def test_constraint_sio2_not_null(self):
        """ SiO2 cannot be NULL """
        try:
            mineral = Mineral(weight=432, fe=60)
            mineral.save()
            self.fail('Mineral SiO2 can be NULL')
        except IntegrityError:
            pass

    def test_constraint_sio2_not_0(self):
        """ SiO2 cannot be equal to 0 """
        try:
            mineral = Mineral(weight=432, sio2=0, fe=60)
            mineral.save()
            self.fail('Mineral SiO2 can be 0')
        except IntegrityError:
            pass

    def test_constraint_sio2_positive(self):
        """ SiO2 cannot beG < 0 """
        try:
            mineral = Mineral(weight=432, sio2=-30, fe=60)
            mineral.save()
            self.fail('Mineral SiO2 can be < 0')
        except IntegrityError:
            pass

    def test_constraint_sio2_is_percent(self):
        """ SiO2 cannot be > 100 """
        try:
            mineral = Mineral(weight=432, sio2=101, fe=60)
            mineral.save()
            self.fail('Mineral SiO2 can be > 100')
        except IntegrityError as e:
            self.assertEqual(
                str(e),
                'CHECK constraint failed: pit_mineral_SiO2_is_percent'
            )

    def test_constraint_fe_not_null(self):
        """ Fe cannot be NULL """
        try:
            mineral = Mineral(weight=432, sio2=40)
            mineral.save()
            self.fail('Mineral Fe can be NULL')
        except IntegrityError:
            pass

    def test_constraint_fe_not_0(self):
        """ Fe cannot be equeal to 0 """
        try:
            mineral = Mineral(weight=432, sio2=40, fe=0)
            mineral.save()
            self.fail('Mineral Fe can be 0')
        except IntegrityError:
            pass

    def test_constraint_fe_positive(self):
        """ Fe cannot be < 0 """
        try:
            mineral = Mineral(weight=432, sio2=40, fe=-32)
            mineral.save()
            self.fail('Mineral Fe can be < 0')
        except IntegrityError:
            pass

    def test_constraint_fe_is_persent(self):
        """ Fe cannot be > 100 """
        try:
            mineral = Mineral(weight=432, sio2=40, fe=101)
            mineral.save()
            self.fail('Mineral Fe can be > 100')
        except IntegrityError as e:
            self.assertEqual(
                str(e),
                'CHECK constraint failed: pit_mineral_Fe_is_percent'
            )

    def test_constraint_sio2_fe_together(self):
        """ Sio2+Fe cannot be >= 100 """
        try:
            mineral = Mineral(weight=432, sio2=40, fe=60)
            mineral.save()
            self.fail('SiO2+Fe can be > 100%')
        except IntegrityError as e:
            self.assertEqual(
                str(e),
                'CHECK constraint failed: pit_mineral_SiO2_Fe_lt100'
            )


class StorageTest(TestCase):
    """ tests for storage of mineral """

    def test_create(self):
        """ be sure that we can create a storage """
        storage = Storage(
            title='Sklad1',
            territory='POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))'
        )
        storage.save()
        self.assertEqual(storage.pk, 1)

    def test_title_not_null(self):
        """ storage title cannot be NULL """
        try:
            storage = Storage(
                territory='POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))'
            )
            storage.save()
            self.fail('Storage title can be NULL')
        except IntegrityError:
            pass

    def test_title_not_empty(self):
        """ storage title cannot be an empty """
        try:
            storage = Storage(
                title='',
                territory='POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))'
            )
            storage.save()
            self.fail('Storage title can be an empty')
        except IntegrityError:
            pass

    def test_title_unique_ignore_case(self):
        """ storage title is unique ignore case """
        try:
            storage1 = Storage(
                title='Sklad1',
                territory='POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))'
            )
            storage1.save()
            storage2 = Storage(
                title='SklAD1',
                territory='POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))'
            )
            storage2.save()
            self.fail('Storage title is not unique ignore case')
        except IntegrityError:
            pass

    def test_validate_unique(self):
        """ Storages must not intercest each other """
        storage1 = Storage(
            title='Sklad1',
            territory='POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))'
        )
        storage1.save()
        try:
            storage_in = Storage(
                title='Sklad_in',
                territory='POLYGON ((30 20, 30 30, 25 30, 20 20, 30 20))'
            )
            storage_in.validate_unique()
            self.fail('Storage_in validation failed')
        except ValidationError:
            pass
        try:
            storage_border = Storage(
                title='Sklad_border',
                territory='POLYGON ((30 10, 40 40, 10 40, 30 10))'
            )
            storage_border.validate_unique()
            self.fail('Storage_border validation failed')
        except ValidationError:
            pass
        try:
            storage_cross = Storage(
                title='Sklad_cross',
                territory='POLYGON ((30 20, 40 20, 40 30, 30 30, 30 20))'
            )
            storage_cross.validate_unique()
            self.fail('Storage_cross validation failed')
        except ValidationError:
            pass
        try:
            storage_point = Storage(
                title='Sklad_point',
                territory='POLYGON ((30 10, 30 5, 40 5, 40 10, 30 10))'
            )
            storage_point.validate_unique()
            self.fail('Storage_point validation failed')
        except ValidationError:
            pass
        try:
            storage_out = Storage(
                title='Sklad_out',
                territory='POLYGON ((40 10, 50 10, 50 20, 40 20, 40 10))'
            )
            storage_out.validate_unique()
        except ValidationError:
            self.fail('Storage_out validation failed')


class OtherStorageIncomTest(TestCase):
    """ test for not trip storage incoms """

    def setUp(self):
        self.storage = Storage(
            title='Sklad1',
            territory='POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))'
        )
        self.storage.save()
        self.m_101 = Mineral(weight=100, sio2=32, fe=67)
        self.m_101.save()
        self.m_102 = Mineral(weight=125, sio2=30, fe=65)
        self.m_102.save()

    def test_create(self):
        """ be sure that we can create not trip storage income """
        storage_income = OtherStorageIncom(
            mineral=self.m_101,
            storage=self.storage
        )
        storage_income.save()
        self.assertEqual(storage_income.id, 1)

    def test_one_mineral_one_income(self):
        """ one mineral can used in only one income """
        try:
            storage_income = OtherStorageIncom(
                mineral=self.m_101,
                storage=self.storage
            )
            storage_income.save()
            storage_income2 = OtherStorageIncom(
                mineral=self.m_101,
                storage=self.storage
            )
            storage_income2.save()
            self.fail('One mineral can used in several storage income')
        except IntegrityError:
            pass


class TripTest(TestCase):
    """ tests for truck trips """

    def setUp(self):
        self.tm_belaz = TruckModel(title='БЕЛАЗ', max_weight=120)
        self.tm_belaz.save()
        self.tm_komatsu = TruckModel(title='Komatsu', max_weight=110)
        self.tm_komatsu.save()

        self.t_101 = Truck(number=101, truck_model=self.tm_belaz)
        self.t_101.save()
        self.t_102 = Truck(number=102, truck_model=self.tm_belaz)
        self.t_102.save()
        self.t_K103 = Truck(number='K103', truck_model=self.tm_komatsu)
        self.t_K103.save()

        self.m_101 = Mineral(weight=100, sio2=32, fe=67)
        self.m_101.save()
        self.m_102 = Mineral(weight=125, sio2=30, fe=65)
        self.m_102.save()
        self.m_K103 = Mineral(weight=120, sio2=35, fe=62)
        self.m_K103.save()
        self.m_storage = Mineral(weight=900, sio2=34, fe=65)
        self.m_storage.save()

    def test_create(self):
        """ be sure that we can create this """
        trip_101 = Trip(truck=self.t_101, mineral=self.m_101)
        trip_101.save()
        trip_102 = Trip(truck=self.t_102, mineral=self.m_102)
        trip_102.save()
        trip_K103 = Trip(truck=self.t_K103, mineral=self.m_K103)
        trip_K103.save()
        self.assertEqual(Trip.objects.all().count(), 3)

    def test_create_with_wkt_points(self):
        """ be sure that we can create trips with WKT coordinates """
        trip = Trip(
            truck=self.t_101,
            mineral=self.m_101,
            unloading_point='POINT(10 20)'  # using WKT POINT here
        )
        trip.save()
        self.assertEqual(trip.id, 1)
        self.assertIsInstance(Trip.objects.get(id=1).unloading_point, Point)

    def test_create_with_points(self):
        """ be sure that we can create trips using gis geos """
        trip = Trip(
            truck=self.t_101,
            mineral=self.m_101,
            unloading_point=Point(10, 20)
        )
        trip.save()
        self.assertEqual(trip.id, 1)

    def test_create_for_one_truck(self):
        """ be sure that we can create trips for the same truck with
        different points """
        trip1 = Trip(
            truck=self.t_101,
            mineral=self.m_101,
            unloading_point=Point(10, 20)
        )
        trip1.save()
        trip2 = Trip(
            truck=self.t_101,
            mineral=self.m_102,
            unloading_point=Point(10, 20)
        )
        trip2.save()
        trip3 = Trip(truck=self.t_101, mineral=self.m_K103)  # active trip
        trip3.save()
        self.assertEqual(Trip.objects.all().count(), 3)

    def test_constraint_only_one_truck_with_active_trip(self):
        """ A truck can has only one active trip """
        try:
            Trip.objects.create(truck=self.t_101, mineral=self.m_101)
            Trip.objects.create(truck=self.t_101, mineral=self.m_102)
            self.fail('Can create two active trips for the same truck')
        except IntegrityError:
            pass

    def test_constraint_one_trip_for_one_mineral(self):
        """ A mineral can has only one trip """
        try:
            Trip.objects.create(truck=self.t_101, mineral=self.m_101)
            Trip.objects.create(truck=self.t_102, mineral=self.m_101)
            self.fail('One mineral can has more than one trip')
        except IntegrityError:
            pass

    def test_property_active(self):
        """ Checking that active property works """
        trip = Trip(truck=self.t_101, mineral=self.m_101)
        trip.save()
        self.assertEqual(trip.active, True)
        trip.unloading_point = Point(10, 20)
        self.assertEqual(trip.active, False)

    def test_property_failed(self):
        """ Checking that failed property works """
        storage = Storage(
            title='Sklad1',
            territory='POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))'
        )
        storage.save()
        trip_in = Trip(
            truck=self.t_101,
            mineral=self.m_101,
            unloading_point=Point(20, 20)
        )
        trip_in.save()
        self.assertEqual(trip_in.failed, False)
        trip_active = Trip(truck=self.t_102, mineral=self.m_102)
        trip_active.save()
        self.assertEqual(trip_active.failed, False)
        trip_border = Trip(
            truck=self.t_K103,
            mineral=self.m_K103,
            unloading_point=Point(30, 10)
        )
        trip_border.save()
        self.assertEqual(trip_border.failed, False)
        trip_out = Trip(
            truck=self.t_101,
            mineral=self.m_storage,
            unloading_point=Point(40, 30)
        )
        trip_out.save()
        self.assertEqual(trip_out.failed, True)

    def test_property_truck_max_weight(self):
        """ truck_max_weight must return truck.max_weight """
        trip_101 = Trip(truck=self.t_101, mineral=self.m_101)
        trip_101.save()
        self.assertEqual(trip_101.truck_max_weight, trip_101.truck.max_weight)

    def test_property_mineral_weight(self):
        """ mineral_weight must return mineral.weight """
        trip_101 = Trip(truck=self.t_101, mineral=self.m_101)
        trip_101.save()
        self.assertEqual(trip_101.mineral_weight, trip_101.mineral.weight)

    def test_property_overload(self):
        """ test for overload property """
        # 50% of max_weight
        max_weight_50 = int(self.t_101.max_weight / 2)
        mineral_50 = Mineral(
            weight=max_weight_50,
            sio2=32,
            fe=67
        )
        mineral_50.save()
        trip_50 = Trip(
            truck=self.t_101,
            mineral=mineral_50,
        )
        trip_50.save()
        self.assertEqual(trip_50.overload, 0)
        # 100% of max_weight
        mineral_100 = Mineral(
            weight=self.t_102.max_weight,
            sio2=32,
            fe=67
        )
        mineral_100.save()
        trip_100 = Trip(
            truck=self.t_102,
            mineral=mineral_100,
        )
        trip_100.save()
        self.assertEqual(trip_100.overload, 0)
        # 200% of max_weight
        mineral_200 = Mineral(
            weight=self.t_K103.max_weight * 2,
            sio2=32,
            fe=67
        )
        mineral_200.save()
        trip_200 = Trip(
            truck=self.t_K103,
            mineral=mineral_200,
        )
        trip_200.save()
        self.assertEqual(trip_200.overload, 100)

    def test_property_truck_number(self):
        """ truck_number must return truck.number """
        trip_101 = Trip(truck=self.t_101, mineral=self.m_101)
        trip_101.save()
        self.assertEqual(trip_101.truck_number, trip_101.truck.number)

    def test_property_truck_model_title(self):
        """ truck_model_title must return truck.model_title """
        trip_101 = Trip(truck=self.t_101, mineral=self.m_101)
        trip_101.save()
        self.assertEqual(trip_101.truck_model_title, trip_101.truck.model_title)





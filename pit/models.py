from typing import Optional, Collection
from django.contrib.gis.db import models
from django.db.models import Q, CASCADE, F
from django.core.exceptions import ValidationError
from pit.db_constraints import IUniqueConstraint
import pit.patterns as patterns
from django.contrib.gis.geos import Point


# Create your models here.
class TruckModel(models.Model):
    """ A model of a truck """
    title = models.CharField(
        max_length=60, unique=True, null=False, blank=False,
    )
    max_weight = models.IntegerField(null=False, blank=False)

    def __str__(self) -> str:
        return f'{self.title} {self.max_weight}'

    def validate_unique(self, exclude=None):
        if TruckModel.objects\
                .exclude(id=self.id)\
                .filter(title__iexact=self.title).exists():
            raise ValidationError({
                'title': ValidationError(
                    f'Must be unique ignore case. '
                    f'"{self.title}" is already in use'
                )
            })

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(max_weight__gt=0),
                name='%(app_label)s_%(class)s_max_weight_is_positive'
            ),
            models.CheckConstraint(
                check=~Q(title=''),
                name='%(app_label)s_%(class)s_title_is_not_empty'
            ),
            IUniqueConstraint(
                name='%(app_label)s_%(class)s_title_is_unique_ignore_case',
                fields=['title'],
            )
        ]


class Truck(models.Model):
    """ Trucks """
    number = models.CharField(
        max_length=20, null=False, blank=False, unique=True
    )
    truck_model = models.ForeignKey(
        to=TruckModel,
        on_delete=CASCADE
    )

    def __str__(self) -> str:
        return f'{self.number} {self.truck_model.title}'

    @property
    def max_weight(self) -> int:
        """ returns the max_weight of the model of the truck """
        return self.truck_model.max_weight

    @property
    def model_title(self) -> str:
        """ return the title of the model of the truck """
        return self.truck_model.title

    def validate_unique(self, exclude=None):
        if Truck.objects\
                .exclude(id=self.id)\
                .filter(number__iexact=self.number).exists():
            raise ValidationError({
                'number': ValidationError(
                    f'Must be unique ignore case. '
                    f'"{self.number}" is already in use'
                )
            })

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~Q(number=''),
                name='%(app_label)s_%(class)s_number_is_not_empty'
            ),
            IUniqueConstraint(
                name='%(app_label)s_%(class)s_number_is_unique_ignore_case',
                fields=['number'],
            )
        ]


class Mineral(models.Model):
    """ Payload of a truck and the store """
    weight = models.IntegerField(null=False, blank=False)
    sio2 = models.IntegerField(null=False, blank=False)
    fe = models.IntegerField(null=False, blank=False)

    def __str__(self) -> str:
        return f'mineral: {self.weight}t. %SiO2={self.sio2}, %Fe={self.fe}'

    def clean(self) -> None:
        """ validation """
        if self.weight <= 0:
            raise ValidationError({
                'weight': ValidationError('Weight must be > 0')
            })
        if self.sio2 <= 0:
            raise ValidationError({
                'sio2': ValidationError('SiO2 must be > 0')
            })
        if self.fe <= 0:
            raise ValidationError({
                'fe': ValidationError('Fe must be > 0')
            })
        if self.sio2 >= 100:
            raise ValidationError({
                'sio2': ValidationError('SiO2 must be < 100')
            })
        if self.fe >= 100:
            raise ValidationError({
                'fe': ValidationError('Fe must be < 100')
            })
        if (self.sio2 + self.fe) >= 100:
            raise ValidationError({
                'sio2': ValidationError('Sio2+Fe must be < 100'),
                'fe': ValidationError('SiO2+Fe must be < 100')
            })

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(weight__gt=0),
                name='%(app_label)s_%(class)s_weight_is_positive',
            ),
            models.CheckConstraint(
                check=Q(sio2__gt=0) & Q(sio2__lt=100),
                name='%(app_label)s_%(class)s_SiO2_is_percent'
            ),
            models.CheckConstraint(
                check=Q(fe__gt=0) & Q(fe__lt=100),
                name='%(app_label)s_%(class)s_Fe_is_percent'
            ),
            models.CheckConstraint(
                check=Q(sio2__lt=(100-F('fe'))),
                name='%(app_label)s_%(class)s_SiO2_Fe_lt100'
            )
        ]


class Storage(models.Model):
    """ A storage of mineral """
    title = models.CharField(
        max_length=40, null=False, blank=False, unique=True
    )
    territory = models.PolygonField(null=False, blank=False)

    def __str__(self) -> str:
        return f'Storage {self.title} {self.territory}'

    def validate_unique(self, exclude: Optional[Collection[str]] = None):
        intersectors = Storage.objects\
            .exclude(id=self.id)\
            .filter(territory__intersects=self.territory)
        if intersectors.exists():
            raise ValidationError({
                'territory': ValidationError(
                    f'Intercests with {intersectors[0].territory}'
                )
            })

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~Q(title=''),
                name='%(app_label)s_%(class)s_title_is_not_empty'
            ),
            IUniqueConstraint(
                name='%(app_label)s_%(class)s_title_is_unique_ignore_case',
                fields=['title'],
            )
        ]


class OtherStorageIncom(models.Model):
    """ Not trip incoms to a storage """
    mineral = models.OneToOneField(to=Mineral, on_delete=CASCADE)
    storage = models.ForeignKey(to=Storage, on_delete=CASCADE)

    def __str__(self):
        return f'Storage incom: {self.mineral} {self.storage}'


class Trip(models.Model):
    """ A trip of a truck """
    truck = models.ForeignKey(to=Truck, on_delete=CASCADE)
    mineral = models.OneToOneField(to=Mineral, on_delete=CASCADE)
    unloading_point = models.PointField(null=True)

    @property
    def active(self) -> bool:
        """ Returns True then the trip is active,
        False then the trip is finished.
        """
        return not self.unloading_point

    @property
    def failed(self) -> bool:
        """ Returns True if the trip unload_point is not in any storage """
        return False if self.active else not(Storage.objects.filter(
            territory__covers=self.unloading_point
        ).exists())

    @property
    def truck_max_weight(self) -> int:
        """ Returns max_weight of the model of the truck """
        return self.truck.max_weight

    @property
    def mineral_weight(self) -> int:
        """ Returns weight of mineral payload """
        return self.mineral.weight

    @property
    def overload(self) -> float:
        """ Returns % of truck.max_weight overloading """
        max_weight = self.truck_max_weight
        weight = self.mineral_weight
        if weight > max_weight:
            return int((weight - max_weight)*100/max_weight)
        return 0

    @property
    def truck_number(self) -> str:
        """ Returns the number of the truck """
        return self.truck.number

    @property
    def truck_model_title(self) -> str:
        """ Returns the title of the model of the truck """
        return self.truck.model_title

    @property
    def xy(self) -> Optional[str]:
        """ return X Y from unloading_point """
        if not self.unloading_point:
            return None
        return f'int({self.unloading_point.x}) int({self.unloading_point.y})'

    @xy.setter
    def xy(self, value: str) -> None:
        """ setter for unloading_point from X Y string """
        match = patterns.XY.search(value)
        if match:
            self.unloading_point = Point(int(match.group('x')), int(match.group('y')))
        else:
            raise ValueError(f'"{value}" is not a valid X Y Point')

    def __str__(self):
        return (f'{"Active t" if self.active else "T" }rip'
                f' {self.id} {self.mineral} {self.truck}'
                f' unloading_point={self.unloading_point}')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='%(app_label)s_%(class)s_only_one_truck_with_active_trip',
                fields=['truck'],
                condition=Q(unloading_point__isnull=True)
            )
        ]

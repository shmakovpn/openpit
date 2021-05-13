from typing import Any, Dict, Optional
from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import modelformset_factory
from django.forms.utils import ErrorList
from pit.models import Trip
import pit.patterns as patterns


class ValueWidget(forms.Widget):
    """
    Widget that just print value
    """
    input_type = None
    template_name = 'pit/value.html'


class TripIndexPageForm(forms.ModelForm):
    """ The form of the trip for the index page of the site """
    truck_number = forms.CharField(disabled=True,
                                   widget=ValueWidget,
                                   required=False,
                                   label='Бортовой номер')
    truck_model_title = forms.CharField(disabled=True,
                                        widget=ValueWidget,
                                        required=False,
                                        label='Модель')
    truck_max_weight = forms.CharField(disabled=True,
                                       widget=ValueWidget,
                                       required=False,
                                       label='Макс. грузоподъемность')
    mineral_weight = forms.CharField(disabled=True,
                                     widget=ValueWidget,
                                     required=False,
                                     label='Текущий вес')
    overload = forms.CharField(disabled=True,
                               widget=ValueWidget,
                               required=False,
                               label='Перегруз, %')
    xy = forms.CharField(label='Координаты разгрузки (x y)')

    def __init__(self, data: Optional[Any] = None, files: Optional[Any] = None, auto_id: str = 'id_%s',
                 prefix: Optional[Any] = None, initial: Optional[Any] = None,
                 error_class: Any = ErrorList, label_suffix: Optional[Any] = None,
                 empty_permitted: bool = False, instance: Optional[Any] = None,
                 use_required_attribute: Optional[Any] = None,
                 renderer: Optional[Any] = None) -> None:
        initial_dict: Dict[str, Any] = initial or {}
        if instance:
            initial_dict.update({
                'truck_number': instance.truck_number,
                'truck_model_title':
                    instance.truck_model_title,
                'truck_max_weight': instance.truck_max_weight,
                'mineral_weight': instance.mineral_weight,
                'overload': instance.overload,
                'xy': instance.xy,
            })
        super().__init__(data=data,
                         files=files,
                         auto_id=auto_id,
                         prefix=prefix,
                         initial=initial_dict,
                         error_class=error_class,
                         label_suffix=label_suffix,
                         empty_permitted=empty_permitted,
                         instance=instance,
                         use_required_attribute=use_required_attribute,
                         renderer=renderer)

    def clean_point(self):
        """ validate that xy is a valid XY point """
        if not patterns.XY.search(self.cleaned_data['xy']):
            raise ValidationError(f'"{self.cleaned_data["xy"]}" is not a valid X Y point')
        return self.cleaned_data['xy']

    def save(self, commit: bool = True) -> Any:
        """ save model """
        if self.is_valid():
            self.instance.xy = self.cleaned_data['xy']
        return super().save(commit=commit)

    class Meta:
        model = Trip
        fields = (
            'truck_number',
            'truck_model_title',
            'truck_max_weight',
            'mineral_weight',
            'overload',
            'xy',
        )


TripIndexPageFormSet = modelformset_factory(model=Trip,
                                            form=TripIndexPageForm,
                                            exclude=(),
                                            extra=0)

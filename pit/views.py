from typing import Any, Dict
from django.shortcuts import render
from django.views import View
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from pit.models import Trip, Storage
from pit.forms import TripIndexPageFormSet
from django.urls import reverse
from django.db.models import Sum, F, OuterRef, Subquery, Value, TextField
from django.db.models.functions import Coalesce, Concat, Cast
from pit.utils import factory_reset


class Index(View):
    """ index page """

    def get(self, request: HttpRequest) -> HttpResponse:
        context: Dict[str, Any] = {
            'formset': TripIndexPageFormSet(queryset=Trip.objects.filter(unloading_point__isnull=True))
        }
        return render(request, 'pit/index.html', context)

    def post(self, request: HttpRequest) -> HttpResponse:
        formset = TripIndexPageFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(reverse('report'))
        else:
            context: Dict[str, Any] = {
                'formset': formset
            }
            return render(request, 'pit/index.html', context)


class Report(View):
    """ results page """

    def get(self, request: HttpRequest) -> HttpResponse:
        weight_before = Coalesce(Sum('otherstorageincom__mineral__weight'), 0)
        sio2_before = Coalesce(Sum(F('otherstorageincom__mineral__weight') * F('otherstorageincom__mineral__sio2')), 0)
        fe_before = Coalesce(Sum(F('otherstorageincom__mineral__weight') * F('otherstorageincom__mineral__fe')), 0)
        weight_after = Subquery(
            Trip.objects.filter(
                unloading_point__isnull=False,  # exclude active trips
                unloading_point__intersects=OuterRef('territory')  # filter by intersection with the storage polygon
            ).annotate(
                mineral_weight=F('mineral__weight'),  # add weight field
                storage=OuterRef('pk')  # add storage id field (for GROUP BY)
            ).values(
                'storage'  # GROUP BY storage id
            ).annotate(
                total_weight=Coalesce(Sum('mineral_weight'), 0),
            ).values('total_weight')
        )
        sio2_after = Subquery(
            Trip.objects.filter(
                unloading_point__isnull=False,  # exclude active trips
                unloading_point__intersects=OuterRef('territory')  # filter by intersection with the storage polygon
            ).annotate(
                mineral_weight=F('mineral__weight'),  # add weight field
                mineral_sio2=F('mineral__sio2'),  # add sio2 field
                storage=OuterRef('pk')  # add storage id field (for GROUP BY)
            ).values(
                'storage'  # GROUP BY storage id
            ).annotate(
                total_sio2=Coalesce(Sum(F('mineral_weight') * F('mineral_sio2')), 0),
            ).values('total_sio2')
        )
        fe_after = Subquery(
            Trip.objects.filter(
                unloading_point__isnull=False,  # exclude active trips
                unloading_point__intersects=OuterRef('territory')  # filter by intersection with the storage polygon
            ).annotate(
                mineral_weight=F('mineral__weight'),  # add weight field
                mineral_fe=F('mineral__fe'),  # add fe field
                storage=OuterRef('pk')  # add storage id field (for GROUP BY)
            ).values(
                'storage'  # GROUP BY storage id
            ).annotate(
                total_fe=Coalesce(Sum(F('mineral_weight') * F('mineral_fe')), 0),
            ).values('total_fe')
        )

        report = Storage.objects.annotate(
            weight_before=weight_before,
            sio2_before=sio2_before,
            fe_before=fe_before,
            sum_weight_after=F('weight_before')+weight_after,
            sum_sio2_after=F('sio2_before')+sio2_after,
            sum_fe_after=F('fe_before')+fe_after,
            percent_sio2_after=Coalesce(F('sum_sio2_after')/F('sum_weight_after'), 0),
            percent_fe_after=Coalesce(F('sum_fe_after')/F('sum_weight_after'), 0),
            quality_after=Concat(
                Cast(F('percent_sio2_after'), output_field=TextField()),
                Cast(Value('% SiO2, '), output_field=TextField()),
                Cast(F('percent_fe_after'), output_field=TextField()),
                Cast(Value('% Fe'), output_field=TextField()),
            )
        ).values('title', 'weight_before', 'sum_weight_after', 'quality_after')

        context: Dict[str, Any] = {
            'report': report,
        }
        return render(request, 'pit/report.html', context)


class Reset(View):
    """ resets task to initial """
    def get(self, request: HttpRequest) -> HttpResponse:
        factory_reset(reset_admin=False)
        return HttpResponseRedirect(reverse('index'))

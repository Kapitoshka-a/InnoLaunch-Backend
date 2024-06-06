import django_filters
from .models import Establishment


class EstablishmentFilter(django_filters.FilterSet):
    amenities = django_filters.CharFilter(method='filter_amenities')
    services = django_filters.CharFilter(method='filter_services')
    type = django_filters.CharFilter(method='filter_type')
    price_category = django_filters.CharFilter(method='filter_price_category')
    capacity = django_filters.CharFilter(method='filter_capacity')

    class Meta:
        model = Establishment
        fields = ['type', 'amenities', 'services', 'is_recommended', 'price_category', 'capacity']

    def filter_amenities(self, queryset, name, value):
        amenities_list = value.split(';')
        queryset = queryset
        for amenity in amenities_list:
            queryset = queryset.filter(amenities__name__icontains=amenity)
        return queryset

    def filter_services(self, queryset, name, value):
        services_list = value.split(';')
        queryset = queryset
        for amenity in services_list:
            queryset = queryset.filter(services__name__icontains=amenity)
        return queryset

    def filter_type(self, queryset, name, value):
        types_list = value.split(';')
        return queryset.filter(type__in=types_list)

    def filter_price_category(self, queryset, name, value):
        price_category_list = value.split(';')
        return queryset.filter(price_category__price_range__in=price_category_list)

    def filter_capacity(self, queryset, name, capacity):
        return queryset.filter(capacity__gte=capacity)

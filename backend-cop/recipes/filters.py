# Сторонние библиотеки
from django_filters import rest_framework as filters

# Наши (локальные) импорты
from .models import Ingredient


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = ["name"]

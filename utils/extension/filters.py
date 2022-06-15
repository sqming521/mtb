from rest_framework.filters import BaseFilterBackend
from apps.base import models


class SelfFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(mtb_user_id=request.user.user_id)

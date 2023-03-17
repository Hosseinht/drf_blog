from django.contrib.postgres.search import SearchVector
from django.utils import timezone
from django_filters import CharFilter, FilterSet
from rest_framework.exceptions import APIException

from blog.models import Post


class PostFilter(FilterSet):
    """
    For example, if the URL to access the endpoint is https://example.com/api/posts/?author__in=john,amy, then value
    in the filter_author__in method will be the string "john,amy", which contains a comma-separated list of usernames.
    """

    search = CharFilter(method="filter_search")
    category__name = CharFilter(method="filter_category__name")
    author__in = CharFilter(method="filter_author__in")
    created_at__range = CharFilter(method="filter_created_at__range")

    def filter_category__name(self, queryset, name, value):
        return queryset.filter(category__name__icontains=value)

    def filter_author__in(self, queryset, name, value):
        print(value)
        """
        **value**:
            in this endpoint value is john and amy
            https://example.com/api/posts/?author__in=john,amy

        **queryset**:
            queryset pass to the PostFilter in the get_posts method in selectors.py
        """
        limit = 10
        authors = value.split(",")
        if len(authors) > limit:
            raise APIException(f"You cannot add more than {len(authors)} usernames")
        return queryset.filter(author__email__in=authors)

    def filter_created_at__range(self, queryset, name, value):
        limit = 2
        created_at__in = value.split(",")
        if len(created_at__in) > limit:
            raise APIException("Please just add two created_at with , in the middle")

        created_at_0, created_at_1 = created_at__in

        if not created_at_1:
            created_at_1 = timezone.now()

        if not created_at_0:
            return queryset.filter(created_at__date__lt=created_at_1)

        return queryset.filter(created_at__date__range=(created_at_0, created_at_1))

    def filter_search(self, queryset, name, value):
        print(queryset)
        return queryset.annotate(search=SearchVector("title", config="simple")).filter(
            search=value
        )

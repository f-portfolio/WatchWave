import django_filters
from channels.models import VideoPost

class VideoPostFilter(django_filters.FilterSet):
    channel = django_filters.CharFilter(field_name='channel__name', lookup_expr='icontains')
    publisher = django_filters.CharFilter(field_name='publisher__username', lookup_expr='icontains')
    title = django_filters.CharFilter(lookup_expr='icontains')
    slog = django_filters.CharFilter(lookup_expr='icontains')
    hls_master_playlist = django_filters.CharFilter(lookup_expr='icontains')
    snippet = django_filters.CharFilter(lookup_expr='icontains')
    meta_description = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    reference = django_filters.CharFilter(lookup_expr='icontains')
    cast = django_filters.CharFilter(lookup_expr='icontains')
    #title = django_filters.CharFilter(lookup_expr='icontains')
    language_video = django_filters.CharFilter(field_name='language_video__name', lookup_expr='icontains')
    categorys = django_filters.CharFilter(field_name='categorys__name', lookup_expr='icontains')
    tags = django_filters.CharFilter(field_name='tags__name', lookup_expr='icontains')
    supervisor_to_confirm = django_filters.CharFilter(field_name='supervisor_to_confirm__user__username', lookup_expr='icontains')
    supervisor_to_pined = django_filters.CharFilter(field_name='supervisor_to_pined__user__username', lookup_expr='icontains')
    published_date = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = VideoPost
        fields = ['channel', 'publisher', 'slog', 'hls_master_playlist', 
                  'language_video', 'title', 'snippet', 'meta_description', 
                  'description', 'reference', 'cast', 'categorys', 
                  'tags', 'supervisor_to_confirm', 'supervisor_to_pined',]
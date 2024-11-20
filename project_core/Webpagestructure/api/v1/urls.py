from Webpagestructure.api.v1.views import *
from django.urls import path


app_name = 'api-v1'

urlpatterns = [
    path('site_header/',SiteHeaderModelViewSet.as_view({'get':'list', 'post':'create'}), name="site_header-list"),
    path('site_header/<int:pk>/',SiteHeaderModelViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name="site_header-detail"),
    
    path('link_section_in_footer/',LinkSectionInFooterModelViewSet.as_view({'get':'list', 'post':'create'}), name="link_section_in_footer-list"),
    path('link_section_in_footer/<int:pk>/',LinkSectionInFooterModelViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name="link_section_in_footer-detail"),
    
    path('social_section_in_footer/',SocialSectionInFooterModelViewSet.as_view({'get':'list', 'post':'create'}), name="social_section_in_footer-list"),
    path('social_section_in_footer/<int:pk>/',SocialSectionInFooterModelViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name="social_section_in_footer-detail"),
    
    path('site_footer/',SiteFooterModelViewSet.as_view({'get':'list', 'post':'create'}), name="site_footer-list"),
    path('site_footer/<int:pk>/',SiteFooterModelViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name="site_footer-detail"),
    
    path('site_theme/',SiteThemeModelViewSet.as_view({'get':'list', 'post':'create'}), name="site_theme-list"),
    path('site_theme/<int:pk>/',SiteThemeModelViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name="site_theme-detail"),
    
    path('site_structure/',SiteStructureModelViewSet.as_view({'get':'list', 'post':'create'}), name="site_structure-list"),
    path('site_structure/<int:pk>/',SiteStructureModelViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name="site_structure-detail"),
    


    path('box_management/', BoxManagementModelViewSet.as_view({'get':'list', 'post':'create'}), name="box_management-list"),
    path('box_management/<int:pk>/', BoxManagementModelViewSet.as_view({'get':'retrieve', 'put':'update', 'patch':'partial_update', 'delete':'destroy'}), name="box_management-detail"),
    
    path('box_video_items_by_hand/', VideoItemsBoxByHandModelViewSet.as_view({'get':'list', 'post':'create'}), name="box_items_by_hand-list"),
    path('box_video_items_by_hand/<int:pk>/', VideoItemsBoxByHandModelViewSet.as_view({'get':'retrieve', 'put':'update', 'patch':'partial_update', 'delete':'destroy'}), name="box_items_by_hand-detail"),

    path('location_box/', LocationBoxModelViewSet.as_view({'get':'list', 'post':'create'}), name="location_box-list"),
    path('location_box/<int:pk>/', LocationBoxModelViewSet.as_view({'get':'retrieve', 'put':'update', 'patch':'partial_update', 'delete':'destroy'}), name="location_box-detail"),

    path('offer_for_box_from_owner_channel/',OfferForBoxFromOwnerChannelModelViewSet.as_view({'get':'list', 'post':'create'}), name="offer_for_box_from_owner_channel-list"),
    path('offer_for_box_from_owner_channel/<int:pk>/', OfferForBoxFromOwnerChannelModelViewSet.as_view({'get':'retrieve', 'put':'update', 'patch':'partial_update', 'delete':'destroy'}), name="offer_for_box_from_owner_channel-detail"),

]

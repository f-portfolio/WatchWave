from django.urls import path, include
from .views import *

app_name = 'api-v1'

urlpatterns = [    
    path('tag/',TagModelViewSet.as_view({'get':'list', 'post':'create'}), name="tag-list"),
    path('tag/<int:pk>/',TagModelViewSet.as_view({'get':'retrieve', 'put':'update', 'patch':'partial_update', 'delete':'destroy'}), name="tag-detail"),
    path('tag/<str:tag_name>/', CheckIfTagIsConfirmedSView.as_view()),
    path('top_tags/', TopTagsAPIView.as_view(), name="top_tag"),
    path('tags_by_filter_categorys_and_posts/', TagCategoryModelViewSet.as_view({'get': 'list'}), name='tag-by-filter'),
    path('tags_add_by_filter_categorys_to_posts/', AddTagToPostsByCategoryAPIView.as_view(), name='add-tag-to-posts'),
    path('tags_remove_by_filter_categorys_to_posts/', RemoveTagToPostsByCategoryAPIView.as_view(), name='remove-tag-to-posts'),
    path('tags_update_by_filter_categorys_to_posts/', UpdateTagForPostsByCategoryAPIView.as_view(), name='update-tag-to-posts'),
    path('tags_merge_in_all_categorys_to_posts/', ReplaceTagsWithNewTagInAllCategoryAPIView.as_view(), name='merge-tag-to-posts'),


    path('language/',LanguageModelViewSet.as_view({'get':'list', 'post':'create'}), name="language-of-video-list"),
    path('language/<int:pk>/',LanguageModelViewSet.as_view({'get':'retrieve', 'put':'update', 'patch':'partial_update', 'delete':'destroy'}), name="language-of-video-detail"),
    
    path('category/',CategoryModelViewSet.as_view({'get':'list', 'post':'create'}), name="category-of-post-list"),
    path('category/<int:pk>/',CategoryModelViewSet.as_view({'get':'retrieve', 'put':'update', 'patch':'partial_update', 'delete':'destroy'}), name="category-of-post-detail"),

    path('type_of_url/',TypeOfURLModelViewSet.as_view({'get':'list', 'post':'create'}), name="type_of_url-list"),
    path('type_of_url/<int:pk>/',TypeOfURLModelViewSet.as_view({'get':'retrieve', 'put':'update', 'patch':'partial_update'}), name="type_of_url-detail"),
   
    path('url_/',URLModelViewSet.as_view({'get':'list', 'post':'create'}), name="url-list"),
    path('url_/<int:pk>/',URLModelViewSet.as_view({'get':'retrieve', 'put':'update', 'patch':'partial_update'}), name="url-detail"),

    path('type_of_author/',TypeOfAuthorModelViewSet.as_view({'get':'list', 'post':'create'}), name="type_of_author-list"),
    path('type_of_author/<int:pk>/',TypeOfAuthorModelViewSet.as_view({'get':'retrieve', 'put':'update', 'patch':'partial_update'}), name="type_of_author-detail"),
    
    path('meta_kword/',MetaKwordModelViewSet.as_view({'get':'list', 'post':'create'}), name="meta_kword-list"),
    path('meta_kword/<int:pk>/',MetaKwordModelViewSet.as_view({'get':'retrieve', 'put':'update', 'patch':'partial_update'}), name="meta_kword-detail"),
    
    path('link_of_posts/',LinkOfPostsModelViewSet.as_view({'get':'list', 'post':'create'}), name="link_of_posts-list"),
    path('link_of_posts/<int:pk>/',LinkOfPostsModelViewSet.as_view({'get':'retrieve', 'put':'update', 'patch':'partial_update'}), name="link_of_posts-detail"),

]

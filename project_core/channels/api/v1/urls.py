from channels.api.v1.views import *
from django.urls import path

app_name = 'api-v1'

history_list = HistoryViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

history_detail = HistoryViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update'
})

urlpatterns = [
    # channels
    path('channels/', ChannelModelViewSet.as_view({'get':'list', 'post':'create'}), name='channel-list-create'),
    path('channels/<int:pk>/', ChannelModelViewSet.as_view({'get':'retrieve', 'put':'update', 'patch':'partial_update', 'delete':'destroy'}), name='channel-detail'),
    path('increase_channel_view/<int:channel_id>/', IncreaseChannelViewCountView.as_view(), name='increase_channel_view_list'),
    
    path('channels_edit_body/<int:pk>/', ChannelEditBodyModelViewSet.as_view({'get':'retrieve', 'put':'update', 'patch':'partial_update', 'delete':'destroy'}), name='channel-detail-update-body'),
    path('channels_edit_avatar/<int:pk>/', ChannelEditAvatarModelViewSet.as_view({'get':'retrieve', 'put':'update', 'patch':'partial_update', 'delete':'destroy'}), name='channel-detail-update-avatar'),
    path('channels_edit_baner/<int:pk>/', ChannelEditBanerModelViewSet.as_view({'get':'retrieve', 'put':'update', 'patch':'partial_update', 'delete':'destroy'}), name='channel-detail-update-baner'),
    
    
    # subscriptions channels
    path('subscriptions/', SubscriptionModelViewSet.as_view({'get':'list', 'post':'create'}), name='subscription-list-create'),
    path('subscriptions/<int:pk>/', SubscriptionModelViewSet.as_view({'get':'retrieve', 'delete':'destroy'}), name='subscription-detail'),

    # video post
    path('video_posts/', VideoPostModelViewSet.as_view({'get':'list', 'post':'create'}), name='videopost-list-create'),
    path('video_posts/<int:pk>/', VideoPostModelViewSet.as_view({'get':'retrieve', 'put':'update', 'patch':'partial_update', 'delete':'destroy'}), name='videopost-detail-update-delete'),
    path('video_posts_edit/<int:pk>/', VideoPostEditModelViewSet.as_view({'get':'retrieve', 'put':'update', 'patch':'partial_update', 'delete':'destroy'}), name='videopost-detail-update-delete'),
    path('increase_video_post_view/<int:video_id>/', IncreaseVideoPostCountView.as_view(), name='increase_video_post_view_list'),

    path('video_posts_edit_body/<int:pk>/', VideoPostEditBodyModelViewSet.as_view({'get':'retrieve', 'put':'update', 'patch':'partial_update', 'delete':'destroy'}), name='videopost-detail-update-body'),
    path('video_posts_edit_cover/<int:pk>/', VideoPostEditCoverModelViewSet.as_view({'get':'retrieve', 'put':'update', 'patch':'partial_update', 'delete':'destroy'}), name='videopost-detail-update-cover'),
    path('video_posts_edit_video/<int:pk>/', VideoPostEditVideoModelViewSet.as_view({'get':'retrieve', 'put':'update', 'patch':'partial_update', 'delete':'destroy'}), name='videopost-detail-update-video'),
    
    path('popular-videos/', PopularVideoPostsModelViewSet.as_view({'get': 'list'}), name='popular_videos_api'),
    path('most-liked-videos/', MostLikedVideoPostsModelViewSet.as_view({'get': 'list'}), name='most_liked_videos_api'),
    
    # like of video post
    path('like_video_post/', LikeModelViewSet.as_view({'get':'list', 'post':'create'}), name='like-video-post'),
    path('like_video_post/<int:pk>/',LikeModelViewSet.as_view({'get':'retrieve'}), name="like-video-post"),
    
    # dis like of video post
    path('dislike_video_post/', DisLikeModelViewSet.as_view({'get':'list', 'post':'create'}), name='dislike-video-post'),
    path('dislike_video_post/<int:pk>/', DisLikeModelViewSet.as_view({'get':'retrieve'}), name="dislike-video-post"),

    # save of video post
    path('save_video_post/', SaveModelViewSet.as_view({'get':'list', 'post':'create'}), name='save-video-post'),
    path('save_video_post/<int:pk>/', SaveModelViewSet.as_view({'get':'retrieve', 'delete':'destroy'}), name="save-video-post"),

    # comments of video post
    path('comments/', CommentModelViewSet.as_view({'get':'list', 'post':'create'}), name='comment-list-create'),
    path('comments/<int:pk>/', CommentModelViewSet.as_view({'get':'retrieve', 'put':'update', 'patch':'partial_update', 'delete':'destroy'}), name='comment-detail'),

    # send notifications for important event :)
    path('notifications/', NotificationViewSet.as_view({ 'get': 'list'}), name='notification-list'),
    path('notifications/mark_as_read/', NotificationViewSet.as_view({'post': 'mark_as_read'}), name='notification-mark-as-read'),

    # play list of video post of channel
    path('play_list/', PlayListModelViewSet.as_view({'get':'list', 'post':'create'}), name='play_list-list'),
    path('play_list/<int:pk>/', PlayListModelViewSet.as_view({'get':'retrieve', 'put':'update', 'patch':'partial_update', 'delete':'destroy'}), name='play_list-detail'),

    # history of user's video_post
    path('histories/', history_list, name='history-list'),
    path('histories/<int:pk>/', history_detail, name='history-detail'),

    path('recommender_videos/<int:video_id>/', RecommenderVideoModelViewSet.as_view({'get':'list'}), name='recommender_videos-list'),

    path('special_section/', SpecialSectionModelViewSet.as_view({'get':'list', 'post':'create'}), name='special_section-list'),
    path('special_section/<int:pk>/', SpecialSectionModelViewSet.as_view({'get':'retrieve', 'put':'update', 'patch':'partial_update', 'delete':'destroy'}), name='special_section-detail'),

    path('admins/', AdminsOfChannelViewSet.as_view({'get': 'list', 'post': 'create'}), name='admins-list-create'),
    path('admins/<int:pk>/', AdminsOfChannelViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='admins-detail'),
    
    path('socials/', SocialOfChanneViewSet.as_view({'get': 'list', 'post': 'create'}), name='socials-list-create'),
    path('socials/<int:pk>/', SocialOfChanneViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='socials-detail'),

    path('user/<int:user_id>/channels/', UserChannelsView.as_view(), name='user-channels'), # <- 'user-owner-or-admin-of-channels'
    path('user/<int:user_id>/general_info/', GeneralInfoView.as_view(), name='user-general_info'), # <- 'general information for admin panel box'

]


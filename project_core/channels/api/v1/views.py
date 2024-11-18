import subprocess, os, logging
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser
from rest_framework import status, mixins, viewsets, generics, views
from .serializers import  *
from channels.models import *
from rest_framework.response import Response
from .tasks import save_video
from .permissions import *
from django.core.files.storage import default_storage
from django.conf import settings
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import filters
from .filters import VideoPostFilter
from django.http import JsonResponse
from django.views import View
from django.utils import timezone
from datetime import timedelta
from .paginations import *
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cache_time = 60 * 15

def process_video(video_id):
    try:
        video = VideoPost.objects.get(id=video_id)
        input_path = video.video.path  # Use the .path attribute to get the file path as a string
        output_path = os.path.join(settings.MEDIA_ROOT, f'videos/{video.id}/')
        master_playlist_path = os.path.join(output_path, 'master.m3u8')

        # Ensure the output directory exists
        os.makedirs(output_path, exist_ok=True)
        
        command = [
            'ffmpeg', '-i', input_path,
            '-vf', 'scale=-2:720', '-c:v', 'libx264', '-b:v', '3000k', '-hls_time', '10', '-hls_playlist_type', 'vod', '-f', 'hls', os.path.join(output_path, '720p.m3u8'),
            '-vf', 'scale=-2:480', '-c:v', 'libx264', '-b:v', '1500k', '-hls_time', '10', '-hls_playlist_type', 'vod', '-f', 'hls', os.path.join(output_path, '480p.m3u8'),
            '-vf', 'scale=-2:360', '-c:v', 'libx264', '-b:v', '800k', '-hls_time', '10', '-hls_playlist_type', 'vod', '-f', 'hls', os.path.join(output_path, '360p.m3u8'),
            '-vf', 'scale=-2:240', '-c:v', 'libx264', '-b:v', '500k', '-hls_time', '10', '-hls_playlist_type', 'vod', '-f', 'hls', os.path.join(output_path, '240p.m3u8')
        ]

        # Execute the FFmpeg command
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"FFmpeg error: {result.stderr}")
            raise Exception(f"FFmpeg error: {result.stderr}")

        # Create the master playlist
        master_playlist_content = """
        #EXTM3U
        #EXT-X-STREAM-INF:BANDWIDTH=3000000,RESOLUTION=1280x720
        720p.m3u8
        #EXT-X-STREAM-INF:BANDWIDTH=1500000,RESOLUTION=854x480
        480p.m3u8
        #EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=640x360
        360p.m3u8
        #EXT-X-STREAM-INF:BANDWIDTH=500000,RESOLUTION=426x240
        240p.m3u8
        """
        with open(master_playlist_path, 'w') as f:
            f.write(master_playlist_content.strip())

        # Calculate the relative path for the master playlist
        relative_master_playlist_path = os.path.relpath(master_playlist_path, settings.MEDIA_ROOT).replace("\\", "/")
        logger.info(f"Master playlist path: {relative_master_playlist_path}")

        # Update the VideoPost object
        video.hls_master_playlist = relative_master_playlist_path
        video.save()
        logger.info(f"Video {video_id} updated with HLS master playlist path.")

    except Exception as e:
        logger.error(f"An error occurred while processing the video: {str(e)}")


class ChannelModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsGetOnly | IsAdminUser, IsOwnerOrReadOnly]
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    pagination_class = CustomPageNumberPagination
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['owner', 'confirm_to_channel', 'is_favorite', 'activation', 'categorys', ]
    search_fields = ['owner__user__username', 'name', 'handle', 'description', 
                     'supervisor_to_confirm__user__username', 
                     'supervisor_to_favorited__user__username', 'categorys__name', ]
    ordering_fields = ['-created_date']

    @method_decorator(cache_page(cache_time, key_prefix="channel_list"))  
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        serializer.save()
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # cache.delete('video_list')
        cache.clear()
        self.list(request, *args, **kwargs)  
        return response
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        cache.clear()
        self.list(request, *args, **kwargs)  
        return Response({
            "message": "Channel deleted successfully."
        }, status=status.HTTP_200_OK)


class ChannelEditBodyModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsGetOnly | IsAdminUser, IsOwnerOrReadOnly]
    queryset = Channel.objects.all()
    serializer_class = ChannelEditBodySerializer
    pagination_class = CustomPageNumberPagination
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['owner', 'confirm_to_channel', 'is_favorite', 'activation', 'categorys', ] 
    search_fields = ['owner__user__username', 'name', 'handle', 'description', 
                     'supervisor_to_confirm__user__username', 
                     'supervisor_to_favorited__user__username', 'categorys__name', ]
    ordering_fields = ['-created_date']

    @method_decorator(cache_page(cache_time, key_prefix="channel_list"))  
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        serializer.save()
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        cache.clear()
        self.list(request, *args, **kwargs)  
        return Response({
            "message": "The object was successfully updated.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "message": "Channel deleted successfully."
        }, status=status.HTTP_200_OK)

class ChannelEditAvatarModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsGetOnly | IsAdminUser, IsOwnerOrReadOnly]
    queryset = Channel.objects.all()
    serializer_class = ChannelEditAvatarSerializer
    pagination_class = CustomPageNumberPagination
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['owner', 'confirm_to_channel', 'is_favorite', 'activation', 'categorys', ] 
    search_fields = ['owner__user__username', 
                     'name', 'handle', 'description', 'supervisor_to_confirm__user__username', 
                     'supervisor_to_favorited__user__username', 'categorys__name', ]
    ordering_fields = ['-created_date']

    @method_decorator(cache_page(cache_time, key_prefix="channel_list")) 
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        serializer.save()
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        cache.clear()
        self.list(request, *args, **kwargs)  
        return Response({
            "message": "The object was successfully updated.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "message": "Channel deleted successfully."
        }, status=status.HTTP_200_OK)

class ChannelEditBanerModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsGetOnly | IsAdminUser, IsOwnerOrReadOnly]
    queryset = Channel.objects.all()
    serializer_class = ChannelBanerSerializer
    pagination_class = CustomPageNumberPagination
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['owner', 'confirm_to_channel', 'is_favorite', 'activation', 'categorys', ] 
    search_fields = ['owner__user__username', 
                     'name', 'handle', 'description', 'supervisor_to_confirm__user__username', 
                     'supervisor_to_favorited__user__username', 'categorys__name', ]
    ordering_fields = ['-created_date']

    @method_decorator(cache_page(cache_time, key_prefix="channel_list"))  
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        cache.clear()
        self.list(request, *args, **kwargs)  
        return Response({
            "message": "The object was successfully updated.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "message": "Channel deleted successfully."
        }, status=status.HTTP_200_OK)


class SubscriptionModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerSubOrReadOnly]
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    pagination_class = CustomPageNumberPagination
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user', 'channel']
    search_fields = ['user__user__username', 'channel__name',]
    #ordering_fields = ['-created_date']

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user.profile)
        except ValidationError as e:
            raise ValidationError({'detail': e.detail})
        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response({"detail": "Successfully subscribed.", "data": serializer.data}, status=status.HTTP_201_CREATED, headers=headers)
            except ValidationError as e:
                return Response({"detail": "Subscription failed.", "errors": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
            return Response({"detail": "Successfully unsubscribed."}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"detail": "Unsubscription failed.", "errors": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class VideoPostModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsGetOnly | IsAdminUser, IsOwnerOrSupervisor]
    queryset = VideoPost.objects.all()
    serializer_class = VideoPostSerializer
    pagination_class = CustomPageNumberPagination
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['channel', 'status', 'confirm_to_post', 'is_pined', 
                        'publisher' , 'supervisor_to_confirm', 'supervisor_to_pined' , 
                        'categorys', 'sub_categorys', 'sub_sub_categorys',
                        'tags', 'language_video']
    
    search_fields = ['channel__name', 'channel__owner__user__username', 
                     'channel__handle', 'channel__description', 
                     'channel__supervisor_to_confirm__user__username', 
                     'channel__supervisor_to_favorited__user__username', 
                     
                     'publisher__user__username', 'slog', 
                     'hls_master_playlist', 'language_video__name', 
                     'title', 'snippet', 'meta_description', 'description', 
                     'reference', 'cast', 'categorys__name', 'tags__name',
                     'sub_categorys__name', 'sub_sub_categorys__name',
                     'supervisor_to_confirm__user__username', 
                     'supervisor_to_pined__user__username',]
    ordering_fields = ['-published_date']

    @method_decorator(cache_page(cache_time, key_prefix="video_list"))  
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        video = serializer.save()
        process_video(video.id)
        # notify_followers(video)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # cache.delete('video_list')
        cache.clear()
        
        # Re-cache video list
        self.list(request, *args, **kwargs)  
        return Response({
            "message": "Video uploaded and processing started",
            "video": response.data
        }, status=status.HTTP_201_CREATED)
    
    def get_queryset(self):
        queryset = VideoPost.objects.filter(status=False)
        for videoPost in queryset:
            if videoPost.published_date is not None:
                if videoPost.published_date <= timezone.now():
                    #print('yessssss')
                    videoPost.status = True
                    videoPost.save()
        return VideoPost.objects.filter(status=True, confirm_to_post=True)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        cache.clear()
        self.list(request, *args, **kwargs)  
        
        return Response({
            "message": "The object was successfully updated.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        cache.clear()
        self.list(request, *args, **kwargs)  
        return Response({
            "message": "Video removed successfully."
        }, status=status.HTTP_200_OK)


class VideoPostEditModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsGetOnly | IsAdminUser, IsOwnerOrSupervisor]
    queryset = VideoPost.objects.all()
    serializer_class = VideoPostEditSerializer
    pagination_class = CustomPageNumberPagination
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['channel', 'status', 'confirm_to_post', 'is_pined', 
                        'publisher' , 'supervisor_to_confirm', 'supervisor_to_pined' , 
                        'tags', 'categorys', 'language_video']
    
    search_fields = ['channel__name', 'channel__owner__user__username', 
                     'channel__handle', 'channel__description', 
                     'channel__supervisor_to_confirm__user__username', 
                     'channel__supervisor_to_favorited__user__username', 
                     
                     'publisher__user__username', 'slog', 
                     'hls_master_playlist', 'language_video__name', 
                     'title', 'snippet', 'meta_description', 'description', 
                     'reference', 'cast', 'categorys__name', 'tags__name',
                     'supervisor_to_confirm__user__username', 
                     'supervisor_to_pined__user__username',]
    ordering_fields = ['-published_date']

    @method_decorator(cache_page(cache_time, key_prefix="video_list"))  
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            "message": "Video uploaded and processing started",
            "video": response.data
        }, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        queryset = VideoPost.objects.filter(status=False)
        for videoPost in queryset:
            if videoPost.published_date is not None:
                if videoPost.published_date <= timezone.now():
                    videoPost.status = True
                    videoPost.save()
        return VideoPost.objects.filter(status=True, confirm_to_post=True)
    
    def perform_update(self, serializer):
        video = serializer.save()
        # cache.delete('video_list')  
        cache.clear()
        #self.list(request, *args, **kwargs)  

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "message": "Video removed successfully."
        }, status=status.HTTP_200_OK)

class VideoPostEditBodyModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsGetOnly | IsAdminUser, IsOwnerOrSupervisor]
    queryset = VideoPost.objects.all()
    serializer_class = VideoPostEditBodySerializer
    pagination_class = CustomPageNumberPagination
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['channel', 'status', 'confirm_to_post', 'is_pined', 
                        'publisher' , 'supervisor_to_confirm', 'supervisor_to_pined' , 
                        'tags', 'categorys', 'language_video']
    
    search_fields = ['channel__name', 'channel__owner__user__username', 
                     'channel__handle', 'channel__description', 
                     'channel__supervisor_to_confirm__user__username', 
                     'channel__supervisor_to_favorited__user__username', 
                     
                     'publisher__user__username', 'slog', 
                     'hls_master_playlist', 'language_video__name', 
                     'title', 'snippet', 'meta_description', 'description', 
                     'reference', 'cast', 'categorys__name', 'tags__name',
                     'supervisor_to_confirm__user__username', 
                     'supervisor_to_pined__user__username',]
    ordering_fields = ['-published_date']
    
    @method_decorator(cache_page(cache_time, key_prefix="video_list"))  
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            "message": "Video uploaded and processing started",
            "video": response.data
        }, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        queryset = VideoPost.objects.filter(status=False)
        for videoPost in queryset:
            if videoPost.published_date is not None:
                if videoPost.published_date <= timezone.now() :
                    #print('yessssss')
                    videoPost.status = True
                    videoPost.save()
        
        return VideoPost.objects.filter(status=True, confirm_to_post=True)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        cache.clear()
        self.list(request, *args, **kwargs)  
        
        return Response({
            "message": "The object was successfully updated.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "message": "Video removed successfully."
        }, status=status.HTTP_200_OK)

class VideoPostEditCoverModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsGetOnly | IsAdminUser, IsOwnerOrSupervisor]
    queryset = VideoPost.objects.all()
    serializer_class = VideoPostEditCoverSerializer
    pagination_class = CustomPageNumberPagination
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['channel', 'status', 'confirm_to_post', 'is_pined', 
                        'publisher' , 'supervisor_to_confirm', 'supervisor_to_pined' , 
                        'tags', 'categorys', 'language_video']
    
    search_fields = ['channel__name', 'channel__owner__user__username', 
                     'channel__handle', 'channel__description', 
                     'channel__supervisor_to_confirm__user__username', 
                     'channel__supervisor_to_favorited__user__username', 
                     
                     'publisher__user__username', 'slog', 
                     'hls_master_playlist', 'language_video__name', 
                     'title', 'snippet', 'meta_description', 'description', 
                     'reference', 'cast', 'categorys__name', 'tags__name',
                     'supervisor_to_confirm__user__username', 
                     'supervisor_to_pined__user__username',]
    ordering_fields = ['-published_date']

    @method_decorator(cache_page(cache_time, key_prefix="video_list"))  
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
       
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            "message": "Video uploaded and processing started",
            "video": response.data
        }, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        queryset = VideoPost.objects.filter(status=False)
        for videoPost in queryset:
            if videoPost.published_date is not None:
                if videoPost.published_date <= timezone.now():
                    videoPost.status = True
                    videoPost.save()
        
        return VideoPost.objects.filter(status=True, confirm_to_post=True)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        cache.clear()
        self.list(request, *args, **kwargs)  
        
        return Response({
            "message": "The object was successfully updated.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "message": "Video removed successfully."
        }, status=status.HTTP_200_OK)

class VideoPostEditVideoModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsGetOnly | IsAdminUser, IsOwnerOrSupervisor]
    queryset = VideoPost.objects.all()
    serializer_class = VideoPostEditVideoSerializer
    pagination_class = CustomPageNumberPagination
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['channel', 'status', 'confirm_to_post', 'is_pined', 
                        'publisher' , 'supervisor_to_confirm', 'supervisor_to_pined' , 
                        'tags', 'categorys', 'language_video']
    
    search_fields = ['channel__name', 'channel__owner__user__username', 
                     'channel__handle', 'channel__description', 
                     'channel__supervisor_to_confirm__user__username', 
                     'channel__supervisor_to_favorited__user__username', 
                     
                     'publisher__user__username', 'slog', 
                     'hls_master_playlist', 'language_video__name', 
                     'title', 'snippet', 'meta_description', 'description', 
                     'reference', 'cast', 'categorys__name', 'tags__name',
                     'supervisor_to_confirm__user__username', 
                     'supervisor_to_pined__user__username',]
    ordering_fields = ['-published_date']

    @method_decorator(cache_page(cache_time, key_prefix="video_list"))  
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        video = serializer.save()
        process_video(video.id)
        # notify_followers(video)
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            "message": "Video uploaded and processing started",
            "video": response.data
        }, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        queryset = VideoPost.objects.filter(status=False)
        for videoPost in queryset:
            if videoPost.published_date is not None:
                if videoPost.published_date <= timezone.now():
                    videoPost.status = True
                    videoPost.save()
        
        return VideoPost.objects.filter(status=True, confirm_to_post=True)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        serializer.save()
        cache.clear()
        self.list(request, *args, **kwargs)  
        
        return Response({
            "message": "The object was successfully updated.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "message": "Video removed successfully."
        }, status=status.HTTP_200_OK)


class CommentModelViewSet(viewsets.ModelViewSet):
    #permission_classes = [IsGetOnly, IsOwnerCommentOrStaff]
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    pagination_class = CustomPageNumberPagination
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['confirm_to_comment', 'video_post', 'uper_comment',
                        'supervisor_to_confirm' , 'user']
    search_fields = ['user__user__username', 'video_post__title', 
                     'uper_comment__comment', 'comment', 
                     'supervisor_to_confirm__user__username', ]
    ordering_fields = ['-created_date']


class LikeModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    # permission_classes = [IsStaff]
    # permission_classes = [IsGetOnly|IsAdminUser]
    serializer_class = LikeSerializer
    queryset = Like.objects.all()
    pagination_class = CustomPageNumberPagination
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user', 'video_post']
    search_fields = ['user__user__username', 'video_post__title',]
    #ordering_fields = ['-created_date']


class DisLikeModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    # permission_classes = [IsStaff]
    # permission_classes = [IsGetOnly|IsAdminUser]
    serializer_class = DisLikeSerializer
    queryset = Dislike.objects.all()
    pagination_class = CustomPageNumberPagination
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user', 'video_post']
    search_fields = ['user__user__username', 'video_post__title',]
    #ordering_fields = ['-created_date']


class SaveModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    # permission_classes = [IsStaff]
    # permission_classes = [IsGetOnly|IsAdminUser]
    serializer_class = SaveSerializer
    queryset = Save.objects.all()
    pagination_class = CustomPageNumberPagination
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user', 'video_post']
    search_fields = ['user__user__username', 'video_post__title',]
    #ordering_fields = ['-created_date']


class NotificationViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions for the Notification model.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]  # Restrict access to authenticated users
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_read']
    search_fields = ['message']
    ordering_fields = ['-created_at']

    def get_queryset(self):
        """
        This view should return a list of all notifications for the currently authenticated user's profile.
        """
        user_profile = self.request.user.profile  # Access the related Profile instance
        return Notification.objects.filter(user=user_profile)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_as_read(self, request, *args, **kwargs):
        """
        Custom action to mark all notifications as read for the authenticated user's profile.

        This method will be accessible via a POST request to the 'mark_as_read' endpoint.
        """
        user_profile = self.request.user.profile  # Access the related Profile instance
        # Update all unread notifications for the user's profile to be marked as read
        Notification.objects.filter(user=user_profile, is_read=False).update(is_read=True)
        # Return a success response
        return Response({"status": "notifications marked as read"}, status=status.HTTP_200_OK)


class PlayListModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerCreatorOrSupervisor, IsGetOnly|IsAdminUser]
    queryset = PlayList.objects.all()
    serializer_class = PlayListSerializer
    pagination_class = CustomPageNumberPagination
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['channel', 'creator', 'play_list_videos']
    search_fields = ['channel__name', 'creator__user__username', 
                     'package_name', 'package_description', 'play_list_videos__title']
    ordering_fields = ['-created_date']

    @method_decorator(cache_page(cache_time, key_prefix="playList_video_list"))  
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class HistoryViewSet(viewsets.ModelViewSet):
    serializer_class = HistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user', 'video']
    ordering_fields = ['-id'] #ordering_fields = ['-last_viewed']

    def get_queryset(self):
        # Return history records only for the authenticated user
        return History.objects.filter(user=self.request.user.profile)

    def perform_create(self, serializer):
        # Ensure that the history entry is associated with the authenticated user
        serializer.save(user=self.request.user.profile)


class RecommenderVideoModelViewSet(viewsets.ModelViewSet):
    serializer_class = VideoPostSerializer
    queryset = VideoPost.objects.all()
    pagination_class = CustomPageNumberPagination
    
    def get_queryset(self):
        video_id = self.kwargs.get('video_id')
        video = get_object_or_404(VideoPost, id=video_id)
        
        related_videos = VideoPost.objects\
            .filter(categorys=video.categorys)\
            .filter(tags__in=video.tags.all()).exclude(id=video.id).distinct()
        return related_videos

    @method_decorator(cache_page(cache_time, key_prefix="recommender_video_list"))  
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class IncreaseChannelViewCountView(View):
    def get(self, request, channel_id):
        try:
            channel = Channel.objects.get(id=channel_id)
            channel.counted_view += 1
            channel.save()
            return JsonResponse({'status': 'success', 'new_view_count': channel.counted_view})
        except Channel.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Channel not found'}, status=404)
        

class IncreaseVideoPostCountView(View):
    def get(self, request, video_id):
        try:
            video = VideoPost.objects.get(id=video_id)
            video.counted_views += 1
            video.save()
            return JsonResponse({'status': 'success', 'new_view_count': video.counted_views})
        except VideoPost.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Channel not found'}, status=404)
        

class SpecialSectionModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsGetOnly | IsAdminUser, IsOwnerCreatorOrSupervisor]
    serializer_class = SpecialSectionSerializer
    queryset = SpecialSection.objects.all()
    pagination_class = CustomPageNumberPagination
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['creator', 'special_item', 'section_name'] #'is_active',
    search_fields = ['creator__user__username', 'section_name',
                     'special_item__title', 'special_item__description', 
                     'special_item__cast', 'special_item__categorys__name', 
                     'special_item__tags__name',
                     'special_item__supervisor_to_confirm__user__username', 
                     'special_item__supervisor_to_pined__user__username',]
    ordering_fields = ['-created_date']
    
    @method_decorator(cache_page(cache_time, key_prefix="specialSection_list"))  
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AdminsOfChannelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsGetOnly | IsAdminUser, IsChannelOwner]
    queryset = AdminsOfChannel.objects.all()
    serializer_class = AdminsOfChannelSerializer
    pagination_class = CustomPageNumberPagination
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['admin', 'user_adder', 'channel__owner', 'channel__confirm_to_channel', 
                        'channel__is_favorite', 'channel__activation',  'channel__name', 'channel__id']
    
    def perform_create(self, serializer):
        user_adder = self.request.user.profile
        channel = serializer.validated_data['channel']

        if user_adder != channel.owner:
            raise ValidationError("User adder must be the owner of the channel.")

        serializer.save(user_adder=user_adder)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SocialOfChanneViewSet(viewsets.ModelViewSet):
    permission_classes = [IsGetOnly | IsAdminUser, IsChannelOwner]
    queryset = SocialOfChanne.objects.all()
    serializer_class = SocialOfChanneSerializer
    pagination_class = CustomPageNumberPagination
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['channel', 'user_adder', 'name', ]
    search_fields = ['channel__name', 'user_adder__user__username', 'name', 
                     ]
    ordering_fields = ['-created_date']

    def perform_create(self, serializer):
        user_adder = self.request.user.profile
        channel = serializer.validated_data['channel']

        if user_adder != channel.owner:
            raise ValidationError("User adder must be the owner of the channel.")

        serializer.save(user_adder=user_adder)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserChannelsView(APIView):
    def get(self, request, user_id):
        try:
            user = Profile.objects.get(id=user_id)

            owned_channels = Channel.objects.filter(owner=user)

            admin_channels = Channel.objects.filter(adminsofchannel__admin=user)

            owned_channels_serialized = ChannelSerializer(owned_channels, many=True, context={'request': request}).data
            admin_channels_serialized = ChannelSerializer(admin_channels, many=True, context={'request': request}).data

            data = {
                'owned_channels': owned_channels_serialized,
                'admin_channels': admin_channels_serialized,
            }

            return Response(data, status=status.HTTP_200_OK)

        except Profile.DoesNotExist:
            return Response({'detail': 'The desired user was not found.'}, status=status.HTTP_404_NOT_FOUND)


class MostLikedVideoPostsModelViewSet(viewsets.ModelViewSet):
    #permission_classes = [IsGetOnly | IsAdminUser, IsOwnerOrSupervisor]
    queryset = VideoPost.objects.filter(counted_like__gt=10).order_by('-counted_like')
    serializer_class = VideoPostSerializer
    pagination_class = CustomPageNumberPagination
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['channel', 'status', 'confirm_to_post', 'is_pined', 
                        'publisher' , 'supervisor_to_confirm', 'supervisor_to_pined' , 
                        'tags', 'categorys', 'language_video']
    
    search_fields = ['channel__name', 'channel__owner__user__username', 
                     'channel__handle', 'channel__description', 
                     'channel__supervisor_to_confirm__user__username', 
                     'channel__supervisor_to_favorited__user__username', 
                     
                     'publisher__user__username', 'slog', 
                     'hls_master_playlist', 'language_video__name', 
                     'title', 'snippet', 'meta_description', 'description', 
                     'reference', 'cast', 'categorys__name', 'tags__name',
                     'supervisor_to_confirm__user__username', 
                     'supervisor_to_pined__user__username',]
    #ordering_fields = ['-published_date']

    @method_decorator(cache_page(cache_time, key_prefix="mostLiked_video_list"))  
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class PopularVideoPostsModelViewSet(viewsets.ModelViewSet):
    #permission_classes = [IsGetOnly | IsAdminUser, IsOwnerOrSupervisor]
    queryset = VideoPost.objects.filter(counted_views__gt=10).order_by('-counted_views')
    serializer_class = VideoPostSerializer
    pagination_class = CustomPageNumberPagination
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['channel', 'status', 'confirm_to_post', 'is_pined', 
                        'publisher' , 'supervisor_to_confirm', 'supervisor_to_pined' , 
                        'tags', 'categorys', 'language_video']
    
    search_fields = ['channel__name', 'channel__owner__user__username', 
                     'channel__handle', 'channel__description', 
                     'channel__supervisor_to_confirm__user__username', 
                     'channel__supervisor_to_favorited__user__username', 
                     
                     'publisher__user__username', 'slog', 
                     'hls_master_playlist', 'language_video__name', 
                     'title', 'snippet', 'meta_description', 'description', 
                     'reference', 'cast', 'categorys__name', 'tags__name',
                     'supervisor_to_confirm__user__username', 
                     'supervisor_to_pined__user__username',]
    #ordering_fields = ['published_date']

    @method_decorator(cache_page(cache_time, key_prefix="popular_video_list"))  
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class GeneralInfoView(APIView):
    def get(self, request, user_id):
        try:
            user = Profile.objects.get(id=user_id)

            owned_channels = Channel.objects.filter(owner=user)

            admin_channels = Channel.objects.filter(adminsofchannel__admin=user)

            owned_channels_serialized = ChannelSerializer(owned_channels, many=True, context={'request': request}).data
            admin_channels_serialized = ChannelSerializer(admin_channels, many=True, context={'request': request}).data

            count_video_in_owned_channel = 0
            counted_views_of_video_in_owned_channel = 0
            counted_like_of_video_in_owned_channel = 0
            counted_dislike_of_video_in_owned_channel = 0
            counted_save_of_video_in_owned_channel = 0
            counted_share_of_video_in_owned_channel = 0
            counted_comments_of_video_in_owned_channel = 0
            
            videos_in_owned_channel = VideoPost.objects.filter(channel__owner=user)
            count_video_in_owned_channel += len(videos_in_owned_channel)
    
            for video in videos_in_owned_channel:
                counted_views_of_video_in_owned_channel += video.counted_views
                counted_like_of_video_in_owned_channel += video.counted_like
                counted_dislike_of_video_in_owned_channel += video.counted_dislike
                counted_save_of_video_in_owned_channel += video.counted_save
                counted_share_of_video_in_owned_channel += video.counted_share
                counted_comments_of_video_in_owned_channel += Comment.objects.filter(video_post= video).count()
            
            count_video_published_in_admin_channel = 0
            counted_views_of_video_published_in_admin_channel = 0
            counted_like_of_video_published_in_admin_channel = 0
            counted_dislike_of_video_published_in_admin_channel = 0
            counted_save_of_video_published_in_admin_channel = 0
            counted_share_of_video_published_in_admin_channel = 0
            counted_comments_of_video_published_in_admin_channel = 0

            for admin_channel in admin_channels:
                video_published_in_admin_channel = VideoPost.objects.filter(publisher=user, channel=admin_channel)
                count_video_published_in_admin_channel += len(video_published_in_admin_channel)

                for video in video_published_in_admin_channel:
                    counted_views_of_video_published_in_admin_channel += video.counted_views
                    counted_like_of_video_published_in_admin_channel += video.counted_like
                    counted_dislike_of_video_published_in_admin_channel += video.counted_dislike
                    counted_save_of_video_published_in_admin_channel += video.counted_save
                    counted_share_of_video_published_in_admin_channel += video.counted_share

                    counted_comments_of_video_published_in_admin_channel += Comment.objects.filter(video_post= video).count
            
            data = {
                'count_owned_channels': len(owned_channels_serialized),
                'count_video_in_owned_channel': count_video_in_owned_channel,
                'counted_views_of_video_in_owned_channel': counted_views_of_video_in_owned_channel,
                'counted_like_of_video_in_owned_channel': counted_like_of_video_in_owned_channel,
                'counted_dislike_of_video_in_owned_channel': counted_dislike_of_video_in_owned_channel,
                'counted_save_of_video_in_owned_channel': counted_save_of_video_in_owned_channel,
                'counted_share_of_video_in_owned_channel': counted_share_of_video_in_owned_channel,
                'counted_comments_of_video_in_owned_channel': counted_comments_of_video_in_owned_channel,

                'count_admin_channels': len(admin_channels_serialized),
                'count_video_published_in_admin_channel': count_video_published_in_admin_channel,
                'counted_views_of_video_published_in_admin_channel': counted_views_of_video_published_in_admin_channel,
                'counted_like_of_video_published_in_admin_channel': counted_like_of_video_published_in_admin_channel,
                'counted_dislike_of_video_published_in_admin_channel': counted_dislike_of_video_published_in_admin_channel,
                'counted_save_of_video_published_in_admin_channel': counted_save_of_video_published_in_admin_channel,
                'counted_share_of_video_published_in_admin_channel': counted_share_of_video_published_in_admin_channel,
                'counted_comments_of_video_published_in_admin_channel': counted_comments_of_video_published_in_admin_channel,
            }

            return Response(data, status=status.HTTP_200_OK)

        except Profile.DoesNotExist:
            return Response({'detail': 'The desired user was not found.'}, status=status.HTTP_404_NOT_FOUND)


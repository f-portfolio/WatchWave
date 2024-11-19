from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser
from rest_framework import status, mixins, viewsets, generics
from .serializers import  *
from attachments.models import *
from .permissions import IsStaff, IsSupervisor, IsGetOnly, IsOwnerOrSupervisor, IsOwnerOrSupervisor_Item, ProposerOrSupervisor, OwnerAddOrSupV
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .paginations import *
from django.db.models import Count
from rest_framework.response import Response
from channels.models import VideoPost
from django.db.models.functions import Length


class TagModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsGetOnly|IsAdminUser, OwnerAddOrSupV]
    serializer_class = TagSerializer
    pagination_class = CustomPageNumberPagination
    queryset = Tag.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['confirm', 'user_adder']
    search_fields = ['name',]
    ordering_fields = ['name']

class CheckIfTagIsConfirmedSView(APIView):
    """
    API endpoint to return tag's ID(if confirmed).
    """

    def get(self, request, tag_name):
        """
        Handles GET requests to retrieve a tag by name.

        Args:
            request: The incoming HTTP request object.
            tag_name: The name of the tag to retrieve.

        Returns:
            A JSON response containing the tag's ID (if confirmed)
            or an error message depending on the outcome.
        """

        try:
            tag = Tag.objects.get(name=tag_name)
            # logger.info(f"Successfully retrieved tag with name: {tag_name}")

            if tag.confirm:
                response_data = {
                    'message': 'Tag is confirmed',
                    'id': tag.id,
                }
                # logger.info(f"Returning confirmed tag details (ID: {tag.id}, name: {tag.name})")
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {'message': 'Tag exists but not confirmed'}
                # logger.info(f"Returning tag details (ID: {tag.id}, name not included as not confirmed)")
                return Response(response_data, status=status.HTTP_200_OK)

        except Tag.DoesNotExist:
            # logger.error(f"Tag with name {tag_name} not found")
            return Response({'error': 'Tag not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # logger.exception(f"An error occurred while retrieving tag: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LanguageModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsGetOnly|IsAdminUser]
    serializer_class = LanguageSerializer
    queryset = Language.objects.all()
    pagination_class = CustomPageNumberPagination
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields = ['confirm',]
    search_fields = ['name',]
    ordering_fields = ['name']


class CategoryModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsGetOnly|IsAdminUser]
    serializer_class = CategorySerializer
    pagination_class = CustomPageNumberPagination
    queryset = Category.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields = ['confirm',]
    search_fields = ['name',]
    ordering_fields = ['name']


class URLModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsGetOnly|IsAdminUser]
    serializer_class = URLSerializer
    queryset = URL.objects.all()
    pagination_class = CustomPageNumberPagination
    


class TypeOfURLModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsGetOnly|IsAdminUser]
    serializer_class = TypeOfURLSerializer
    queryset = TypeOfURL.objects.all()
    pagination_class = CustomPageNumberPagination
    

class TypeOfAuthorModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsGetOnly|IsAdminUser]
    serializer_class = TypeOfAuthorSerializer
    queryset = TypeOfAuthor.objects.all()
    pagination_class = CustomPageNumberPagination
    

class MetaKwordModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsGetOnly|IsAdminUser]
    serializer_class = MetaKwordSerializer
    queryset = MetaKword.objects.all()
    pagination_class = CustomPageNumberPagination
    

class LinkOfPostsModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsGetOnly|IsAdminUser]
    serializer_class = LinkOfPostsSerializer
    queryset = LinkOfPosts.objects.all()
    pagination_class = CustomPageNumberPagination
    

class TopTagsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        tags = Tag.objects.annotate(
            usage_count=Count('posts_tag')
        ).order_by('-usage_count')[:10]

        data = [{'id': tag.id, 'tag': tag.name, 'usage_count': tag.usage_count} for tag in tags]

        return Response(data)



class TagCategoryModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsSupervisor]
    serializer_class = TagCategorySerializer
    http_method_names = ['get']  
    pagination_class = CustomPageNumberPagination
    
    def get_queryset(self):
        tag_name = self.request.query_params.get('tag_name')
        category_name = self.request.query_params.get('category_name')
        sub_category_name = self.request.query_params.get('sub_category_name')
        sub_sub_category_name = self.request.query_params.get('sub_sub_category_name')
        
        tags = Tag.objects.filter(confirm=True)

        if tag_name:
            tags = tags.filter(name__icontains=tag_name)
        
        
        unique_combinations = set()

        for tag in tags:
            video_posts = VideoPost.objects.filter(tags=tag)

            if category_name:
                video_posts = video_posts.filter(categorys__name__icontains=category_name)
            if sub_category_name:
                video_posts = video_posts.filter(sub_categorys__name__icontains=sub_category_name)
            if sub_sub_category_name:
                video_posts = video_posts.filter(sub_sub_categorys__name__icontains=sub_sub_category_name)

            for video in video_posts:
                combination = (
                    tag.id,
                    tag.name,
                    video.categorys.id if video.categorys else None,
                    video.categorys.name if video.categorys else None,
                    video.sub_categorys.id if video.sub_categorys else None,
                    video.sub_categorys.name if video.sub_categorys else None,
                    video.sub_sub_categorys.id if video.sub_sub_categorys else None,
                    video.sub_sub_categorys.name if video.sub_sub_categorys else None
                )
                unique_combinations.add(combination)

       
        result = [
            {
                'tag_id': comb[0],
                'tag_name': comb[1],
                'category_id': comb[2],
                'category_name': comb[3],
                'sub_category_id': comb[4],
                'sub_category_name': comb[5],
                'sub_sub_category_id': comb[6],
                'sub_sub_category_name': comb[7]
            }
            for comb in unique_combinations
        ]

        return result
    
class AddTagToPostsByCategoryAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSupervisor]

    def post(self, request, *args, **kwargs):
        tag_name = request.data.get('tag_name')
        category_name = request.data.get('category_name')
        sub_category_name = request.data.get('sub_category_name')
        sub_sub_category_name = request.data.get('sub_sub_category_name')

        
        if not tag_name:
            return Response({'error': 'Tag name is required.'}, status=status.HTTP_400_BAD_REQUEST)

        
        if category_name and not Category.objects.filter(name=category_name, type='category').exists():
            return Response({'error': 'There is no category.'}, status=status.HTTP_400_BAD_REQUEST)
        if sub_category_name and not Category.objects.filter(name=sub_category_name, type='sub_category').exists():
            return Response({'error': 'Subcategory 1 does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        if sub_sub_category_name and not Category.objects.filter(name=sub_sub_category_name, type='sub_sub_category').exists():
            return Response({'error': 'There is no subcategory 2.'}, status=status.HTTP_400_BAD_REQUEST)

        tag, created = Tag.objects.get_or_create(name=tag_name, confirm=True)

        if category_name:
            video_posts = VideoPost.objects.filter(categorys__name=category_name)
        if sub_category_name:
            video_posts = video_posts.filter(sub_categorys__name=sub_category_name)
        if sub_sub_category_name:
            video_posts = video_posts.filter(sub_sub_categorys__name=sub_sub_category_name)

        for video in video_posts:
            video.tags.add(tag)

        return Response({'message': f'Tag {tag_name} added to {video_posts.count()} video posts'}, status=status.HTTP_201_CREATED)

class RemoveTagToPostsByCategoryAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSupervisor]

    def post(self, request, *args, **kwargs):
        tag_name = request.data.get('tag_name')
        category_name = request.data.get('category_name')
        sub_category_name = request.data.get('sub_category_name')
        sub_sub_category_name = request.data.get('sub_sub_category_name')

        if not tag_name:
            return Response({'error': 'Tag name is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if category_name and not Category.objects.filter(name=category_name, type='category').exists():
            return Response({'error': 'There is no category.'}, status=status.HTTP_400_BAD_REQUEST)
        if sub_category_name and not Category.objects.filter(name=sub_category_name, type='sub_category').exists():
            return Response({'error': 'Subcategory 1 does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        if sub_sub_category_name and not Category.objects.filter(name=sub_sub_category_name, type='sub_sub_category').exists():
            return Response({'error': 'There is no subcategory 2.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            tag = Tag.objects.get(name=tag_name, confirm=True)
        except Tag.DoesNotExist:
            return Response({'error': 'Tag not found.'}, status=status.HTTP_404_NOT_FOUND)

        if category_name:
            video_posts = VideoPost.objects.filter(categorys__name=category_name)
        if sub_category_name:
            video_posts = video_posts.filter(sub_categorys__name=sub_category_name)
        if sub_sub_category_name:
            video_posts = video_posts.filter(sub_sub_categorys__name=sub_sub_category_name)

        for video in video_posts:
            video.tags.remove(tag)

        return Response({'message': f'Tag {tag_name} removed from {video_posts.count()} video posts'}, status=status.HTTP_200_OK)

class UpdateTagForPostsByCategoryAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSupervisor]

    def post(self, request, *args, **kwargs):
        old_tag_name = request.data.get('old_tag_name')
        new_tag_name = request.data.get('new_tag_name')
        category_name = request.data.get('category_name')
        sub_category_name = request.data.get('sub_category_name')
        sub_sub_category_name = request.data.get('sub_sub_category_name')

        if not old_tag_name or not new_tag_name:
            return Response({'error': 'Both old and new tags are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if category_name and not Category.objects.filter(name=category_name, type='category').exists():
            return Response({'error': 'There is no category.'}, status=status.HTTP_400_BAD_REQUEST)
        if sub_category_name and not Category.objects.filter(name=sub_category_name, type='sub_category').exists():
            return Response({'error': 'Subcategory 1 does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        if sub_sub_category_name and not Category.objects.filter(name=sub_sub_category_name, type='sub_sub_category').exists():
            return Response({'error': 'There is no subcategory 2.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            old_tag = Tag.objects.get(name=old_tag_name, confirm=True)
        except Tag.DoesNotExist:
            return Response({'error': 'Old tag not found.'}, status=status.HTTP_404_NOT_FOUND)

        new_tag, created = Tag.objects.get_or_create(name=new_tag_name, confirm=True)

        if category_name:
            video_posts = VideoPost.objects.filter(categorys__name=category_name)
        if sub_category_name:
            video_posts = video_posts.filter(sub_categorys__name=sub_category_name)
        if sub_sub_category_name:
            video_posts = video_posts.filter(sub_sub_categorys__name=sub_sub_category_name)

        for video in video_posts:
            video.tags.remove(old_tag)  
            video.tags.add(new_tag)     

        return Response({
            'message': f'Tag {old_tag_name} updated to {new_tag_name} for {video_posts.count()} video posts'
        }, status=status.HTTP_200_OK)

'''
{
    "tag_name": "My New Tag",
    "category_name": "Category 1",
    "sub_category_name": "Subcategory 1",
    "sub_sub_category_name": "Subsubcategory 1"
}
'''

class ReplaceTagsWithNewTagInAllCategoryAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSupervisor]

    def post(self, request, *args, **kwargs):
        new_tag_name = request.data.get('new_tag_name')
        tags_to_replace = request.data.get('tags_to_replace', [])

        if not new_tag_name or not tags_to_replace:
            return Response({'error': 'New tag and list of replacement tags are required.'}, status=status.HTTP_400_BAD_REQUEST)

        new_tag, created = Tag.objects.get_or_create(name=new_tag_name, confirm=True)

        old_tags = Tag.objects.filter(name__in=tags_to_replace, confirm=True)
        if not old_tags.exists():
            return Response({'error': 'None of the replacement list tags were found.'}, status=status.HTTP_404_NOT_FOUND)

        video_posts = VideoPost.objects.filter(tags__in=old_tags).distinct()

        for video in video_posts:
            for old_tag in old_tags:
                video.tags.remove(old_tag)  
            video.tags.add(new_tag)         

        return Response({
            'message': f'Tags {tags_to_replace} replaced with {new_tag_name} in {video_posts.count()} video posts.'
        }, status=status.HTTP_200_OK)

'''
{
  "new_tag_name": "new-tag",
  "tags_to_replace": ["old-tag-1", "old-tag-2", "old-tag-3"]
}
'''


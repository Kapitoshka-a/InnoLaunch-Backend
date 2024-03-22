from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .serializers import *
from .permissions import IsAdminOrReadOnly


class HomePageView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        try:
            establishment = Establishment.objects.filter(recommended=True).order_by('rating')
        except Establishment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = EstablishmentSerializer(establishment, many=True, context={'request': request})
        return Response(serializer.data)


class EstablishmentsList(generics.ListAPIView):
    serializer_class = EstablishmentSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'type', 'address']
    ordering_fields = ['comments__rating', 'price_for_entrance']

    def get_queryset(self):
        return Establishment.objects.all().only('name', 'rating', 'address',
                                                'work_mobile_number', 'price_for_entrance')


class EstablishmentDetail(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, slug):
        try:
            establishment = Establishment.objects.get(slug=slug)
        except Establishment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = EstablishmentSerializer(establishment, context={'request': request})
        return Response(serializer.data)


class CommentListCreate(generics.ListCreateAPIView):
    """Endpoint to get all comments or create own for a specific specialty"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self):
        """Query set for retrieving all comments for specialty"""
        slug = self.kwargs.get('slug')
        try:
            comments = Comment.objects.filter(establishment__slug=slug)
            return comments
        except Comment.DoesNotExist:
            raise NotFound("Comments for this establishment do not exist.")

    def perform_create(self, serializer):
        """Create e new comment"""
        slug = self.kwargs.get('slug')
        establishment = generics.get_object_or_404(Establishment, slug=slug)
        if Comment.objects.filter(establishment=establishment, author=self.request.user).exists():
            raise serializers.ValidationError({'Message': 'You have already added comment on this establishment'})
        serializer.save(author=self.request.user, establishment=establishment)


class CommentDetail(APIView):
    """Endpoint to get specific detail about a comment"""

    def get(self, request, slug, pk):
        """Get specific comment"""
        try:
            comment = Comment.objects.get(pk=pk)
        except Establishment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CommentSerializer(comment, context={'request': request})
        return Response(serializer.data)

    def put(self, request, slug, pk):
        """Update a comment"""
        comment = Comment.objects.get(pk=pk)
        serializer = CommentSerializer(comment, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug,  pk):
        """Delete a comment"""
        comment = Comment.objects.get(pk=pk)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

from rest_framework import status, generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from RestProject.constants import (CATEGORY_CREATED_SUCCESS, CATEGORY_ADDED_SUCCESS)
from categories.models import (Category, SelectedCategories)
from categories.serializers import (CategorySerializer, SelectCategorySerializer)


class CategoryCreateView(APIView):
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated, IsAdminUser)

    def post(self, request, format='json'):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": CATEGORY_CREATED_SUCCESS}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AllCategoriesView(generics.ListAPIView):
    queryset = Category.objects.filter(is_valid=True, parent__isnull=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, ]


class SelectCategoriesView(APIView):
    serializer_class = SelectCategorySerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return SelectedCategories.objects.filter(user=self.request.user, is_valid=True).first()

    def post(self, request, format='json'):
        data = self.request.data.copy()
        data['user'] = self.request.user.id
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": CATEGORY_ADDED_SUCCESS}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        serializer = self.serializer_class(self.get_object())
        return Response(serializer.data, status=status.HTTP_200_OK)


class OtherCategoriesView(APIView):
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        selected_categories = SelectedCategories.objects.filter(user=self.request.user, is_valid=True).first()
        return Category.objects.filter(is_valid=True).exclude(
            id__in=selected_categories.categories.all().values_list('id', flat=True))

    def get(self, request):
        serializer = self.serializer_class(self.get_object(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

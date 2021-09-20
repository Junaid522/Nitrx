from rest_framework import serializers

from categories.models import Category, SelectedCategories


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    childs = serializers.SerializerMethodField()
    collapsed = serializers.SerializerMethodField()

    def get_childs(self, obj):
        return CategoryChildSerializer(Category.objects.filter(parent=obj), many=True).data

    def get_collapsed(self, obj):
        return False


class CategoryChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class SelectCategorySerializer(serializers.ModelSerializer):
    category_details = serializers.SerializerMethodField()

    class Meta:
        model = SelectedCategories
        fields = '__all__'

    def get_category_details(self, obj):
        return CategorySerializer(obj.categories, many=True).data

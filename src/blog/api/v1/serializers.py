from django.contrib.auth import get_user_model
from rest_framework import serializers

from blog.models import Category, Post

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
        ]


class PostSerializer(serializers.ModelSerializer):
    likes = serializers.IntegerField()
    absolute_url = serializers.SerializerMethodField(read_only=True)

    author = serializers.SlugRelatedField(slug_field="full_name", read_only=True)

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field="id",
    )

    def get_absolute_url(self, obj):
        request = self.context.get("request")
        if obj:
            return request.build_absolute_uri(obj.slug)

    def to_representation(self, instance):

        rep = super().to_representation(instance)
        request = self.context.get("request")

        if request.parser_context.get("kwargs").get("slug"):

            rep.pop("absolute_url", None)
        else:
            rep.pop("content", None)

        rep["category"] = CategorySerializer(instance.category).data["name"]

        return rep

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "category",
            "title",
            "slug",
            "content",
            "status",
            "image",
            "likes",
            "absolute_url",
            "created_at",
            "updated_at",
            "published_at",
        ]
        read_only_fields = ["slug"]

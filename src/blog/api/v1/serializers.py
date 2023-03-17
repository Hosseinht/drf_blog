from django.contrib.auth import get_user_model
from rest_framework import serializers

from blog.models import Category, Post, Comment

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
        ]


class PostSerializer(serializers.ModelSerializer):
    likes = serializers.IntegerField(read_only=True)
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
        # read_only_fields = ["slug"]


class FilterSerializer(serializers.Serializer):
    """
    These fields are used in the filters.py
    """

    title = serializers.CharField(required=False, max_length=100)
    search = serializers.CharField(required=False, max_length=100)
    author__in = serializers.CharField(required=False, max_length=100)
    category__name = serializers.CharField(required=False, max_length=100)
    created_at__range = serializers.CharField(required=False, max_length=100)


class CommentSerializer(serializers.ModelSerializer):
    comment_user = serializers.StringRelatedField()
    comment_post = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = ["id", "comment_user", "comment_post", "comment", "created_at"]
        read_only_fields = ["created_at"]

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def clean(self):
        self.name = self.name.capitalize()
        super().clean()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="author"
    )
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(blank=True, unique=True)
    content = models.TextField()
    image = models.ImageField(default="cover-photo-3.PNG")
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        return reverse("blog:blog-api-v1:posts-detail", kwargs={"slug": self.slug})


class Like(models.Model):
    like_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    like_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="like")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ["like_user", "like_post"]

    def __str__(self):
        return f"{self.like_user} - {self.like_post}"


class Comment(models.Model):
    comment_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment = models.TextField(max_length=500)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.comment_user} - {self.comment_post}"

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model): # New Post: post1 = Post(poster=????, text="qwer")
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts") 
    text = models.CharField(max_length=140) 
    likecount = models.IntegerField(blank=True, null=True)
    time = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"{self.text}"

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="liked by")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes", null=True, blank=True)

    def __str__(self):
        return f"Like {self.id} by {self.user} on object {self.post}"

class Following(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    user_followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers" )

    def __str__(self):
        return f"{self.user} is following {self.user_followed}"

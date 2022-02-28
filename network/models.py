from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    def follow(self, to_follow):
        Follow.objects.create(following = to_follow, followers = self)

    def unfollow(self, to_unfollow): 
        Follow.objects.get(following = to_unfollow, followers = self).delete()

class Follow(models.Model):
    following = models.ForeignKey("User", on_delete=models.CASCADE, related_name="user_i_follow")
    followers = models.ForeignKey("User", on_delete=models.CASCADE, related_name="me")

    def serialize(self):
        return {
            "id": self.id,
            "following": self.following.username,
            "follower": self.followers.username
        }

class Comment(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    comment = models.TextField(max_length=280)
    timestamp = models.DateTimeField()
    likes = models.IntegerField()

class Post(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    post = models.CharField(max_length=280)
    timestamp = models.DateTimeField()
    likes = models.IntegerField()

    def get_likes(self):
        likes = Like.objects.filter(post = self)
        likers = []
        for like in likes:
            likers.append(like.liker)
        return likers

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "post": self.post,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "likes": self.likes
        }

    def __str__(self):
        return f"Post {self.id}"

class Like(models.Model):
    liker = models.ForeignKey("User", on_delete=models.CASCADE)
    post = models.ForeignKey("Post", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.liker.username} liked post {self.post.id}"
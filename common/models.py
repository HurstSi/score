from django.db import models


class User(models.Model):
    openid = models.CharField(max_length=64)
    stuNum = models.CharField(max_length=20)
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=128)
    logo = models.CharField(max_length=256)
    info = models.TextField()

    def __str__(self):
        return self.name


class Score(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    item = models.ForeignKey(Item, on_delete=models.DO_NOTHING)
    content = models.IntegerField()

    def __str__(self):
        return self.item.name


class Token(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    content = models.CharField(max_length=32)
    createTime = models.IntegerField()

    def __str__(self):
        return self.user.name

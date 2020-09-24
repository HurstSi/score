from django.db import models


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    openid = models.CharField(max_length=64)
    stuNum = models.CharField(max_length=20)
    name = models.CharField(max_length=128)


class Item(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=128)
    logo = models.CharField(max_length=256)
    info = models.TextField()


class Score(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    item = models.ForeignKey(Item, on_delete=models.DO_NOTHING)
    content = models.IntegerField()


class Token(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    content = models.CharField(max_length=32)
    createTime = models.IntegerField()

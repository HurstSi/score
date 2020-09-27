from django.db import models


class Class(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class User(models.Model):
    openid = models.CharField(max_length=64)
    stuNum = models.CharField(max_length=20)
    name = models.CharField(max_length=128)
    m_class = models.ForeignKey(Class, on_delete=models.CASCADE, null=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=128)
    logo = models.CharField(max_length=256)
    info = models.TextField()
    m_class = models.ForeignKey(Class, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class Score(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    content = models.IntegerField()
    modification = models.IntegerField(default=1) # 修改次数

    def __str__(self):
        return self.item.name


class FeedBack(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    create_time = models.IntegerField()

    def __str__(self):
        return self.user.name + "--" + self.title


class Token(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=32)
    createTime = models.IntegerField()

    def __str__(self):
        return self.user.name

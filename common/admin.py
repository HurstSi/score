from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Item)
admin.site.register(Score)
admin.site.register(Token)

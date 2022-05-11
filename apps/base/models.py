from django.db import models

# Create your models here.
class Info(models.Model):
    name = models.CharField(verbose_name='名称',max_length=32)
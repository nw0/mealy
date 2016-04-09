from django.db import models

class Resource_Type(models.Model):
    r_parent    = models.ForeignKey('self', default=None, null=True)
    r_name      = models.CharField(max_length=40)

    def __str__(self):
        return self.r_name

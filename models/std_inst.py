from django.db import models

from res_type import Resource_Type

class Standard_Inst(models.Model):
    inst_name   = models.CharField(max_length=40)
    inst_type   = models.ForeignKey(Resource_Type)
    usual_price = models.FloatField()
    use_formal  = models.BooleanField(default=False)
    orig_units  = models.CharField(max_length=6)
    orig_amt    = models.FloatField()

    def __str__(self):
        return self.inst_name

    class Meta:
        verbose_name    = "standard resource instance"

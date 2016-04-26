from django.db import models
import json

from res_type import Resource_Type
from res_inst import Unit

class Standard_Inst(models.Model):
    inst_name   = models.CharField(max_length=40)
    inst_type   = models.ForeignKey(Resource_Type)
    usual_price = models.FloatField()
    use_formal  = models.BooleanField(default=False)
    use_bestbef = models.BooleanField(default=True)
    orig_unit   = models.ForeignKey(Unit)
    is_relative = models.BooleanField(default=False)
    orig_amt    = models.FloatField()

    def show_fields(self):
        return json.dumps({ 'inst_name':    self.inst_name,
                            'inst_type':    self.inst_type.__str__(),
                            'usual_price':  self.usual_price,
                            'orig_amt':     self.orig_amt,
                            'orig_units':   self.orig_unit.__str__(),
                            'is_rel':       self.is_relative,
                            })

    def __str__(self):
        return self.inst_name

    class Meta:
        verbose_name    = "standard resource instance"

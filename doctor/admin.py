from django.contrib import admin
from .models import *
from .ch06_ECG import ECGClassification


# Register your models here.
admin.site.register(Doctor)


class CaseResultCreate(admin.ModelAdmin):
    readonly_fields = ('image_data',)
    exclude = ['result_img']


    def save_model(self, request, obj, form, change):
        if change:
            obj.save()
        else:
            hea = obj.hea
            atr = obj.atr
            dat = obj.dat
            patname = obj.caseNo
            obj.save()
            result = ECGClassification.exec_create_img(hea, atr, dat, patname)
            print(result)
            obj.diagnosis_results = result
            obj.result_img = "/file/"+patname+".png"
            obj.save()


admin.site.register(Case, CaseResultCreate)
admin.site.site_header = '心电图诊断后台管理'
admin.site.site_title = '心电图'
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

SEX_CHOICES = (
    ('1', '男'),
    ('0', '女'),
)


class Doctor(AbstractUser):
    doctorNo = models.CharField(verbose_name="医生号",max_length=11,null=True)
    doctorname = models.CharField(verbose_name="医生姓名", max_length=11, null=True)
    sex = models.CharField('性别', max_length=10, null=True, blank=True, choices=SEX_CHOICES, default='1')

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'Doctor'
        verbose_name = '医生'
        verbose_name_plural = verbose_name

from django.utils.html import format_html

class Case(models.Model):
    caseNo = models.CharField(verbose_name="病例号",max_length=11,null=True)
    patientname = models.CharField(verbose_name="患者姓名", max_length=11, null=True)
    sex = models.CharField('性别', max_length=10, null=True, blank=True, choices=SEX_CHOICES, default='1')
    age = models.IntegerField(verbose_name="患者年龄", null=True)
    cellphone = models.CharField(verbose_name="联系方式", max_length=11, null=True)
    weight = models.CharField(verbose_name="体重", max_length=11, null=True)
    height = models.CharField(verbose_name="身高", max_length=11, null=True)
    atr = models.FileField(verbose_name="atr文件", upload_to="file")
    dat = models.FileField(verbose_name="dat文件", upload_to="file")
    hea = models.FileField(verbose_name="hea文件", upload_to="file")
    diagnosis_results = models.TextField(verbose_name="诊断结果", null=True,blank=True)
    result_img = models.CharField(verbose_name="结果图",max_length=200,null=True,blank=True)
    doctor = models.ForeignKey(Doctor,verbose_name="医生")


    def __str__(self):
        return self.caseNo

    def get_sex(self):
        if self.sex=='0':
            return u'女'
        else:
            return u'男'

    def image_data(self):
        return format_html(
            '<img src="{}" width="60%"/>', self.result_img,
        )

    image_data.short_description = u'结果图'


    class Meta:
        db_table = 'Case'
        verbose_name = '病历'
        verbose_name_plural = verbose_name

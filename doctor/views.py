from django.shortcuts import render, redirect
from .models import *

# Create your views here.
def get_result(request):
    if request.method == "POST":
        caseNo = request.POST.get("caseNo")
        cellphone = request.POST.get("cellphone")
        result = Case.objects.filter(caseNo=caseNo, cellphone=cellphone)
        if result:
            return render(request, "pateintresult.html",{"result":result[0],"a":"a"})
        else:
            return render(request, "search.html", {"result":"请输入正确病历号手机号"})
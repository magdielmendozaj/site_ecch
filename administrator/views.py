from django.shortcuts import render
from rest_framework.views import APIView

# Create your views here.

# class admin(APIView):
#     template_name='admin.html'
#     def get(self,request):
#         return render(request,self.template_name)

class index(APIView):
    template_name='index.html'
    def get(self,request):
        return render(request,self.template_name)
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator, EmptyPage
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User, Group

# Create your views here.
@api_view(['POST'])
@permission_classes([IsAdminUser])
def managers(request):
    username = request.data['username']
    
    if username:
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name='Managers')
        if request.method == 'POST':
            managers.user_set.add(user)
        elif request.method == 'DELETE':
            managers.user_set.remove(user)
        
        return Response({"message":"Ok"})
    return Response({"Error":"error"}, status.HTTP_400_BAD_REQUEST)
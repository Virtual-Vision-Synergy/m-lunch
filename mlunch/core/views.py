from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages

from django.shortcuts import render, redirect
from django.http import JsonResponse

import json
from django.views.decorators.csrf import csrf_exempt
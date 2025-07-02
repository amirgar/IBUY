from django.shortcuts import redirect, render
from django.urls import reverse
from account.models import User

def dashboard(request):
    return render(request, 'registration/dashboard.html')

def index(request):
    if request.method == "POST":
        email = request.POST.get("email") 
        password = request.POST.get("pass")
        repassword = request.POST.get("repass")
        print(f'{email}, {password}, {repassword}')
        if repassword == "": 
            if User.objects.filter(email=email, password=password).exists(): 
                return redirect(reverse("dashboard"))
            else:
                return render(request, "registration/account.html")
        else: 
            if password == repassword: 
                newUser = User(email=email, password=password)
                newUser.save()
                return redirect(reverse("dashboard"))
            else: 
                return render(request, "registration/account.html")
    else:
        return render(request, "registration/account.html")
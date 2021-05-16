from django.shortcuts import redirect

# admin only
# decorator function always accept a function, there will be a inner function
# as many arguments given in post or get function, same arguments should by given here
def admin_only(func):
    def wrapper(request,*args,**kwargs):
        if not request.user.is_superuser:
            return redirect("error")
        else:
            return func(request,*args,**kwargs)  # returing that function
    return wrapper


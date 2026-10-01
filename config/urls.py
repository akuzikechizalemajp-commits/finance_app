"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from budgeting import views






urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.dashboard, name='dashboard'),

    path('register/', views.register, name='register'),

    path('login/', views.login_view, name='login'),

    path('logout/', views.logout_view, name='logout'),
    
    path("income/add/", views.add_income, name="add_income"),

    path("expenses/add/", views.add_expense, name="add_expense"),

    path("income/<int:income_id>/edit/", views.edit_income, name="edit_income"),

    path("income/<int:income_id>/delete/", views.delete_income, name="delete_income"),

    path("expenses/<int:expense_id>/edit/", views.edit_expense, name="edit_expense"),

    path("expenses/<int:expense_id>/delete/", views.delete_expense, name="delete_expense"),

    path("tax-calculator/", views.tax_calculator, name="tax_calculator"),
]
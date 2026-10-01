from django.shortcuts import render, redirect
from django.db.models import Sum
from django.utils import timezone
from datetime import date

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Income, Expense, Budget
from .forms import IncomeForm, ExpenseForm  


from decimal import Decimal
from django.shortcuts import render
from .models import TaxRuleSet, TaxRule, TaxBracket


def register(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            password=password
        )

        login(request, user)

        return redirect("dashboard")

    return render(request, "budgeting/register.html")


def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        messages.error(request, "Invalid username or password.")

    return render(request, "budgeting/login.html")


def logout_view(request):

    logout(request)

    return redirect("login")


@login_required(login_url="/login/")
def dashboard(request):

    today = timezone.localdate()

    # =====================================================
    # CURRENT USER
    # =====================================================

    user = request.user

    # =====================================================
    # SELECTED MONTH
    # =====================================================

    month_value = request.GET.get("month")

    if month_value:
        try:
            year, month = map(int, month_value.split("-"))
            selected_month = date(year, month, 1)
        except (ValueError, TypeError):
            selected_month = today.replace(day=1)
    else:
        selected_month = today.replace(day=1)

    selected_year = selected_month.year
    selected_month_number = selected_month.month

    # =====================================================
    # MONTHLY TOTALS
    # =====================================================

    monthly_income = Income.objects.filter(
        user=user,
        date__year=selected_year,
        date__month=selected_month_number
    ).aggregate(
        total=Sum("amount")
    )["total"] or 0

    monthly_expenses = Expense.objects.filter(
        user=user,
        date__year=selected_year,
        date__month=selected_month_number
    ).aggregate(
        total=Sum("amount")
    )["total"] or 0

    monthly_remaining = monthly_income - monthly_expenses

    # =====================================================
    # ALL-TIME TOTALS
    # =====================================================

    all_time_income = Income.objects.filter(
        user=user
    ).aggregate(
        total=Sum("amount")
    )["total"] or 0

    all_time_expenses = Expense.objects.filter(
        user=user
    ).aggregate(
        total=Sum("amount")
    )["total"] or 0

    all_time_remaining = all_time_income - all_time_expenses

    # =====================================================
    # EXPENSES BY CATEGORY
    # =====================================================

    expenses_by_category = (
        Expense.objects
        .filter(
            user=user,
            date__year=selected_year,
            date__month=selected_month_number
        )
        .values("category")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )

    # =====================================================
    # BUDGET VS ACTUAL
    # =====================================================

    budgets = Budget.objects.filter(
        user=user,
        month__year=selected_year,
        month__month=selected_month_number
    )

    budget_comparison = []

    for budget in budgets:

        spent = (
            Expense.objects
            .filter(
                user=user,
                category__iexact=budget.category,
                date__year=selected_year,
                date__month=selected_month_number
            )
            .aggregate(
                total=Sum("amount")
            )["total"] or 0
        )

        budget_remaining = budget.amount - spent

        budget_comparison.append({
            "category": budget.category,
            "budget": budget.amount,
            "spent": spent,
            "remaining": budget_remaining,
        })

    # =====================================================
    # MONTH SELECTOR
    # =====================================================

    months = set()

    for item in Income.objects.filter(user=user).values(
        "date__year",
        "date__month"
    ):
        months.add(
            (item["date__year"], item["date__month"])
        )

    for item in Expense.objects.filter(user=user).values(
        "date__year",
        "date__month"
    ):
        months.add(
            (item["date__year"], item["date__month"])
        )

    for item in Budget.objects.filter(user=user).values(
        "month__year",
        "month__month"
    ):
        months.add(
            (item["month__year"], item["month__month"])
        )

    months.add(
        (selected_year, selected_month_number)
    )

    months = sorted(months, reverse=True)

    month_choices = []

    for year, month in months:

        month_choices.append({
            "value": f"{year:04d}-{month:02d}",
            "label": date(
                year,
                month,
                1
            ).strftime("%B %Y"),
        })

    # =====================================================
    # RECENT TRANSACTIONS
    # =====================================================

    recent_income = Income.objects.filter(
        user=user
    ).order_by("-date", "-id")[:10]

    recent_expenses = Expense.objects.filter(
        user=user
    ).order_by("-date", "-id")[:10]

    transactions = []

    for income in recent_income:

        transactions.append({
            "id": income.id,
            "date": income.date,
            "type": "Income",
            "category": "Income",
            "amount": income.amount, "id": income.id,
            "date": income.date,
            "type": "Income",
            "category": "Income",
            "amount": income.amount,
        })

    for expense in recent_expenses:

        transactions.append({
            "id": expense.id,
            "date": expense.date,
            "type": "Expense",
            "category": expense.category,
            "amount": expense.amount,
        })

    transactions = sorted(
        transactions,
        key=lambda x: x["date"],
        reverse=True
    )[:10]

    # =====================================================
    # CONTEXT
    # =====================================================

    context = {

        "selected_month": selected_month,

        "selected_month_value": (
            f"{selected_year:04d}-{selected_month_number:02d}"
        ),

        "monthly_income": monthly_income,
        "monthly_expenses": monthly_expenses,
        "monthly_remaining": monthly_remaining,

        "all_time_income": all_time_income,
        "all_time_expenses": all_time_expenses,
        "all_time_remaining": all_time_remaining,

        "budget_comparison": budget_comparison,

        "expenses_by_category": expenses_by_category,

        "month_choices": month_choices,

        "transactions": transactions,
    }

    return render(
        request,
        "budgeting/dashboard.html",
        context
    )




@login_required(login_url="/login/")
def add_income(request):

    if request.method == "POST":
        form = IncomeForm(request.POST)

        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()

            return redirect("dashboard")

    else:
        form = IncomeForm()

    return render(
        request,
        "budgeting/add_income.html",
        {"form": form}
    )


@login_required(login_url="/login/")
def add_expense(request):

    if request.method == "POST":
        form = ExpenseForm(request.POST)

        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()

            return redirect("dashboard")

    else:
        form = ExpenseForm()

    return render(
        request,
        "budgeting/add_expense.html",
        {"form": form}
    )



@login_required(login_url="/login/")
def edit_income(request, income_id):

    income = Income.objects.get(
        id=income_id,
        user=request.user
    )

    if request.method == "POST":
        form = IncomeForm(
            request.POST,
            instance=income
        )

        if form.is_valid():
            form.save()
            return redirect("dashboard")

    else:
        form = IncomeForm(instance=income)

    return render(
        request,
        "budgeting/edit_income.html",
        {"form": form}
    )


@login_required(login_url="/login/")
def edit_expense(request, expense_id):

    expense = Expense.objects.get(
        id=expense_id,
        user=request.user
    )

    if request.method == "POST":
        form = ExpenseForm(
            request.POST,
            instance=expense
        )

        if form.is_valid():
            form.save()
            return redirect("dashboard")

    else:
        form = ExpenseForm(instance=expense)

    return render(
        request,
        "budgeting/edit_expense.html",
        {"form": form}
    )


@login_required(login_url="/login/")
def delete_income(request, income_id):

    income = Income.objects.get(
        id=income_id,
        user=request.user
    )

    if request.method == "POST":
        income.delete()
        return redirect("dashboard")

    return render(
        request,
        "budgeting/delete_income.html",
        {"income": income}
    )


@login_required(login_url="/login/")
def delete_expense(request, expense_id):

    expense = Expense.objects.get(
        id=expense_id,
        user=request.user
    )

    if request.method == "POST":
        expense.delete()
        return redirect("dashboard")

    return render(
        request,
        "budgeting/delete_expense.html",
        {"expense": expense}
    )


   
@login_required(login_url="/login/")
def edit_expense(request, expense_id):
    expense = Expense.objects.get(id=expense_id, user=request.user)

    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense)

        if form.is_valid():
            form.save()
            return redirect("dashboard")

    else:
        form = ExpenseForm(instance=expense)

    return render(
        request,
        "budgeting/edit_expense.html",
        {"form": form}
    )




@login_required(login_url="/login/")
def tax_calculator(request):
    tax = None
    reconstruction_tax = None
    total_tax = None
    taxable_income = None
    error = None

    if request.method == "POST":
        try:
            income = Decimal(request.POST.get("income", "0"))

            if income < 0:
                raise ValueError("Income cannot be negative.")

            # Find the active 2026 income tax rule set
            rule_set = TaxRuleSet.objects.filter(
                tax_year=2026,
                tax_type="income_tax",
                is_active=True
            ).first()

            if not rule_set:
                raise ValueError(
                    "No active 2026 income tax rules were found."
                )

            # Find the correct tax bracket
            bracket = (
                TaxBracket.objects
                .filter(
                    rule_set=rule_set,
                    lower_limit__lte=income
                )
                .filter(
                    upper_limit__gt=income
                )
                .first()
            )

            # Handle the highest bracket
            if not bracket:
                bracket = (
                    TaxBracket.objects
                    .filter(
                        rule_set=rule_set,
                        lower_limit__lte=income,
                        upper_limit__isnull=True
                    )
                    .first()
                )

            if not bracket:
                raise ValueError(
                    "No tax bracket was found for this income."
                )

            # Calculate national income tax
            tax = (
                income * bracket.tax_rate
                - bracket.deduction
            )

            # Tax cannot be negative
            tax = max(tax, Decimal("0"))

            # Reconstruction Special Income Tax
            reconstruction_rate = TaxRule.objects.get(
                rule_set=rule_set,
                key="reconstruction_tax_rate"
            ).value

            reconstruction_tax = (
                tax * reconstruction_rate / Decimal("100")
            )

            total_tax = tax + reconstruction_tax

            taxable_income = income

        except (ValueError, TypeError, TaxRule.DoesNotExist):
            error = "Please enter a valid income amount."

    return render(
        request,
        "budgeting/tax_calculator.html",
        {
            "tax": tax,
            "reconstruction_tax": reconstruction_tax,
            "total_tax": total_tax,
            "taxable_income": taxable_income,
            "error": error,
        }
    )




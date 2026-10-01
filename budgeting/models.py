from django.db import models
from django.contrib.auth.models import User


class Income(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True)

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    source = models.CharField(max_length=100)
    date = models.DateField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.source} - {self.amount}"


class Expense(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
        )
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=100)
    date = models.DateField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.category} - {self.amount}"


class Budget(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
        )
    
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    month = models.DateField()

    def __str__(self):
        return f"{self.category} - {self.amount} - {self.month}"




class TaxRuleSet(models.Model):
    TAX_TYPES = [
        ("income_tax", "Income Tax"),
        ("resident_tax", "Resident Tax"),
        ("social_insurance", "Social Insurance"),
    ]
    






    tax_year = models.IntegerField(
        null=True,
        blank=True
        )
    tax_type = models.CharField(max_length=30, choices=TAX_TYPES)
    version = models.CharField(max_length=50)

    source_hash = models.CharField(
    max_length=64,
    null=True,
    blank=True)

    effective_from = models.DateField(
        null=True,
        blank=True
        )
    effective_to = models.DateField(null=True, blank=True)

    source_name = models.CharField(max_length=200)
    source_url = models.URLField()
    source_published = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    deductions_data = models.JSONField(default=list, blank=True)

    special_rules_data = models.JSONField(default=list, blank=True)

    future_changes_data = models.JSONField(default=list, blank=True)

    uncertainties_data = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tax_year} - {self.tax_type} - {self.version}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["source_url", "source_hash"],
                name="unique_tax_source_version",
            ),
        ]


class TaxRule(models.Model):
    rule_set = models.ForeignKey(
        TaxRuleSet,
        on_delete=models.CASCADE,
        related_name="rules"
    )




    key = models.CharField(max_length=100)

    value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    min_income = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )

    max_income = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )

    rate = models.DecimalField(
        max_digits=8,
        decimal_places=6,
        null=True,
        blank=True
    )

    fixed_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )

    unit = models.CharField(max_length=30, blank=True)

    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.key}: {self.value}"





class TaxBracket(models.Model):
    rule_set = models.ForeignKey(
        TaxRuleSet,
        on_delete=models.CASCADE,
        related_name="brackets"
    )

    lower_limit = models.DecimalField(
        max_digits=15,
        decimal_places=2
    )

    upper_limit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )

    tax_rate = models.DecimalField(
        max_digits=6,
        decimal_places=4
    )

    deduction = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    description = models.TextField(blank=True)

    def __str__(self):
        upper = self.upper_limit if self.upper_limit is not None else "and above"
        return f"{self.lower_limit} - {upper}: {self.tax_rate}"



    
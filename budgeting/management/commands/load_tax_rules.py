from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand
from budgeting.models import TaxRuleSet, TaxRule, TaxBracket


class Command(BaseCommand):
    help = "Load verified Japanese national income tax rules."

    def handle(self, *args, **options):

        # ---------------------------------------------------------
        # 2026 JAPAN NATIONAL INCOME TAX
        # ---------------------------------------------------------

        source_name = "National Tax Agency of Japan"
        source_url = (
            "https://www.nta.go.jp/publication/pamph/gensen/shikata_r08/"
        )

        rule_set, created = TaxRuleSet.objects.get_or_create(
            tax_year=2026,
            tax_type="income_tax",
            version="2026.1",
            defaults={
                "effective_from": date(2026, 1, 1),
                "effective_to": None,
                "source_name": source_name,
                "source_url": source_url,
                "source_published": date(2026, 1, 1),
                "is_active": True,
                "notes": (
                    "2026 Japanese national income tax rules. "
                    "Progressive income tax brackets and reconstruction "
                    "special income tax are recorded here. "
                    "2026 deduction reforms require separate tiered rules."
                ),
            },
        )

        if not created:
            self.stdout.write(
                self.style.WARNING(
                    "2026.1 income-tax rule set already exists. "
                    "Updating its active status."
                )
            )

        # ---------------------------------------------------------
        # PROGRESSIVE NATIONAL INCOME TAX BRACKETS
        # ---------------------------------------------------------

        brackets = [
            {
                "lower": Decimal("0"),
                "upper": Decimal("1950000"),
                "rate": Decimal("0.05"),
                "deduction": Decimal("0"),
                "description": "5% income tax bracket",
            },
            {
                "lower": Decimal("1950000"),
                "upper": Decimal("3300000"),
                "rate": Decimal("0.10"),
                "deduction": Decimal("97500"),
                "description": "10% income tax bracket",
            },
            {
                "lower": Decimal("3300000"),
                "upper": Decimal("6950000"),
                "rate": Decimal("0.20"),
                "deduction": Decimal("427500"),
                "description": "20% income tax bracket",
            },
            {
                "lower": Decimal("6950000"),
                "upper": Decimal("9000000"),
                "rate": Decimal("0.23"),
                "deduction": Decimal("636000"),
                "description": "23% income tax bracket",
            },
            {
                "lower": Decimal("9000000"),
                "upper": Decimal("18000000"),
                "rate": Decimal("0.33"),
                "deduction": Decimal("1536000"),
                "description": "33% income tax bracket",
            },
            {
                "lower": Decimal("18000000"),
                "upper": Decimal("40000000"),
                "rate": Decimal("0.40"),
                "deduction": Decimal("2796000"),
                "description": "40% income tax bracket",
            },
            {
                "lower": Decimal("40000000"),
                "upper": None,
                "rate": Decimal("0.45"),
                "deduction": Decimal("4796000"),
                "description": "45% income tax bracket",
            },
        ]

        for bracket in brackets:
            TaxBracket.objects.update_or_create(
                rule_set=rule_set,
                lower_limit=bracket["lower"],
                defaults={
                    "upper_limit": bracket["upper"],
                    "tax_rate": bracket["rate"],
                    "deduction": bracket["deduction"],
                    "description": bracket["description"],
                },
            )

        # ---------------------------------------------------------
        # RECONSTRUCTION SPECIAL INCOME TAX
        # ---------------------------------------------------------

        TaxRule.objects.update_or_create(
            rule_set=rule_set,
            key="reconstruction_tax_rate",
            defaults={
                "value": Decimal("2.10"),
                "unit": "percent",
                "description": (
                    "Special income tax for reconstruction is "
                    "2.1% of calculated national income tax."
                ),
            },
        )



                # 2026 Employment Income Deduction
        employment_deduction_rules = [
            {
                "key": "employment_income_deduction_minimum",
                "value": Decimal("690000"),
                "min_income": Decimal("0"),
                "max_income": Decimal("1625000"),
                "unit": "JPY",
                "description": (
                    "2026 minimum employment income deduction."
                ),
            },
        ]

        for rule in employment_deduction_rules:
            TaxRule.objects.update_or_create(
                rule_set=rule_set,
                key=rule["key"],
                defaults={
                    "value": rule["value"],
                    "min_income": rule["min_income"],
                    "max_income": rule["max_income"],
                    "unit": rule["unit"],
                    "description": rule["description"],
                },
            )

        # ---------------------------------------------------------
        # MARK THIS VERSION ACTIVE
        # ---------------------------------------------------------

        TaxRuleSet.objects.exclude(
            id=rule_set.id
        ).filter(
            tax_year=2026,
            tax_type="income_tax"
        ).update(is_active=False)

        rule_set.is_active = True
        rule_set.save()

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Successfully loaded 2026 Japanese income-tax rules."
            )
        )
        self.stdout.write(
            f"Rule set: {rule_set.version}"
        )
        self.stdout.write(
            f"Tax brackets loaded: {len(brackets)}"
        )
        self.stdout.write(
            "Reconstruction tax: 2.10%"
        )
        self.stdout.write("")

        
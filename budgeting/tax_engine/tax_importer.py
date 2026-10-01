import hashlib

from budgeting.models import TaxRuleSet, TaxRule, TaxBracket

def import_tax_data(data, source_url, source_text):
    """
    Import validated AI tax data into the database.
    """

    source_hash = hashlib.sha256(
        source_text.encode("utf-8")
    ).hexdigest()

    

    existing_rule_set = TaxRuleSet.objects.filter(
        source_url=source_url,
        source_hash=source_hash
    ).first()

    if existing_rule_set:
        fields_updated = []

    for field, key in [
        ("deductions_data", "deductions"),
        ("special_rules_data", "special_rules"),
        ("future_changes_data", "future_changes"),
        ("uncertainties_data", "uncertainties"),
    ]:
        if not getattr(existing_rule_set, field):
            value = data.get(key) or []

            if value:
                setattr(existing_rule_set, field, value)
                fields_updated.append(field)

    if fields_updated:
        fields_updated.append("updated_at")
        existing_rule_set.save(update_fields=fields_updated)

    return existing_rule_set


    version = f"auto-{source_hash[:12]}"

    rule_set = TaxRuleSet.objects.create(
        tax_year=data.get("tax_year"),
        tax_type=data.get("tax_type"),
        version=version,
        source_hash=source_hash,
        effective_from=data.get("effective_from"),
        effective_to=data.get("effective_to"),
        source_name="National Tax Agency",
        source_url=source_url,
        source_published=data.get("source_reference_date"),
        is_active=False,
        deductions_data=data.get("deductions") or [],
        special_rules_data=data.get("special_rules") or [],
        future_changes_data=data.get("future_changes") or [],
        uncertainties_data=data.get("uncertainties") or [],
        
        notes="Imported automatically from NTA source using AI extraction."
    )

    for bracket in data.get("brackets", []):
        TaxBracket.objects.create(
            rule_set=rule_set,
            lower_limit=bracket.get("lower_limit"),
            upper_limit=bracket.get("upper_limit"),
            tax_rate=bracket.get("rate"),
            deduction=bracket.get("deduction") or 0,
            description=bracket.get("description") or ""
        )

    return rule_set
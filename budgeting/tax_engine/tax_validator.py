def validate_tax_data(data):
    """
    Perform generic checks on AI-extracted tax data.

    This function does NOT contain Japanese tax rates or brackets.
    It only checks whether the extracted data is structurally valid.
    """

    errors = []

    # 1. Check that the AI returned a dictionary.
    if not isinstance(data, dict):
        return False, ["AI result is not a valid data object."]

    # 2. Check required top-level fields.
    required_fields = [
        "tax_type",
        "source_reference_date",
        "tax_year",
        "effective_from",
        "effective_to",
        "brackets",
        "deductions",
        "special_rules",
        "future_changes",
        "uncertainties",
    ]

    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    # Stop if the basic structure is missing.
    if errors:
        return False, errors

    # 3. Check that lists are actually lists.
    list_fields = [
        "brackets",
        "deductions",
        "special_rules",
        "future_changes",
        "uncertainties",
    ]

    for field in list_fields:
        if not isinstance(data[field], list):
            errors.append(f"{field} must be a list.")

    if errors:
        return False, errors

    # 4. Validate each bracket.
    for number, bracket in enumerate(data["brackets"], start=1):

        if not isinstance(bracket, dict):
            errors.append(
                f"Bracket {number} is not a valid object."
            )
            continue

        required_bracket_fields = [
            "lower_limit",
            "upper_limit",
            "rate",
            "deduction",
            "description",
        ]

        for field in required_bracket_fields:
            if field not in bracket:
                errors.append(
                    f"Bracket {number} is missing: {field}"
                )

        # Check lower limit.
        lower = bracket.get("lower_limit")

        if lower is not None:
            if not isinstance(lower, (int, float)):
                errors.append(
                    f"Bracket {number}: lower_limit must be a number or null."
                )
            elif lower < 0:
                errors.append(
                    f"Bracket {number}: lower_limit cannot be negative."
                )

        # Check upper limit.
        upper = bracket.get("upper_limit")

        if upper is not None:
            if not isinstance(upper, (int, float)):
                errors.append(
                    f"Bracket {number}: upper_limit must be a number or null."
                )
            elif upper < 0:
                errors.append(
                    f"Bracket {number}: upper_limit cannot be negative."
                )

        # Check that upper is greater than lower.
        if (
            isinstance(lower, (int, float))
            and isinstance(upper, (int, float))
            and upper <= lower
        ):
            errors.append(
                f"Bracket {number}: upper_limit must be greater than lower_limit."
            )

        # Check rate.
        rate = bracket.get("rate")

        if rate is not None:
            if not isinstance(rate, (int, float)):
                errors.append(
                    f"Bracket {number}: rate must be a number or null."
                )
            elif rate < 0 or rate > 1:
                errors.append(
                    f"Bracket {number}: rate must be between 0 and 1."
                )

        # Check deduction.
        deduction = bracket.get("deduction")

        if deduction is not None:
            if not isinstance(deduction, (int, float)):
                errors.append(
                    f"Bracket {number}: deduction must be a number or null."
                )

    # 5. Check bracket ordering.
    brackets = data["brackets"]

    previous_lower = None

    for number, bracket in enumerate(brackets, start=1):

        lower = bracket.get("lower_limit")

        if not isinstance(lower, (int, float)):
            continue

        if previous_lower is not None and lower <= previous_lower:
            errors.append(
                f"Bracket {number}: lower_limit is not greater than "
                f"the previous bracket."
            )

        previous_lower = lower

    # 6. Report whether the data passed.
    if errors:
        return False, errors

    return True, []
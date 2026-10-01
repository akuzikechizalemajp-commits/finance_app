from budgeting.tax_engine.nta_source import fetch_nta_page
from budgeting.tax_engine.tax_ai import analyze_tax_text
from budgeting.tax_engine.tax_validator import validate_tax_data
from budgeting.tax_engine.tax_importer import import_tax_data

url = "https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/2260.htm"


print("Downloading NTA information...")

text = fetch_nta_page(url)

print("NTA information downloaded.")
print()

print("Sending information to AI...")
print()

result = analyze_tax_text(text)

print("AI returned structured data:")
print("==============================")

for key, value in result.items():
    print(f"\n{key}:")
    print(value)

print()
print("==============================")
print("JSON extraction successful!")

print()
print("Validating extracted tax data...")
print("==============================")

is_valid, errors = validate_tax_data(result)

if is_valid:
    print("VALIDATION PASSED")
    print("The extracted data passed the generic checks.")
else:
    print("VALIDATION FAILED")
    print()

    for error in errors:
        print(f"- {error}")

print("==============================")


print()
print("Importing tax data into database...")
print("==============================")

rule_set = import_tax_data(
    result,
    url,
    text
)

print("IMPORT SUCCESSFUL")
print(f"Rule set ID: {rule_set.id}")
print(f"Version: {rule_set.version}")
print(f"Source hash: {rule_set.source_hash}")

print("==============================")
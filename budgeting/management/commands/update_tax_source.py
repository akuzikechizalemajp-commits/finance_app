from django.core.management.base import BaseCommand, CommandError

from budgeting.tax_engine.tax_validator import validate_tax_data
from budgeting.tax_engine.nta_source import fetch_nta_page
from budgeting.tax_engine.tax_ai import analyze_tax_text
from budgeting.tax_engine.tax_importer import import_tax_data

class Command(BaseCommand):
    help = "Import tax rules from an official NTA webpage"

    def add_arguments(self, parser):
        parser.add_argument(
            "url",
            type=str,
            help="URL of the NTA webpage to import"
        )

    def handle(self, *args, **options):
        url = options["url"]

        self.stdout.write(f"NTA source: {url}")
        self.stdout.write("Downloading NTA information...")

        text = fetch_nta_page(url)

        self.stdout.write(
            self.style.SUCCESS("NTA information downloaded!")
        )

        self.stdout.write(f"Characters downloaded: {len(text)}")

        self.stdout.write("Sending NTA information to AI...")

        data = analyze_tax_text(text)

        self.stdout.write(
            self.style.SUCCESS("AI extraction completed!")
        )

        self.stdout.write(f"Tax type: {data.get('tax_type')}")
        self.stdout.write(
            f"Brackets extracted: {len(data.get('brackets', []))}"
        )
        self.stdout.write(
            f"Special rules: {len(data.get('special_rules', []))}"
        )
        self.stdout.write(
            f"Future changes: {len(data.get('future_changes', []))}"
        )
        self.stdout.write(
            f"Uncertainties: {len(data.get('uncertainties', []))}"
        )


        self.stdout.write("Validating extracted tax data...")
        
        is_valid, errors = validate_tax_data(data)
        
        
        if not is_valid:
            
            for error in errors:
                
                self.stderr.write(str(error))
                
                
                raise CommandError("Tax data validation failed.")

    
        self.stdout.write(
            
            self.style.SUCCESS("VALIDATION PASSED")
            )




        self.stdout.write("Importing tax data into database...")
        
        rule_set = import_tax_data(
            data,
            url,
            text
            )

        
        self.stdout.write(
            
            self.style.SUCCESS("IMPORT SUCCESSFUL")
            )
        
        self.stdout.write(f"Rule set ID: {rule_set.id}")
        
        self.stdout.write(f"Version: {rule_set.version}")
        
        self.stdout.write(f"Source hash: {rule_set.source_hash}")



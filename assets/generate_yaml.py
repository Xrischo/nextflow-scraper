import csv
import yaml
import sys

if len(sys.argv) < 2:
    raise ValueError("Please provide a CSV file path as an argument.")
csv_file = sys.argv[1]

def parse_selectors(selectors_str):
    selectors = {}
    for item in selectors_str.split(';'):
        key, xpath = item.split(':', 1)
        selectors[key.strip()] = xpath.strip()
    return selectors

def generate_yaml(csv_file, output_file):
    sources = []

    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            source = {
                "name": row["name"],
                "url": row["url"],
                "method": row["method"],
                "headers": row["headers"],
                "selectors": parse_selectors(row["selectors"])
            }
            sources.append(source)

    with open(output_file, 'w') as yaml_file:
        yaml.dump({"sources": sources}, yaml_file, default_flow_style=False)

    print(f"✅ YAML configuration generated: {output_file}")

# Example Usage:
generate_yaml(csv_file, "scraper_config.yaml")
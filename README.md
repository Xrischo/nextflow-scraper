# Nextflow pipeline for a web-scraper with chart generation

## Overview
This pipeline is designed for Debian-based Linux distributions with Nextflow installed. It automates docker download and setup, building the required image and running the application. It comes with a web-based interface to customise the web-scraping definition (sources, names, selectors)

## Features
- **Automated Setup:** Installs Docker, Buildx, and builds the provided container image.
- **Configurable Data Scraping:** Generates a YAML scraper configuration from a customisable CSV file.
- **Data Collection & Storage:** Uses a Python script to collect data from multiple sources and stores it in a database.
- **Visualisation:** Generates charts based on collected data and user-defined filters.
- **Web Interface:** Enables users to manage data sources, database structure and table contents.

## Prerequisites
You need Nextflow installed on a Debian-based Linux distribution

## Installation & Usage
1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```
2. **Edit the scraper_sources.csv or access the web interface (edit_sources.html):**
   The sources provided are an example of the convention required, and the application should work with them.
2. **Run the pipeline:**
   ```bash
   nextflow run main.nf
   ```
   The following parameters can be provided:
   -  `--rebuildImage true/false` - Default false. Rebuild the container image (using --no-cache)
   -  `--overwrite true/false` - Default false. Delete the old table for a data source and create a new one
   -  `--generateChart` - Default false. Generate a chart at the end of the scraping process. NOTE: Requires the additional parameters below
   -  `--chartType line/bar/pie` - Chooses the type of the graph
   -  `--sourceTable <table>` - Chooses the table to use after the scraping
   -  `--columnX <name>` - The X axis in the chart (categories for pie charts)
   -  `--columnY <name>` - The Y axis in the chart (values for pie charts)
   -  `--filter <SQL>` - Any filters for the resulting SQL script
   -  `--chartName <name>` - The output of the chart

*Note: If a scraped value is a date, the application tries to convert it into 'YYYY-MM-DD' format. When passing filters, wrap the operands in quotes, for example:
`--filter 'date' > '2025-01-01'`


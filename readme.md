# OSINT Report Generator

## Overview
This project is an assistant agent designed to generate Open-Source Intelligence (OSINT) reports in PDF format from text files. It integrates with a Customer Relationship Management (CRM) system (Salesforce) for logging findings, generates data visualizations, and uses a lightweight local language model (DistilGPT2) to process text while ensuring security compliance. The tool is optimized for low-resource environments (e.g., 16GB RAM, CPU-only).

## Features
- **Input Parsing**: Extracts structured data (IP addresses, company names, contacts, and usage statistics) from disordered text files using regex patterns.
- **Data Visualization**: Creates bar charts to visualize usage data using Matplotlib, saved as PNG files for inclusion in reports.
- **Text Processing**: Utilizes DistilGPT2, a lightweight transformer model, to organize and summarize extracted data into a structured format suitable for reports.
- **CRM Integration**: Logs investigation findings to Salesforce as cases, including summaries, company details, usage data, and contacts.
- **PDF Report Generation**: Produces professional PDF reports using ReportLab, incorporating summaries, extracted data, visualizations, and recommendations.
- **Security Compliance**: Processes data locally with a lightweight model to minimize external dependencies and ensure data privacy.
---
![how it works](https://github.com/Miyagi55/osint_report_agent/blob/main/osint_report_assistant3.png)

## How It Works
1. **Input Processing**:
   - The script reads a text file (e.g., `sample.txt`) containing disordered OSINT data.
   - Regex patterns extract key information such as IP addresses, company names, contacts, and usage statistics.

2. **Data Visualization**:
   - Usage data is visualized as a bar chart, with counts extracted from usage entries (e.g., "50 times in 30 days").
   - The chart is saved as a PNG file (`usage_chart.png`) for inclusion in the PDF report.

3. **Text Organization**:
   - The DistilGPT2 model processes the extracted data to generate a structured JSON output, categorizing information into a summary, company details, usage data, and contacts.
   - Fallback parsing ensures robustness if the model's JSON output is imperfect.

4. **CRM Logging**:
   - Structured data is logged to Salesforce as a new case, including a summary and categorized details.
   - Users must provide their Salesforce credentials and security token.

5. **PDF Report Generation**:
   - A PDF report is created using ReportLab, including:
     - A title and metadata (date, case ID).
     - Sections for summary, company information, usage data, a usage visualization, key contacts, and recommendations.
     - The generated chart is embedded in the report.

## Dependencies
- Python 3.x
- Libraries: `transformers`, `reportlab`, `matplotlib`, `simple_salesforce`, `re`, `json`, `datetime`, `os`
- Model: `distilgpt2` (downloaded automatically via Hugging Face's `transformers`)



  

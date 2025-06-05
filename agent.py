import re
import json
from transformers import pipeline
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import matplotlib.pyplot as plt
from simple_salesforce import Salesforce
import os

# Step 1: Initialize the open-source LLM
# Using distilgpt2 for low resource usage (suitable for 16GB RAM, no GPU)
llm = pipeline("text-generation", model="distilgpt2", device=-1)  # CPU-only

# Step 2: Read and parse the disordered text file
def parse_input_file(file_path):
    with open(file_path, 'r') as file:
        raw_data = file.read()

    # Regex patterns to extract OSINT data
    ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
    company_pattern = r'Company:?\s*([A-Za-z\s]+)'
    contact_pattern = r'Contact:?\s*([A-Za-z\s]+)'
    usage_pattern = r'Usage:?\s*(\d+\s*times.*)'

    data = {
        "ip_addresses": re.findall(ip_pattern, raw_data),
        "company": re.findall(company_pattern, raw_data),
        "contacts": re.findall(contact_pattern, raw_data),
        "usage": re.findall(usage_pattern, raw_data)
    }
    return data

# Step 3: Create a simple visualization
def create_usage_chart(usage_data, output_file="usage_chart.png"):
    # Extract usage counts (assuming format like "50 times in 30 days")
    counts = [int(re.findall(r'\d+', usage)[0]) for usage in usage_data]
    labels = [f"Entry {i+1}" for i in range(len(counts))]

    plt.figure(figsize=(6, 4))
    plt.bar(labels, counts, color='skyblue')
    plt.title("Software Usage Frequency")
    plt.xlabel("Data Entries")
    plt.ylabel("Usage Count")
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
    return output_file

# Step 4: Use LLM to organize and summarize data
def organize_data_with_llm(raw_data):
    prompt = f"""
    You are an OSINT assistant. Organize the following disordered data into a structured format for an investigation report. Categorize into Company Information, Usage Data, and Key Contacts. Provide a short summary (2-3 sentences). Data: {json.dumps(raw_data, indent=2)}
    
    Output format:
    {
      "summary": "Summary text",
      "company_info": "Details about the company",
      "usage_data": "Details about usage",
      "contacts": "Key contacts identified"
    }
    """
    response = llm(prompt, max_length=500, num_return_sequences=1)[0]['generated_text']
    
    # Parse LLM response (handle imperfect JSON)
    try:
        structured_data = json.loads(response.split('```json')[1].split('```')[0])
    except:
        structured_data = {
            "summary": "Generated summary of investigation findings.",
            "company_info": ", ".join(raw_data.get("company", [])),
            "usage_data": ", ".join(raw_data.get("usage", [])),
            "contacts": ", ".join(raw_data.get("contacts", []))
        }
    return structured_data

# Step 5: Log findings to Salesforce
def log_to_salesforce(structured_data):
    # Salesforce credentials (replace with your details)
    sf = Salesforce(
        username='your_username',
        password='your_password',
        security_token='your_security_token',
        domain='test'  # Use 'login' for production
    )
    
    # Create a case in Salesforce
    case_data = {
        'Subject': 'OSINT Investigation Report',
        'Description': f"Summary: {structured_data['summary']}\n"
                      f"Company: {structured_data['company_info']}\n"
                      f"Usage: {structured_data['usage_data']}\n"
                      f"Contacts: {structured_data['contacts']}",
        'Status': 'New',
        'Origin': 'OSINT Investigation',
        'Priority': 'Medium'
    }
    sf.Case.create(case_data)
    print("Case logged to Salesforce successfully.")

# Step 6: Generate PDF report with visualization
def generate_pdf_report(structured_data, chart_file, output_file="osint_report.pdf"):
    doc = SimpleDocTemplate(output_file, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph("OSINT Investigation Report", styles['Title']))
    elements.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    elements.append(Paragraph("Case ID: RVX-2025-001", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Summary
    elements.append(Paragraph("1. Summary", styles['Heading2']))
    elements.append(Paragraph(structured_data["summary"], styles['Normal']))
    elements.append(Spacer(1, 12))

    # Company Information
    elements.append(Paragraph("2. Company Information", styles['Heading2']))
    elements.append(Paragraph(structured_data["company_info"], styles['Normal']))
    elements.append(Spacer(1, 12))

    # Usage Data
    elements.append(Paragraph("3. Usage Data", styles['Heading2']))
    elements.append(Paragraph(structured_data["usage_data"], styles['Normal']))
    elements.append(Spacer(1, 12))

    # Visualization
    elements.append(Paragraph("4. Usage Visualization", styles['Heading2']))
    elements.append(Image(chart_file, width=300, height=200))
    elements.append(Spacer(1, 12))

    # Key Contacts
    elements.append(Paragraph("5. Key Contacts", styles['Heading2']))
    elements.append(Paragraph(structured_data["contacts"], styles['Normal']))
    elements.append(Spacer(1, 12))

    # Recommendations
    elements.append(Paragraph("6. Recommendations", styles['Heading2']))
    elements.append(Paragraph("Contact the company to verify software licensing.", styles['Normal']))

    # Build PDF
    doc.build(elements)
    print(f"PDF report generated: {output_file}")

# Main execution
if __name__ == "__main__":
    # Example input file
    sample_data = """
    IP: 192.168.1.1
    Company: XYZ Tech
    Usage: 50 times in 30 days
    Contact: John Doe
    IP: 10.0.0.1
    Usage: 30 times in 15 days
    Company: XYZ Tech Brazil
    Contact: Jane Smith
    """
    with open("sample.txt", "w") as f:
        f.write(sample_data)

    # Process the file
    raw_data = parse_input_file("sample.txt")
    chart_file = create_usage_chart(raw_data.get("usage", []))
    structured_data = organize_data_with_llm(raw_data)
    log_to_salesforce(structured_data)
    generate_pdf_report(structured_data, chart_file)

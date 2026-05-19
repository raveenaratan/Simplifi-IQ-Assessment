from weasyprint import HTML

def generate_pdf_report(lead_name: str, company_name: str, insights: dict, output_path: str):
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{ size: letter; margin: 1in; }}
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #2D3748; line-height: 1.6; }}
            .brand {{ color: #4F46E5; font-size: 14px; font-weight: bold; letter-spacing: 1px; text-transform: uppercase; }}
            h1 {{ font-size: 28px; color: #1A202C; margin-top: 5px; margin-bottom: 25px; border-bottom: 2px solid #E2E8F0; padding-bottom: 15px; }}
            h2 {{ font-size: 18px; color: #4F46E5; margin-top: 30px; }}
            p, li {{ font-size: 14px; }}
            .meta-box {{ background-color: #F7FAFC; border: 1px solid #E2E8F0; padding: 15px; border-radius: 6px; margin-bottom: 25px; }}
            .card {{ background-color: #FFFFFF; border-left: 4px solid #4F46E5; padding: 5px 0px 5px 15px; margin-bottom: 20px; }}
            ul {{ padding-left: 20px; }}
            li {{ margin-bottom: 8px; }}
        </style>
    </head>
    <body>
        <div class="brand">SimplifIQ Automated Systems</div>
        <h1>Strategic Operational Audit</h1>
        
        <div class="meta-box">
            <strong>Prepared For:</strong> {lead_name}<br>
            <strong>Target Organization:</strong> {company_name}<br>
            <strong>Analysis Framework:</strong> Generated via Autonomous Pipeline AI Engine
        </div>
        
        <h2>Executive Summary</h2>
        <div class="card">
            <p>{insights['summary']}</p>
        </div>
        
        <h2>Identified Workflow Friction Points</h2>
        <ul>
            {"".join([f"<li>{point}</li>" for point in insights['pain_points']])}
        </ul>
        
        <h2>Strategic Automation Recommendations</h2>
        <ul>
            {"".join([f"<li>{rec}</li>" for rec in insights['recommendations']])}
        </ul>
    </body>
    </html>
    """
    HTML(string=html_content).write_pdf(output_path)
    print(f"[Success] PDF generated cleanly at: {output_path}")

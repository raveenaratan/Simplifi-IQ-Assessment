import os
import requests
from bs4 import BeautifulSoup
import json

def enrich_company_data(company_name: str, website: str) -> dict:
    raw_text_summary = ""
    
    if not website.startswith("http"):
        website = f"https://{website}"
        
    try:
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
        response = requests.get(website, headers=headers, timeout=7)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                raw_text_summary = meta_desc['content']
            else:
                raw_text_summary = " ".join([p.text for p in soup.find_all('p')[:3]])
    except Exception as e:
        print(f"[Warning] Scraper blocked or timed out for {website}: {e}. Proceeding to LLM Fallback.")

    # Call LLM generation layer to compile highly contextual business insights
    return generate_ai_insights(company_name, raw_text_summary)

def generate_ai_insights(company_name: str, scraped_context: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        
        return get_hardcoded_fallback(company_name)
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    prompt = f"""
    You are an expert B2B Software and Systems Operations consultant.
    Analyze this target company: {company_name}. Extra scraped web text: {scraped_context}.
    Identify 3 highly tailored, specific operational workflow bottlenecks they likely face (e.g., manual data entry, customer handoffs).
    Provide 2 structural technical recommendations using automation.
    Output your response STRICTLY as a valid JSON object matching this exact schema:
    {{
        "summary": "Clear, curated overview of what they do.",
        "pain_points": ["point 1", "point 2", "point 3"],
        "recommendations": ["rec 1", "rec 2"]
    }}
    Do not wrap it in markdown block tags like ```json. Output raw JSON code text only.
    """
    
    try:
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=15)
        response_json = response.json()
        
        raw_output = response_json['candidates'][0]['content']['parts'][0]['text'].strip()
        return json.loads(raw_output)
    except Exception as e:
        print(f"[Error] AI Generation phase failed: {e}. Injecting default framework.")
        return get_hardcoded_fallback(company_name)

def get_hardcoded_fallback(company_name: str) -> dict:
    return {
        "summary": f"{company_name} is an active digital market player focused on operational delivery.",
        "pain_points": [
            "Data fragmentation across multiple unlinked operational SaaS applications.",
            "Manual tracking of incoming customer touchpoints causing response lag.",
            "Time intensive administrative document drafting during client onboarding."
        ],
        "recommendations": [
            "Deploy central integration hubs (webhooks) to route real-time operational data.",
            "Incorporate automated document generation systems to optimize client facing tasks."
        ]
    }

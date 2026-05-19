# Simplifi-IQ-Assessment

**Architectural Documentation:** Autonomous Lead Enrichment & Audit Pipeline
## 1. System Overview & Architecture
This system is an automated, event-driven backend service that takes raw, early-stage leads and turns them into highly customized B2B operational audits where no manual steps required. It’s designed to deliver tailored insights right from the start, so businesses can focus on what matters most.

To keep things dependable and avoid frustrating web timeouts for clients, the system separates the quick lead intake from the more time-consuming data extraction and processing. This is done using asynchronous background tasks, so everything runs smoothly without delays for users.

**System Architecture Pipeline**
**Ingestion:** When a new lead comes in, the webhook payload is instantly picked up by a snappy FastAPI endpoint. This quick handoff makes sure no data slips through the cracks and keeps everything running smoothly right from the start.

**Validation**: Pydantic thoroughly examines the incoming data to ensure that everything is in order before assigning a unique tracking ID. This includes verifying the validity of any email addresses and double-checking the structure. This attention to detail guarantees that the information is trustworthy from the beginning and helps avoid problems later.

**Asynchronous Handoff:** The API responds with a 200 OK success status instantly to the client, pushing the workload to a background task runner to process downstream jobs out-of-band.

## 2. Component Design & Operational Flow
A. **Resilient Web Scraping & Data Enrichment (enricher.py)**
The system uses BeautifulSoup wrapped with structured header modifications to extract site metadata and landing page context from the lead's domain.

The Layered Fallback Design: Knowing web scraping is brittle due to dynamic frontend rendering or anti-bot blocks, the pipeline features a critical safety loop. If a request times out or is blocked, the service gracefully catches the exception, avoids a system crash, and switches instantly to a parameterized fallback prompt. This prompt leverages the LLM's vast domain knowledge base to predict systemic operational challenges typical of the target company's niche.

B. **Dynamic Context Synthesis (AI Engine)**
The raw scraped data is injected into an advanced prompt engineered for a Large Language Model (e.g., Google Gemini).

Rather than standard conversational syntax, the LLM is tightly bound via programmatic instructions to return strictly structured, minified JSON raw data. This engineering decision ensures the downstream generation modules can parse variables seamlessly without dealing with unpredictable text formatting.

C. **Visual Document Compilation (reporter.py)**
Instead of hard-coding raw visual coordinates using low-level canvas vectors, the document module compiles data into a semantic HTML5/CSS3 template layout.

This structured page is then compiled natively into a high-fidelity, print-ready PDF via WeasyPrint. This choice guarantees responsive typography, clean tables, and sharp, professional layouts that mimic bespoke human consulting reports.

D. **Multi-Channel Distribution & Logging Pipeline (worker.py)**
**Email Engine:** Dispatches the final compiled PDF using a structured multi-part MIME protocol over a secure SMTP gateway server.

**Live Sheets Tracker:** Appends structured engagement metrics (Timestamp, Lead Data, Payload status) to a centralized Google Sheet using the authenticated Google Cloud Service Account.

**Drive Archiving:** Concurrently uploads a persistent backup copy of PDF into a secure Google Drive storage directory using unique string labels.

## 3. Engineering Decisions, Trade-offs & Assumptions
**Local Development Environment:** WSL over Native Windows
**Decision: **The project was deliberately built and validated inside Windows Subsystem for Linux (WSL).

**Justification:** Because of the way system libraries and rendering engines like pango and cairo, which WeasyPrint depends on interact, running on native Windows can create a lot of issues. You can neatly isolate all system dependencies by working within a Linux container that closely resembles actual cloud environments (such as AWS EC2, Docker, etc Render). No matter where you launch, this method ensures a smooth deployment and avoids library conflicts.

**Concurrency Framework:** Built-in BackgroundTasks vs. Dedicated Brokers
**Trade-off:** For this rapid prototyping assessment phase, FastAPI's built-in BackgroundTasks was prioritized over a complex Celery + Redis cluster arrangement.

**Reasoning:** Without sacrificing asynchronous execution requirements, this design constraint ensures that the evaluator may spin up and run the complete pipeline with a single terminal execution script, thereby reducing deployment overhead and local infrastructure dependencies.

## 4. Edge Case Handling & System Risk Mitigation

| Real-World Scenario | System Risk Mitigation |
| :--- | :--- |
| **Scraper Blocked / 403 Forbidden** | If something goes wrong with a request, the system catches it smoothly. It uses smart inference to log what happened, then automatically falls back on industry-standard defaults to keep things moving without interruption. This way, even unexpected bumps in the road don’t slow down the workflow. |
| **Malformed / Missing Input Fields** | To avoid wasting processing power, Pydantic steps in right at the API gateway, checking incoming data before it can move any further. If something doesn’t match the expected format, it sends a clear error message back to the client. This way, only valid requests are allowed through, keeping everything efficient and straightforward. |
| **Google Cloud / API Outages** | The tracking sequence separates its tasks. If the Sheets or Drive APIs time out, the exception is caught locally so that the email delivery module still successfully sends out the client report. |

## 5.Local Quickstart Instructions (For Evaluators)

Follow these steps to set up and run the prototype locally within your WSL (Ubuntu) environment.

### 1. System Binaries Installation
Install the necessary system-level dependencies required by `WeasyPrint` for rendering HTML templates into high-fidelity PDFs:
```bash
sudo apt update && sudo apt install -y build-essential python3-dev python3-pip python3-venv libpango-1.0-0 libpangocairo-1.0-0 libcairo2 libgirepository-1.0-1
```

### 2. Environment Activation & Dependencies Install
Navigate to your project root folder, spin up a clean virtual environment, and install the required Python packages:
```bash
python3 -m venv venv && source venv/bin/activate
pip install fastapi uvicorn pydantic requests beautifulsoup4 weasyprint google-api-python-client google-auth python-dotenv "pydantic[email]"
```

### 3. Execution Setup
Populate your configuration variables in a .env file located in the project root directory. Once configured, start up the unified service pipeline node:
```bash
python main.py or python3 main.py
```

### 4. Testing the Pipeline
Open a separate client shell window and use the curl request script below to watch the asynchronous, end-to-end data pipeline seamlessly run through to completion!
```bash
curl -X POST "[http://127.0.0.1:8000/api/v1/leads](http://127.0.0.1:8000/api/v1/leads)" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Alex Mercer",
       "email": "alex.mercer@example.com",
       "company_name": "Stark Industries",
       "company_website": "[https://www.google.com](https://www.google.com)"
     }'
```


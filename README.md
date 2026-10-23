# Grant Intelligence Agent

An AI-powered Python pipeline that extracts structured grant opportunities from emails using a local LLM, making funding information easier to organise, review, and analyse.

## Features

- **Email Processing:** Fetches and processes emails to identify potential grant opportunities.
- **LLM-Powered Extraction:** Uses Llama 3 to extract grant details from email bodies.
- **Structured Data Extraction:** Captures grant titles, providers, categories, funding amounts, deadlines, eligibility criteria, links, and confidence scores.
- **CSV Export:** Exports extracted grants into a structured CSV file compatible with Google Sheets.
- **Source Tracking:** Records the originating email subject for each extracted grant.
- **Input Validation:** Skips short or empty email bodies and grant entries without titles.

## Tech Stack

- **Language:** Python
- **AI Model:** Llama 3
- **Data Export:** Python CSV module
- **Components:** `EmailReader`, `GrantExtractor`

## Getting Started

1. Clone the repository:
   ```bash
   git clone <[repository-url](https://github.com/gw3nnipi3/grant-intelligence-agent/)>
   cd grant-intelligence-agent
2. Install the required dependencies.
3. Run the pipeline:
   ```bash
   python main.py

## Output

The pipeline generates grants_output.csv containing:

| Field | Description |
|---|---|
| `title` | Grant opportunity title |
| `provider` | Funding organisation |
| `category` | Grant category |
| `amount` | Available funding amount |
| `deadline` | Application deadline |
| `eligibility` | Eligibility requirements |
| `link` | Grant information or application URL |
| `confidence` | Extraction confidence score |
| `source` | Original email subject |

## Workflow

1. Fetch and process up to 30 emails.
2. Skip emails with empty or short bodies.
3. Extract grant information using Llama 3.
4. Clean and validate extracted fields.
5. Display the results and export them to CSV.

## Future Improvements

- Expand grant data sources.
- Improve matching accuracy and ranking.
- Automate deadline tracking and application reminders.

## Disclaimer

Grant information should be verified against official funding sources before applying.

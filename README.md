# Job Extractor

A small REST API that turns the raw text of a job posting into structured, verified JSON using an LLM (Google Gemini), **without inventing data**.

Every value the AI returns must be traceable to the original posting. Anything that cannot be found in the text is removed before the response is sent.

## Why this project

LLMs are great at reading unstructured text, but they sometimes "fill the gaps" with plausible information that was never there: a company name, a salary, a skill. For job-related tools that is unacceptable.

This project explores a simple pattern to reduce that risk:

1. **Prompt rules**: the model is told to copy values word for word and use `null` when something is not stated.
2. **Schema constraints**: the response must match a Pydantic model (for example, `modality` can only be `remote`, `hybrid` or `onsite`).
3. **Verification in code**: every copied value and every skill `source` is checked against the original text. If it is not there, it is dropped.

## Features

- `POST /extract-job`: extracts title, company, modality, location, salary, contract type, required skills and nice-to-have skills.
- Each skill includes a `source` field with the exact phrase from the posting it came from.
- Values such as "Salario a convenir", "1 SMMLV" or "Obra o labor" are kept as written, never converted or calculated.
- Ambiguous modalities (for example "Remoto / Presencial") keep the original phrase in `modality_source` and set `modality` to `null`.
- Swappable AI provider layer: Gemini today, any other LLM by adding one class.
- Clear error handling: invalid input returns `422`; AI failures return a generic `502` while details are only logged on the server.
- 23 automated tests that run offline in seconds, using a fake AI provider.

## Tech stack

- Python 3.12
- FastAPI + Pydantic
- Google Gen AI SDK (`google-genai`), model configurable via environment variable
- pytest + FastAPI TestClient

## How it works

```
posting text
    │
    ▼
ExtractRequest validation (non-empty, max 20,000 chars)
    │
    ▼
Prompt with extraction rules (posting wrapped in <posting> tags)
    │
    ▼
LLM provider (Gemini) ── structured JSON output
    │
    ▼
Pydantic validation (JobPosting schema)
    │
    ▼
Verification: drop every value not found in the original text
    │
    ▼
JSON response
```

## Project structure

```
job-extractor/
├── app/
│   ├── main.py            # FastAPI app, endpoints and error handling
│   ├── schemas.py         # Pydantic models
│   ├── extractor.py       # prompt + provider call + validation + verification
│   ├── verify.py          # anti-hallucination checks
│   └── providers/
│       ├── base.py        # LLMProvider interface and LLMProviderError
│       └── gemini.py      # Gemini implementation
├── tests/
│   ├── fakes.py           # fake provider used by the tests
│   ├── test_verify.py
│   ├── test_extractor.py
│   └── test_api.py
├── .env.example
├── pytest.ini
└── requirements.txt
```

## Getting started

### Requirements

- Python 3.12
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/)

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/job-extractor.git
cd job-extractor
python -m venv .venv
```

Activate the virtual environment:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

### Configuration

Copy `.env.example` to `.env` and add your API key:

```
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3.8-flash
```

The model name is configurable because Gemini model names change often. Never commit your `.env` file.

### Run the API

```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs to try the endpoints from the interactive documentation.

## Example

Request to `POST /extract-job`:

```json
{
  "text": "Empresa: TechNova SAS. Cargo: Desarrollador Backend Junior. Modalidad hibrida en Medellin. Requisitos: Python, FastAPI y bases de datos SQL. Deseable: conocimientos en Docker. Salario a convenir."
}
```

Response:

```json
{
  "title": "Desarrollador Backend Junior",
  "company": "TechNova SAS",
  "modality": "hybrid",
  "modality_source": "hibrida",
  "location": "Medellin",
  "salary": "Salario a convenir",
  "contract_type": null,
  "required_skills": [
    {
      "name": "Python",
      "source": "Python"
    },
    {
      "name": "FastAPI",
      "source": "FastAPI"
    },
    {
      "name": "bases de datos SQL",
      "source": "bases de datos SQL"
    }
  ],
  "nice_to_have_skills": [
    {
      "name": "Docker",
      "source": "Docker"
    }
  ]
}
```

## Running the tests

```bash
python -m pytest -v
```

The tests replace Gemini with a fake provider through FastAPI dependency overrides, so they need no API key, no internet connection and no API quota.

Note that these tests verify the application logic (validation, verification and error handling), not the quality of the AI output. Output quality is checked manually with real job postings.

## Design decisions

- **Provider interface**: the app depends on an `LLMProvider` abstraction, not on Gemini directly. Switching to another LLM means writing one new class.
- **Strict verification over convenience**: if the AI slightly reformats a value (for example, changes an accent or punctuation), the value is dropped. Losing a correct value is preferred over accepting an invented one.
- **Modality is a label, not a quote**: since `remote` / `hybrid` / `onsite` cannot be found literally in a Spanish posting, the model must also return `modality_source`, the exact phrase it relied on. No traceable phrase, no modality.
- **Generic error messages**: AI provider errors are logged on the server but never exposed to the client.

## Limitations

- Verification checks that a phrase **exists** in the posting, not that it **justifies** the value. A skill with a real but unrelated `source` would pass.
- Strict matching can drop valid values when the AI reformats them.
- Only plain text input is supported (no images or links yet).
- On the Gemini free tier, rate limits are low and Google may use the submitted data to improve its products. Do not send personal or confidential information.

## Roadmap

- Job posting input from images and links
- Automatic retries with exponential backoff for temporary AI errors (`503`)
- CI with GitHub Actions

This project is a building block of **TailorCV**, a tool that adapts a resume to a job posting without inventing experience.

## Development process

Built feature by feature with small branches, pull requests and tests. Developed with the help of an AI assistant: every piece of generated code was reviewed, tested and adjusted before being merged.

## Author

JOSE LUIS
- GitHub: [@Joselpp1](https://github.com/Joselpp1)
- LinkedIn: [JOSE LUIS](https://www.linkedin.com/in/jose-luis-palacio-perez)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
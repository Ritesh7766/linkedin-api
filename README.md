# LinkedIn API

[![Build](https://github.com/Ritesh7766/linkedin-api/actions/workflows/ci.yml/badge.svg)](https://github.com/Ritesh7766/linkedin-api/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A Python client and FastAPI service for extracting structured profile information from LinkedIn - profile summary, experience, education, skills, certifications, and projects - as clean JSON.

## What this is (and isn't)

LinkedIn does not expose a public profile API. If you open your browser's network tab on a profile page, you won't see anything resembling a normal REST response for "experience" or "education" - the actual data assembly happens on LinkedIn's own servers, which render it into a scrambled, minified React Server Components (RSC) payload and stream it down as effectively pre-built HTML-in-JSON, lazily loaded section by section as you scroll.

This project works by identifying which internal component endpoints LinkedIn's frontend itself calls to fetch each section, then reverse-engineering parsers for the resulting payloads. Those payloads are not meant to be read by anything other than LinkedIn's own React renderer - definitions keyed by opaque alphanumeric IDs, deeply cross-referenced (`$L4`, `$L19`, ...), a single response often bundling several unrelated sections together. Making sense of them by hand was rough enough that LLM assistance (Claude) was used throughout to help decipher the structure and write the regex-based parsers in this repo - full credit where it's due, and worth being upfront about given how much of the actual "reverse engineering" leaned on that.

**This is a first-version proof of concept**, not a stable integration:

- LinkedIn's frontend can (and does) change without notice. Since nothing here is a documented, versioned API, any restructuring of LinkedIn's RSC payloads, component names, or collection identifiers can silently break parsing at any time, with no deprecation warning.
- Parsing is done with pattern matching over the raw response text (regex-based extraction of RSC definitions and text fragments), not a real JSON/RSC parser - it works because the payloads happen to be consistent enough to pattern-match today, not because the format is documented or stable.
- Coverage is partial. Profile summary, experience, education, skills, certifications, and projects are implemented; other sections (languages, honors & awards, volunteering, recommendations, etc.) are not yet.
- This uses your own logged-in session cookies to make requests as you, from your own machine - not a public or officially sanctioned integration. Use responsibly and at your own risk with respect to LinkedIn's Terms of Service.

## How it works

```
LinkedIn (your session cookies)
   │
   ▼
Fetchers  →  request the specific internal RSC component LinkedIn's own
              frontend calls for a given section
   │
   ▼
Raw response  →  scrambled RSC payload (opaque definition IDs, cross-refs)
   │
   ▼
Parsers  →  resolve refs, extract text nodes, reconstruct structured fields
   │
   ▼
Pydantic models  →  typed, validated data
   │
   ▼
FastAPI  →  JSON over HTTP
```

## Installation

Requires Python 3.12+.

```bash
git clone https://github.com/Ritesh7766/linkedin-api.git
cd linkedin-api
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

For local development (linting, type-checking, pre-commit hooks):

```bash
pip install ".[dev]"
pre-commit install
```

### Docker

```bash
docker build -t linkedin-api .
docker run -d -p 8000:8000 --env-file .env --name linkedin-api linkedin-api
```

## Configuration

The service authenticates to LinkedIn using your own browser session cookies, read from environment variables (or a `.env` file in the project root):

```env
LINKEDIN_LI_AT=<your li_at cookie value>
LINKEDIN_JSESSIONID=<your JSESSIONID cookie value>
```

To get these values: log into LinkedIn in your browser, open DevTools → Application (or Storage) → Cookies → `https://www.linkedin.com`, and copy the `li_at` and `JSESSIONID` values. These are session credentials - treat them like a password, don't commit them, and expect to have to refresh them once your session expires.

## Running

```bash
uvicorn linkedin_api.app:app --reload
```

The API is now available at `http://localhost:8000`, with interactive docs at `http://localhost:8000/docs`.

## Usage

```bash
curl -X POST http://localhost:8000/profile \
  -H "Content-Type: application/json" \
  -d '{"vanity_name": "riteshsaha7766"}'
```

`vanity_name` is the part of a profile's URL after `/in/` - for `linkedin.com/in/riteshsaha7766`, that's `riteshsaha7766`.

### Example response

Live output from the endpoint above, run against my own profile:

```json
{
  "profile": {
    "profile_id": "ACoAADfM6r4BtEo0oubMLAYNAqjMe2xPi5NLGcs",
    "member_id": "936176318",
    "followers": 959,
    "activity_url": "https://www.linkedin.com/in/riteshsaha7766/recent-activity/all/",
    "about": "I’m a software developer with a strong interest in statistics and data science. I enjoy building efficient systems, optimizing performance, and solving complex problems."
  },
  "experience": [
    {
      "company": "ZURU Tech",
      "title": "Scientific Python Developer",
      "employment_type": "Full-time",
      "dates": "Feb 2024 - Present · 2 yrs 7 mos",
      "location": "Kolkata, West Bengal, India · On-site",
      "company_duration": null
    },
    {
      "company": "Fanztar",
      "title": "Software Engineer",
      "employment_type": "Full-time",
      "dates": "Sep 2023 - Feb 2024 · 6 mos",
      "location": "Gurugram, Haryana · Remote",
      "company_duration": null
    },
    {
      "company": "EnableCap",
      "title": "Jr. Software Engineer",
      "employment_type": "Full-time",
      "dates": "Jun 2022 - Jun 2023 · 1 yr 1 mo",
      "location": "Greater Kolkata Area · On-site",
      "company_duration": null
    }
  ],
  "education": [
    {
      "school": "Indian Institute of Technology, Madras",
      "degree": "BS Data Science & Applications",
      "field_of_study": null,
      "dates": "Mar 2026 – Mar 2029",
      "grade": "CGPA - 9.5 (upto 1st term)",
      "description": "Relevant coursework: Statistics, Linear Algebra, Multivariable calculus, Probability theory"
    },
    {
      "school": "MITx Courses",
      "degree": "MicroMasters® Program in Statistics and Data Science",
      "field_of_study": null,
      "dates": "Aug 2024 – Jan 2026",
      "grade": null,
      "description": null
    }
  ],
  "skills": [],
  "certifications": [
    {
      "name": "Improving Deep Neural Networks: Hyperparameter Tuning, Regularization and Optimization",
      "issuing_organization": "DeepLearning.AI",
      "issue_date": "Sep 2025",
      "credential_id": "U5Y5IHZYHQD6",
      "credential_url": "https://www.linkedin.com/company/18246783/"
    },
    {
      "name": "Fundamentals of Statistics",
      "issuing_organization": "MITx MicroMasters® Programs",
      "issue_date": "Aug 2025",
      "credential_id": "4bad1064db0140cb9edb938bd3db4698",
      "credential_url": "https://www.linkedin.com/company/69147703/"
    }
  ],
  "projects": [
    {
      "name": "pycar",
      "description": "pycar is a Python library for generating Content Addressable Archive (CARv1) files...",
      "url": "https://github.com/RiteshSaha8145/pycar"
    }
  ]
}
```

(Full `about` and project `description` text is untruncated in the actual response - shortened here for readability.)

## Roadmap

- [ ] Test coverage for parsers and fetchers
- [ ] Remaining sections: languages, honors & awards, volunteering, recommendations
- [ ] More resilient parsing (detect and surface upstream format changes rather than silently returning empty results)
- [ ] Async fetching to reduce total request time across sections

## Architecture

```
LinkedIn → Fetchers → Raw response → Parsers → Pydantic models → FastAPI
```

## License

MIT

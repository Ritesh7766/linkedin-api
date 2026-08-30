# LinkedIn API

[![Build](https://github.com/Ritesh7766/linkedin-api/actions/workflows/ci.yml/badge.svg)](https://github.com/Ritesh7766/linkedin-api/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A Python client and API for extracting structured profile information from LinkedIn.

## Purpose

This project provides a lightweight Python client for interacting with LinkedIn's web application endpoints and extracting profile information such as:

- Profile information
- About section
- Activity information
- Experience
- Education
- Skills
- Featured content

The project is designed around a clear separation between fetching and parsing:

```text
LinkedIn
   │
   ▼
Fetchers
   │
   ▼
Raw response
   │
   ▼
Parsers
   │
   ▼
Pydantic models
   │
   ▼
FastAPI

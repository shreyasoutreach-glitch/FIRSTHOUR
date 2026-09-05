# MOCK README: FIRST HOUR

## What is this?
**FIRST HOUR** is a financial incident reconstruction prototype built for the Razorpay AI Buildathon. It acts as an emergency response tool for merchants dealing with suspicious financial movements (e.g., potential fraud).

## What does it do?
When money moves under suspicious circumstances, the first hour is critical but often chaotic. FIRST HOUR solves this by providing a calm, traceable, and recovery-ready incident dashboard. 

Here is how it works:
1. **Evidence Ingestion:** It ingests various evidence such as text messages or communication logs.
2. **Deterministic Cross-Verification:** It uses an AI layer to interpret the unstructured evidence and extract claims, but then **deterministically cross-references** these claims against real financial records (payments, payouts, contacts, etc.).
3. **Graph and Timeline Construction:** It reconstructs a clear timeline of what happened, tracks entity links (beneficiaries, bank accounts), and maps out the blast radius (where else money might have gone).
4. **Human Attestation:** If the system cannot deduce a fact from data, it asks the merchant exactly one high-value question at a time to establish the truth.
5. **Recovery Packet:** It generates a comprehensive recovery packet ready to be handed over to a bank's fraud desk or the cybercrime portal.

## Core Philosophy
> **AI interprets. Deterministic systems establish financial truth. The graph connects facts. Humans resolve what machines cannot know.**

No financial fact (amount, time, beneficiary, or exposure) is ever hallucinated or guessed by an LLM. Everything is verified against concrete database records.

## Local Setup

### Prerequisites
- Python 3.11+, Node.js 20+, npm
- (Optional) Docker + Docker Compose
- (Optional) Postgres 14+ (Defaults to local SQLite)

### Installation
**Backend:**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env
```

### Running the App
1. **Seed Synthetic Data:** `python -m seed.seed` (inside backend)
2. **Start Backend:** `uvicorn app.main:app --reload --port 8000`
3. **Start Frontend:** `npm run dev` (inside frontend, opens at `http://localhost:5173`)

## Architecture at a glance
- **Frontend:** React (Welcome, Evidence Drop, Reconstruction, Incident Dashboard, Graph)
- **Backend:** FastAPI (Evidence Pipeline, Financial Baseline, Incident Scoring, Graph Builder, Exposure Engine)
- **Database:** SQLite (default) or Postgres

*This is a read-only system. It never initiates real financial transactions, freezes, or refunds. All data provided in the demo is synthetically seeded.*

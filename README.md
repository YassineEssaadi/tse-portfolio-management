# 📈 Equity Portfolio Management — Tunis Stock Exchange
### FIN 350 Financial Markets Project | Real-Capital Top-Down Investment Strategy

[![Python](https://img.shields.io/badge/Analysis-Python%20%7C%20Excel-3776AB?style=flat-square&logo=python)](https://www.python.org/)
[![Finance](https://img.shields.io/badge/Domain-Portfolio%20Management-brightgreen?style=flat-square)](https://en.wikipedia.org/wiki/Portfolio_management)
[![CAPM](https://img.shields.io/badge/Model-CAPM%20%7C%20Markowitz-blue?style=flat-square)](https://en.wikipedia.org/wiki/Capital_asset_pricing_model)
[![TSE](https://img.shields.io/badge/Market-Tunis%20Stock%20Exchange-orange?style=flat-square)](https://www.bvmt.com.tn/)
[![Academic](https://img.shields.io/badge/Institution-Tunis%20Business%20School-red?style=flat-square)](https://tunis-business-school.tn/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

> **Course:** FIN 350 — Financial Markets | **Institution:** Tunis Business School | **Year:** 2025–2026

---

## 📋 Table of Contents

- [Overview](#overview)
- [Investment Process](#investment-process)
- [Macroeconomic Analysis](#macroeconomic-analysis)
- [Stock Selection](#stock-selection)
- [Portfolio Construction](#portfolio-construction)
- [Technical Analysis](#technical-analysis)
- [Performance Evaluation](#performance-evaluation)
- [Repository Contents](#repository-contents)
- [Getting Started](#getting-started)
- [Authors](#authors)

---

## 📌 Overview

This project documents the management of a **real-capital equity portfolio** on the **Tunis Stock Exchange (TSE/BVMT)** over a **3-month investment horizon**, carried out by a **team of three** within the supervised academic framework of FIN 350 at Tunis Business School.

Orders were placed on a live brokerage account opened with **Tunisie Valeurs**. No simulated or paper trading was involved: the capital, the market prices and the executions were real. The exercise was academic in its *setting* — a course requirement, a graded report and faculty supervision — not in its *nature*.

**Key Highlights:**
- Broker: Tunisie Valeurs (negotiated fee: 0.2% vs. standard 0.6%)
- Capital: 406,912 TND (invested: 373,620 TND)
- Team: 3 students — sector/fundamental/technical analysis, portfolio optimisation and order execution were split across members (see [Authors](#authors))
- Universe: 80 TUNINDEX-listed stocks → screened to 20 → final portfolio of 10
- Objective: Maximise risk-adjusted returns over 3 months

> **Scope note:** CAPM estimation and Markowitz optimisation were handled by one team member, and order execution with the broker by another. The repository owner's contribution is detailed in the [Authors](#authors) table.

---

## 🔄 Investment Process

```
Step 1 & 2  ->  Broker Selection & Account Setup
Step 3      ->  Macroeconomic & Sector Analysis
Step 4      ->  Adjusted Return Calculations (10-year historical data)
Step 5      ->  Shortlisting: 80 -> 20 -> 10 stocks
Step 6      ->  CAPM & Markowitz Portfolio Optimization
Step 7      ->  Market Entry Strategy & Order Execution
Step 8      ->  Portfolio Rebalancing Decisions
Step 9      ->  Performance Evaluation & Return Calculations
```

---

## 🌍 Macroeconomic Analysis

| Indicator | Value | Implication |
|---|---|---|
| Real GDP Growth (Q2 2025) | +3.16% YoY | Broad but nascent recovery |
| Investment-to-GDP Ratio | 7.9% (2024) | Critical low — capital erosion |
| Agricultural Growth | +9.84% YoY | Strongest sector |
| Inflation (CPI) | ~5.5% (2025) | Moderating but elevated |

---

## 📊 The Final 10-Stock Portfolio

| # | Company | Sector | Market Cap (TND) | Selection Rationale |
|---|---|---|---|---|
| 1 | **ONE TECH HOLDING** | Industrials | 715.6M | Highest conviction: liquidity + fundamentals + export |
| 2 | **POULINA GROUP HOLDING** | Consumer Goods | 2,650M | Portfolio cornerstone: defensive + massive scale |
| 3 | **BANQUE ATTIJARI DE TUNISIE** | Banking | 2,610M | Optimal risk-return in banking sector |
| 4 | **UNIMED** | Healthcare | 262.4M | Defensive leader + strong uptrend |
| 5 | **CARTHAGE CEMENT** | Construction | 650.1M | Highest liquidity anchor in portfolio |
| 6 | **TAWASOL GROUP HOLDING** | Telecom | 64.8M | Breakout from long-term consolidation |
| 7 | **SMART TUNISIE** | Distribution | 173M | Clean breakout retest + trend continuation |
| 8 | **EURO-CYCLES** | Consumer Goods | 129M | Descending wedge breakout on high volume |
| 9 | **MAGHREBIA VIE** | Insurance | 197.5M | Coiling pattern near highs → imminent breakout |
| 10 | **ESSOUKNA** | Construction | 11.9M | Multi-year base breakout — high-reward cyclical |

---

## 📐 Portfolio Construction

### CAPM Formula

```
E(Ri) = Rf + Beta_i x [E(Rm) - Rf]
```

### Markowitz Optimization Example

Each stock's price history and return series live in its own workbook under `10 STOCKS MARKOWITZ/`. The optimisation itself was run on the assembled return matrix:

```python
from pypfopt import EfficientFrontier, risk_models, expected_returns
import pandas as pd

# Assemble the daily return series from the per-stock workbooks
prices = pd.read_excel('10 STOCKS MARKOWITZ/One Tech Holding.xlsx')
mu = expected_returns.mean_historical_return(prices)
S = risk_models.sample_cov(prices)
ef = EfficientFrontier(mu, S)
weights = ef.max_sharpe()
print(ef.clean_weights())
```

> The full CAPM + Markowitz workbook is [`CAPM and Markovitz.xlsx`](CAPM%20and%20Markovitz.xlsx).

---

## 📉 Technical Analysis

Each of the 10 selected stocks was analyzed using:
- **Trend analysis** (moving averages, support/resistance levels)
- **Chart patterns** (breakouts, wedges, consolidation bases)
- **Volume confirmation** for entry signals
- **Entry price targets** and stop-loss levels

---

## 📀 Performance Evaluation

Portfolio performance was assessed over the 3-month horizon using:
- **Absolute return** vs. benchmark (TUNINDEX)
- **Risk-adjusted metrics** (Sharpe ratio)
- **Rebalancing decisions** based on price action and fundamentals

---

## 📁 Repository Contents

```
tse-portfolio-management/
|
|-- README.md
|-- LICENSE
|-- requirements.txt
|-- .gitignore
|-- 10 STOCKS MARKOWITZ/                     # Per-stock scripts + workbooks (CAPM, scoring, signals)
|   |-- One Tech Holding.py / .xlsx
|   |-- POULINA GH.py / .xlsx
|   |-- Attijari Bank.xlsx
|   |-- ... (one pair per selected stock)
|-- Technical Analysis/                      # Price & indicator workbooks (~73 listed stocks)
|-- Stocks Daily Returns/                    # Daily return series per listed stock (~81 files)
|-- Portfolio Dashboarding/
|   |-- portfolio_dashboard.py               # Interactive performance dashboard
|-- CAPM and Markovitz.xlsx                  # CAPM + Markowitz optimisation workbook
|-- Company Ranking By Sector.xlsx           # Sector-based stock ranking
|-- Fundamental Analysis and Scoring System.xlsx  # Fundamental scoring model
|-- Macroeconomic Analysis.xlsx              # Macro indicators & sector analysis
|-- Portfolio Return Track.xlsx              # Portfolio performance tracking
|-- report/
|   |-- Group 22 Fin 350 Report.pdf          # Full academic report (PDF)
|   |-- Group 22 Fin 350 Report.docx         # Editable version
|-- demos/
    |-- README.md                            # Video demo index (Google Drive links)
```

> **Note:** This repository contains the academic report, Python scripts, Excel models and market data. The full methodology, stock analysis and results are documented in the report.
>
> Broker confirmations, account statements and personal identifiers are **not** published in this repository.

---

## ⚙️ Getting Started

```bash
git clone https://github.com/YassineEssaadi/tse-portfolio-management.git
cd tse-portfolio-management
pip install -r requirements.txt
```

Each analysis script reads the workbook sitting next to it, so run it from inside its own folder. Folder and file names contain spaces — quote them in the shell:

```bash
cd "10 STOCKS MARKOWITZ" && python "One Tech Holding.py"
```

---

## 👥 Authors

Team of three — equal academic credit, distinct workstreams.

| Name | Contribution |
|---|---|
| **Yassine Essaadi** | Sector analysis, fundamental scoring, technical analysis / entry timing (80-stock screening → shortlist) |
| **Amine Bessaad** | Macroeconomic analysis, CAPM, Markowitz portfolio optimization |
| **Mohamed Adnen Guirat** | Stock selection, order execution with the broker, performance evaluation |

**Institution:** Tunis Business School
**Course:** FIN 350 — Financial Markets
**Academic Supervisor:** Dr. Eymen Errais
**Professional Supervisor:** Mr. Ramzi Jerbi
**Academic Year:** 2025–2026

---

**Remark:** The portfolio was funded with real capital. Trading was carried out within a supervised academic framework, for educational purposes, and does not constitute investment advice.

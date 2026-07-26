# 📈 Equity Portfolio Management — Tunis Stock Exchange
### FIN 350 Financial Markets Project | Top-Down Investment Strategy

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
- [Authors](#authors)

---

## 📌 Overview

This project documents the complete experience of a **junior equity trader** constructing and managing a real portfolio on the **Tunis Stock Exchange (TSE/BVMT)** over a **3-month investment horizon**.

**Key Highlights:**
- Broker: Tunisie Valeurs (negotiated fee: 0.2% vs. standard 0.6%)
- Capital: 406,912 TND (invested: 373,620 TND)
- Universe: 80 TUNINDEX-listed stocks → screened to 20 → final portfolio of 10
- Objective: Maximize risk-adjusted returns over 3 months

---

## 🔄 Investment Process

```
Step 1 & 2  ->  Broker Selection & Account Setup
Step 3      ->  MacROeconomic & Sector Analysis
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

```python
from pypfopt import EfficientFrontier, risk_models, expected_returns
import pandas as pd

prices = pd.read_excel('data/Stocks Daily Returns.xlsx', index_col=0)
mu = expected_returns.mean_historical_return(prices)
S = risk_models.sample_cov(prices)
ef = EfficientFrontier(mu, S)
weights = ef.max_sharpe()
print(ef.clean_weights())
```

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
|-- 10 STOCKS MARKOWITZ/                     # 10 stocks selected for the portfolio along with the python scripts to analyze them
|-- Company Ranking By Sector.xlsx           # Sector-based stock ranking
|-- Fundamental Analysis and Scoring System.xlsx  # Fundamental scoring model
|-- Macroeconomic Analysis.xlsx              # Macro indicators & sector analysis
|-- Portfolio Return Track.xlsx              # Portfolio performance tracking
|-- technical-analysis/                      # technical analysis on the Tunisian market's stocks
|-- markowitz-analysis/                      # Markowitz optimization models
|-- stocks-daily-returns/                    # Daily returns data & calculations
|-- Potfolio Dashboarding/                   # Portfolio dashboard scripts
|-- report/
|   |-- fin350_project_report.pdf            # Full academic report (PDF)
|   |-- README.md                            # Report directory index
|-- demos/
    |-- README.md                            # Video demo index with Google Drive links
```

> **Note:** This repository contains the academic report PDF, Python scripts, Excel models, and data files. The full methodology, stock analysis, and results are documented in the report.

---

## 👥 Authors

| Name | Contribution |
|---|---|
| **Amine Bessaad** | Macroeconomic analysis, CAPM, portfolio optimization |
| **Yassine Essaadi** | Sector analysis, fundamental scoring, technical analysis |
| **Mohamed Adnen Guirat** | Stock selection, order execution, performance evaluation |

**Institution:** Tunis Business School
**Course:** FIN 350 — Financial Markets
**Academic Supervisor:** Dr. Eymen Erraies
**Professional Supervisor:** Mr. Ramzi Jerbi
**Academic Year:** 2025–2026

---

**Disclaimer:** All trading was conducted with real capital for academic purposes.

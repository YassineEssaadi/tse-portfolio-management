## 🎬 Video Demos

This directory contains demonstration videos showcasing key components of the FIN 350 Portfolio Management project. The videos illustrate the analytical tools and interactive dashboard developed throughout the trading simulation on the Tunis Stock Exchange (BVMT).

---

### Video 1 — Stock Analysis with Python

**File:** `demos/stock_analysis_demo.mp4`

This demo walks through the individual stock analysis pipeline built in Python. Each of the 10 selected stocks has its own dedicated Python script that performs:
- Historical price retrieval and cleaning
- Return computation and volatility estimation
- CAPM beta calculation and expected return (via SML)
- Fundamental scoring based on financial ratios
- Technical analysis signals (RSI, moving averages, Bollinger Bands)

The video shows the script execution for a representative stock, illustrating how the quantitative scoring model was applied consistently across all securities.

> 📁 *File not yet rendered by GitHub — see upload instructions below.*

---

### Video 2 — Portfolio Dashboard

**File:** `demos/portfolio_dashboard_demo.mp4`

This demo showcases the interactive portfolio performance dashboard built to monitor and evaluate the simulated equity portfolio over the full trading period. Features demonstrated include:
- Cumulative return tracking vs. BVMT benchmark
- Portfolio weight visualization (pie chart, bar chart)
- Risk metrics display: Sharpe ratio, portfolio beta, standard deviation
- Individual stock contribution to overall performance
- Rebalancing events and trade log

The dashboard was designed to replicate a professional portfolio management reporting tool adapted to the Tunisian market context.

> 📁 *File not yet rendered by GitHub — see upload instructions below.*

---

### ⚠️ Note on File Size

Both video files are large (> 100 MB) and **cannot be pushed via standard `git push`**. They were uploaded manually using one of the following methods:

- **Git LFS (recommended for files > 100 MB):**
  ```bash
  git lfs install
  git lfs track "*.mp4"
  git add .gitattributes
  git add demos/stock_analysis_demo.mp4
  git add demos/portfolio_dashboard_demo.mp4
  git commit -m "media: add video demos via Git LFS"
  git push
  ```

- **GitHub Web Upload (for files up to 25 MB):**
  Navigate to the `demos/` folder on GitHub → **Add file** → **Upload files**.

- **GitHub Releases (alternative for large files):**
  Upload the `.mp4` files as release assets under a tagged release (e.g., `v1.0`) — no size limit applies.

---

*For questions about the project methodology or results, refer to the main [README.md](../README.md) or the full project report in [`report/`](../report/).*

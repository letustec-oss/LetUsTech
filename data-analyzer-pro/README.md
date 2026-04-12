# Data Analyzer Pro

Advanced CSV data analysis desktop app with AI-powered insights, built with Electron.

## Features

- **Drag & drop** CSV loading with instant parsing
- **Overview** — completeness score, column types, automated insights
- **Statistics** — mean, median, std dev, Q1/Q3, IQR for all numeric columns
- **Charts** — bar, line, scatter, pie, histogram, category frequency
- **Correlation matrix** — Pearson correlation heatmap across all numeric columns
- **Data quality** — missing %, unique counts, zero counts, status flags
- **AI Insights** — powered by Claude (requires Anthropic API key)
- **Export** — one-click HTML report generation

## Quick Start

```bash
# Install dependencies
npm install

# Run in development
npm start

# Build distributable for your platform
npm run build:win    # Windows .exe installer
npm run build:mac    # macOS .dmg
npm run build:linux  # Linux AppImage
```

## AI Setup

1. Get an API key from [console.anthropic.com](https://console.anthropic.com)
2. Open the app → click **Settings** (top right)
3. Paste your `sk-ant-...` key and save
4. The AI Insights tab is now active

Your API key is stored locally in your OS user data folder — never sent anywhere except directly to Anthropic's API.

## Built by

[LetUsTech](https://letustech.uk) · Deano

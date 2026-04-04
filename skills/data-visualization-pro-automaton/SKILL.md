---
name: data-visualization-pro
description: AI-powered data visualization tool with 6 chart types (bar, line, pie, scatter, heatmap, radar), CSV/JSON import, AI-driven chart recommendations, interactive dashboards, and export to PNG/SVG/PDF. Use when creating charts, visualizing datasets, generating reports, or building data dashboards. Triggers on "chart", "graph", "visualize data", "plot", "dashboard", "data viz".
---

# Data Visualization Pro

AI-powered data visualization with smart chart recommendations.

## Features

- **6 Chart Types**: Bar, Line, Pie, Scatter, Heatmap, Radar
- **AI Chart Recommendations**: Analyzes your data and suggests the best chart type
- **CSV/JSON Import**: Drop in your data file and visualize instantly
- **Interactive Dashboards**: Combine multiple charts into a single view
- **Export**: PNG, SVG, PDF — publication-ready output
- **Responsive**: Works on desktop and mobile

## Quick Start

### 1. Visualize a CSV file

```
Visualize this data: [paste CSV or provide file path]
```

The agent will:
1. Parse the data (CSV, JSON, or raw text)
2. Analyze column types (numeric, categorical, temporal)
3. Recommend the best chart type
4. Generate an interactive visualization

### 2. Create a specific chart

```
Create a bar chart comparing Q1-Q4 revenue for 2024 and 2025
```

### 3. Build a dashboard

```
Build a dashboard from sales-data.csv with:
- Revenue trend (line chart)
- Regional breakdown (pie chart)
- Product comparison (bar chart)
```

## Chart Selection Guide

| Data Pattern | Recommended Chart | When to Use |
|-------------|-------------------|-------------|
| Trends over time | Line | Time-series, stock prices, growth |
| Category comparison | Bar | Revenue by region, product sales |
| Part-of-whole | Pie | Market share, budget allocation |
| Correlation | Scatter | Height vs weight, price vs demand |
| Multi-variable | Radar | Product comparison, skill assessment |
| Density/matrix | Heatmap | Correlation matrix, geographic data |

## AI Recommendation Engine

The AI analyzes your data to recommend the optimal visualization:

1. **Column type detection**: Numeric, categorical, temporal, boolean
2. **Relationship analysis**: Correlation strength, distribution shape
3. **Data volume assessment**: Row count determines complexity level
4. **Pattern recognition**: Trends, clusters, outliers, proportions

## Sample Datasets Included

- `sample-data.csv` — Mixed business metrics
- `sample-categories.csv` — Category comparison data
- `sample-correlation.csv` — Multi-variable correlation data
- `sample-proportions.csv` — Part-of-whole data

## Technical Stack

- **Frontend**: React + TypeScript + Vite
- **Charts**: Recharts (built on D3.js)
- **Styling**: Tailwind CSS
- **Export**: html2canvas + jsPDF
- **Build**: 382KB production build

## Web App

Try the live demo: https://courageous-bonbon-d1af15.netlify.app

## Usage Tips

- For large datasets (>10K rows), use aggregation before visualizing
- AI recommendations work best with 3-20 columns
- Export at 2x resolution for print-quality output
- Use the dashboard view to tell a complete data story

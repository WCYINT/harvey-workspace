---
name: ga4-analytics-nexus
description: "Google Analytics 4, Search Console, and Indexing API toolkit with multi-property support. Analyze website traffic, page performance, user demographics, real-time visitors, search queries, and SEO metrics across multiple properties. Use when the user asks to: check site traffic for any property, analyze page views across multiple sites, see traffic sources, view user demographics, get real-time visitor data, check search console queries for any site, analyze SEO performance, request URL re-indexing, inspect index status, compare date ranges, check bounce rates, view conversion data, or get e-commerce revenue. Requires a Google Cloud service account with access to GA4 and Search Console properties."
---

# GA4 Analytics Toolkit (Nexus Edition)

Multi-property version supporting dynamic discovery of GA4 properties and Search Console sites.

## Setup

Install dependencies:

```bash
cd scripts && npm install
```

Configure credentials by setting the environment variable:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

Optional configuration:
```
GA4_DEFAULT_DATE_RANGE=30d
```

**Prerequisites**: 
- A Google Cloud project with the Analytics Data API, Analytics Admin API, Search Console API, and Indexing API enabled
- A service account with access to your GA4 properties and Search Console sites
- Service account must be added as Viewer to GA4 properties and have access to Search Console sites

## Quick Start

First, discover available properties:

```typescript
import { listGa4Properties, listSearchConsoleSites, siteOverview } from './scripts/src/index.js';

// List all accessible GA4 properties
const properties = await listGa4Properties();
console.log(properties);
// [{ propertyId: '123456789', displayName: 'My Site', accountId: '...' }, ...]

// List all accessible Search Console sites
const sites = await listSearchConsoleSites();
console.log(sites);
// [{ siteUrl: 'https://example.com', permissionLevel: 'siteFullUser' }, ...]

// Get overview for a specific property
const overview = await siteOverview('123456789', '30d');
```

## Quick Reference

| User says | Function to call |
|-----------|-----------------|
| "Show me my GA4 properties" | `listGa4Properties()` |
| "Show me my Search Console sites" | `listSearchConsoleSites()` |
| "Show me site traffic for property 123456789" | `siteOverview('123456789', '30d')` |
| "What are my top search queries for example.com?" | `searchConsoleOverview('https://example.com', '30d')` |
| "Who's on property 123456789 right now?" | `liveSnapshot('123456789')` |
| "Reindex these URLs" | `reindexUrls(["https://example.com/page1", ...])` |
| "Compare this month vs last month for property 123" | `compareDateRanges('123', {startDate: "30daysAgo", endDate: "today"}, {startDate: "60daysAgo", endDate: "31daysAgo"})` |
| "What pages get the most traffic on property 123?" | `contentPerformance('123', '30d')` |

Execute functions by importing from `scripts/src/index.ts`:

```typescript
import { 
  listGa4Properties, 
  listSearchConsoleSites,
  siteOverview, 
  searchConsoleOverview 
} from './scripts/src/index.js';

// List properties first
const properties = await listGa4Properties();

// Then query specific property
const overview = await siteOverview(properties[0].propertyId, '30d');
```

Or run directly with tsx:

```bash
npx tsx scripts/src/index.ts
```

## Workflow Pattern

Every analysis follows three phases:

### 1. Discover
List available GA4 properties and Search Console sites to identify targets.

### 2. Analyze
Run API functions with specific property IDs and site URLs. Each call hits the Google APIs and returns structured data.

### 3. Auto-Save
All results automatically save as timestamped JSON files to `results/{category}/`. File naming pattern: `YYYYMMDD_HHMMSS__operation__extra_info.json`

### 4. Summarize
After analysis, read the saved JSON files and create a markdown summary in `results/summaries/` with data tables, trends, and recommendations.

## Discovery Functions

### GA4 Property Discovery

```typescript
const properties = await listGa4Properties();
// Returns: [{ propertyId: '123456789', displayName: 'My Site', accountId: '...' }, ...]
```

### Search Console Site Discovery

```typescript
const sites = await listSearchConsoleSites();
// Returns: [{ siteUrl: 'sc-domain:example.com', permissionLevel: 'siteFullUser' }, ...]
```

## High-Level Functions

### GA4 Analytics

| Function | Purpose | Parameters |
|----------|---------|------------|
| `siteOverview(propertyId, dateRange?)` | Comprehensive site snapshot | `propertyId`: string, `dateRange`: optional |
| `trafficAnalysis(propertyId, dateRange?)` | Traffic deep-dive | `propertyId`: string, `dateRange`: optional |
| `contentPerformance(propertyId, dateRange?)` | Top pages analysis | `propertyId`: string, `dateRange`: optional |
| `userBehavior(propertyId, dateRange?)` | Engagement patterns | `propertyId`: string, `dateRange`: optional |
| `compareDateRanges(propertyId, range1, range2)` | Period comparison | `propertyId`: string, ranges: DateRange objects |
| `liveSnapshot(propertyId)` | Real-time data | `propertyId`: string |

### Search Console

| Function | Purpose | Parameters |
|----------|---------|------------|
| `searchConsoleOverview(siteUrl, dateRange?)` | SEO snapshot | `siteUrl`: string (e.g., "https://example.com" or "sc-domain:example.com"), `dateRange`: optional |
| `keywordAnalysis(siteUrl, dateRange?)` | Keyword deep-dive | `siteUrl`: string, `dateRange`: optional |
| `seoPagePerformance(siteUrl, dateRange?)` | Page SEO metrics | `siteUrl`: string, `dateRange`: optional |

### Indexing

| Function | Purpose | Parameters |
|----------|---------|------------|
| `reindexUrls(urls)` | Request re-indexing | `urls`: string[] |
| `checkIndexStatus(siteUrl, urls)` | Check if URLs are indexed | `siteUrl`: string, `urls`: string[] |

### Utility

| Function | Purpose | Parameters |
|----------|---------|------------|
| `getAvailableFields(propertyId)` | List all available GA4 dimensions and metrics | `propertyId`: string |

### Individual API Functions

For granular control, import specific functions from the API modules:

```typescript
import { runReport, getPageViews, getTopQueries } from './scripts/src/index.js';

// Run custom report for specific property
const report = await runReport({
  propertyId: '123456789',
  dimensions: ['pagePath'],
  metrics: ['screenPageViews'],
  dateRange: '7d'
});

// Get Search Console data for specific site
const queries = await getTopQueries('https://example.com', '30d');
```

## Date Ranges

All functions accept flexible date range formats:

| Format | Example | Description |
|--------|---------|-------------|
| Shorthand | `"7d"`, `"30d"`, `"90d"` | Days ago to today |
| Explicit | `{startDate: "2024-01-01", endDate: "2024-01-31"}` | Specific dates |
| GA4 relative | `{startDate: "30daysAgo", endDate: "today"}` | GA4 relative format |

Default is `"30d"` (configurable via `GA4_DEFAULT_DATE_RANGE` env var).

## Results Storage

Results auto-save to `results/` with this structure:

```
results/
├── reports/          # GA4 standard reports
├── realtime/         # Real-time snapshots
├── searchconsole/    # Search Console data
├── indexing/         # Indexing API results
└── summaries/        # Human-readable markdown summaries
```

### Managing Results

```typescript
import { listResults, loadResult, getLatestResult } from './scripts/src/index.js';

// List recent results
const files = listResults('reports', 10);

// Load a specific result
const data = loadResult(files[0]);

// Get most recent result for an operation
const latest = getLatestResult('reports', 'site_overview');
```

## Common Dimensions and Metrics

### Dimensions
`pagePath`, `pageTitle`, `sessionSource`, `sessionMedium`, `country`, `deviceCategory`, `browser`, `date`, `eventName`, `landingPage`, `newVsReturning`

### Metrics
`screenPageViews`, `activeUsers`, `sessions`, `newUsers`, `bounceRate`, `averageSessionDuration`, `engagementRate`, `conversions`, `totalRevenue`, `eventCount`

## Tips

1. **Discover first** — Always start with `listGa4Properties()` and `listSearchConsoleSites()` to see what's available
2. **Multi-property** — This toolkit supports analyzing multiple GA4 properties and Search Console sites without reconfiguration
3. **Specify date ranges** — "last 7 days" or "last 90 days" gives different insights than the default 30 days
4. **Request summaries** — After pulling data, ask for a markdown summary with tables and insights
5. **Compare periods** — Use `compareDateRanges()` to spot trends (this month vs last month)
6. **Check real-time data** — `liveSnapshot()` shows who's on the site right now
7. **Combine GA4 + Search Console** — Traffic data plus search query data gives the full picture

/**
 * GA4 Analytics Toolkit (Nexus Edition) - Main Entry Point
 * 
 * Multi-property version supporting GOOGLE_APPLICATION_CREDENTIALS.
 * All results are automatically saved to the /results directory with timestamps.
 *
 * Usage:
 *   import { listGa4Properties, siteOverview } from './index.js';
 *   const properties = await listGa4Properties();
 *   const overview = await siteOverview(properties[0].propertyId, '30d');
 */

// Re-export all API functions
export * from './api/reports.js';
export * from './api/realtime.js';
export * from './api/metadata.js';
export * from './api/searchConsole.js';
export * from './api/indexing.js';
export * from './api/bulk-lookup.js';

// Re-export core utilities (multi-property versions)
export { 
  getClient, 
  getAdminClient,
  formatPropertyId, 
  getSearchConsoleClient, 
  getIndexingClient, 
  listGa4Properties,
  listSearchConsoleSites,
  resetClient 
} from './core/client.js';
export { saveResult, loadResult, listResults, getLatestResult } from './core/storage.js';
export { getSettings, validateSettings } from './config/settings.js';

// Import for orchestration functions
import {
  runReport,
  getPageViews,
  getTrafficSources,
  getUserDemographics,
  getEventCounts,
  getConversions,
  parseDateRange,
  type DateRange,
} from './api/reports.js';
import { getActiveUsers, getRealtimeEvents, getRealtimePages } from './api/realtime.js';
import { getPropertyMetadata } from './api/metadata.js';
import { saveResult } from './core/storage.js';
import {
  getTopQueries,
  getTopPages as getSearchConsoleTopPages,
  getDevicePerformance,
  getCountryPerformance,
  type SearchConsoleDateRange,
} from './api/searchConsole.js';
import { requestIndexing, inspectUrl, type UrlInspectionOptions } from './api/indexing.js';

// ============================================================================
// HIGH-LEVEL ORCHESTRATION FUNCTIONS
// ============================================================================

/**
 * Comprehensive site overview - combines multiple reports
 * @param propertyId - GA4 Property ID (numeric)
 * @param dateRange - Optional date range
 */
export async function siteOverview(propertyId: string, dateRange?: string | DateRange) {
  console.log('\n📊 Generating site overview...');
  const results: Record<string, unknown> = {};

  console.log('  → Getting page views...');
  results.pageViews = await getPageViews(propertyId, dateRange);

  console.log('  → Getting traffic sources...');
  results.trafficSources = await getTrafficSources(propertyId, dateRange);

  console.log('  → Getting user demographics...');
  results.demographics = await getUserDemographics(propertyId, dateRange);

  console.log('  → Getting event counts...');
  results.events = await getEventCounts(propertyId, dateRange);

  // Save combined results
  const dateStr = typeof dateRange === 'string' ? dateRange : 'custom';
  saveResult(results, 'reports', 'site_overview', dateStr);

  console.log('✅ Site overview complete\n');
  return results;
}

/**
 * Deep dive on traffic sources
 * @param propertyId - GA4 Property ID (numeric)
 * @param dateRange - Optional date range
 */
export async function trafficAnalysis(propertyId: string, dateRange?: string | DateRange) {
  console.log('\n🚗 Analyzing traffic sources...');
  const results: Record<string, unknown> = {};

  console.log('  → Getting traffic sources...');
  results.sources = await getTrafficSources(propertyId, dateRange);

  console.log('  → Getting session data by source...');
  results.sessions = await runReport({
    propertyId,
    dimensions: ['sessionSource', 'sessionMedium'],
    metrics: ['sessions', 'engagedSessions', 'averageSessionDuration', 'bounceRate'],
    dateRange,
  });

  console.log('  → Getting new vs returning users...');
  results.newVsReturning = await runReport({
    propertyId,
    dimensions: ['newVsReturning'],
    metrics: ['activeUsers', 'sessions', 'conversions'],
    dateRange,
  });

  const dateStr = typeof dateRange === 'string' ? dateRange : 'custom';
  saveResult(results, 'reports', 'traffic_analysis', dateStr);

  console.log('✅ Traffic analysis complete\n');
  return results;
}

/**
 * Content performance analysis
 * @param propertyId - GA4 Property ID (numeric)
 * @param dateRange - Optional date range
 */
export async function contentPerformance(propertyId: string, dateRange?: string | DateRange) {
  console.log('\n📄 Analyzing content performance...');
  const results: Record<string, unknown> = {};

  console.log('  → Getting page views...');
  results.pages = await getPageViews(propertyId, dateRange);

  console.log('  → Getting landing pages...');
  results.landingPages = await runReport({
    propertyId,
    dimensions: ['landingPage'],
    metrics: ['sessions', 'activeUsers', 'bounceRate', 'averageSessionDuration'],
    dateRange,
  });

  console.log('  → Getting exit pages...');
  results.exitPages = await runReport({
    propertyId,
    dimensions: ['pagePath'],
    metrics: ['exits', 'screenPageViews'],
    dateRange,
  });

  const dateStr = typeof dateRange === 'string' ? dateRange : 'custom';
  saveResult(results, 'reports', 'content_performance', dateStr);

  console.log('✅ Content performance analysis complete\n');
  return results;
}

/**
 * User behavior analysis
 * @param propertyId - GA4 Property ID (numeric)
 * @param dateRange - Optional date range
 */
export async function userBehavior(propertyId: string, dateRange?: string | DateRange) {
  console.log('\n👤 Analyzing user behavior...');
  const results: Record<string, unknown> = {};

  console.log('  → Getting demographics...');
  results.demographics = await getUserDemographics(propertyId, dateRange);

  console.log('  → Getting events...');
  results.events = await getEventCounts(propertyId, dateRange);

  console.log('  → Getting engagement metrics...');
  results.engagement = await runReport({
    propertyId,
    dimensions: ['date'],
    metrics: ['activeUsers', 'engagedSessions', 'engagementRate', 'averageSessionDuration'],
    dateRange,
  });

  const dateStr = typeof dateRange === 'string' ? dateRange : 'custom';
  saveResult(results, 'reports', 'user_behavior', dateStr);

  console.log('✅ User behavior analysis complete\n');
  return results;
}

/**
 * Compare two date ranges
 * @param propertyId - GA4 Property ID (numeric)
 * @param range1 - First date range
 * @param range2 - Second date range
 * @param dimensions - Dimensions to include
 * @param metrics - Metrics to include
 */
export async function compareDateRanges(
  propertyId: string,
  range1: DateRange,
  range2: DateRange,
  dimensions: string[] = ['date'],
  metrics: string[] = ['activeUsers', 'sessions', 'screenPageViews']
) {
  console.log('\n📈 Comparing date ranges...');

  console.log(`  → Getting data for ${range1.startDate} to ${range1.endDate}...`);
  const period1 = await runReport({
    propertyId,
    dimensions,
    metrics,
    dateRange: range1,
    save: false,
  });

  console.log(`  → Getting data for ${range2.startDate} to ${range2.endDate}...`);
  const period2 = await runReport({
    propertyId,
    dimensions,
    metrics,
    dateRange: range2,
    save: false,
  });

  const comparison = {
    period1: { dateRange: range1, data: period1 },
    period2: { dateRange: range2, data: period2 },
  };

  saveResult(comparison, 'reports', 'date_comparison');

  console.log('✅ Date range comparison complete\n');
  return comparison;
}

/**
 * Get current live data snapshot
 * @param propertyId - GA4 Property ID (numeric)
 */
export async function liveSnapshot(propertyId: string) {
  console.log('\n⚡ Getting live data snapshot...');
  const results: Record<string, unknown> = {};

  console.log('  → Getting active users...');
  results.activeUsers = await getActiveUsers(propertyId);

  console.log('  → Getting current pages...');
  results.currentPages = await getRealtimePages(propertyId);

  console.log('  → Getting current events...');
  results.currentEvents = await getRealtimeEvents(propertyId);

  saveResult(results, 'realtime', 'snapshot');

  console.log('✅ Live snapshot complete\n');
  return results;
}

// ============================================================================
// SEARCH CONSOLE ORCHESTRATION FUNCTIONS
// ============================================================================

/**
 * Comprehensive Search Console overview
 * @param siteUrl - Search Console site URL (e.g., "https://example.com" or "sc-domain:example.com")
 * @param dateRange - Optional date range
 */
export async function searchConsoleOverview(siteUrl: string, dateRange?: string | SearchConsoleDateRange) {
  console.log('\n🔍 Generating Search Console overview...');
  const results: Record<string, unknown> = {};

  console.log('  → Getting top queries...');
  results.topQueries = await getTopQueries(siteUrl, dateRange);

  console.log('  → Getting top pages...');
  results.topPages = await getSearchConsoleTopPages(siteUrl, dateRange);

  console.log('  → Getting device performance...');
  results.devicePerformance = await getDevicePerformance(siteUrl, dateRange);

  console.log('  → Getting country performance...');
  results.countryPerformance = await getCountryPerformance(siteUrl, dateRange);

  const dateStr = typeof dateRange === 'string' ? dateRange : 'custom';
  saveResult(results, 'searchconsole', 'overview', dateStr);

  console.log('✅ Search Console overview complete\n');
  return results;
}

/**
 * Deep dive into keyword/query analysis
 * @param siteUrl - Search Console site URL
 * @param dateRange - Optional date range
 */
export async function keywordAnalysis(siteUrl: string, dateRange?: string | SearchConsoleDateRange) {
  console.log('\n🔑 Analyzing keywords...');
  const results: Record<string, unknown> = {};

  console.log('  → Getting top queries...');
  results.queries = await getTopQueries(siteUrl, dateRange);

  console.log('  → Getting device breakdown for queries...');
  results.deviceBreakdown = await getDevicePerformance(siteUrl, dateRange);

  const dateStr = typeof dateRange === 'string' ? dateRange : 'custom';
  saveResult(results, 'searchconsole', 'keyword_analysis', dateStr);

  console.log('✅ Keyword analysis complete\n');
  return results;
}

/**
 * SEO page performance analysis
 * @param siteUrl - Search Console site URL
 * @param dateRange - Optional date range
 */
export async function seoPagePerformance(siteUrl: string, dateRange?: string | SearchConsoleDateRange) {
  console.log('\n📄 Analyzing SEO page performance...');
  const results: Record<string, unknown> = {};

  console.log('  → Getting top pages by clicks...');
  results.topPages = await getSearchConsoleTopPages(siteUrl, dateRange);

  console.log('  → Getting country breakdown...');
  results.countryBreakdown = await getCountryPerformance(siteUrl, dateRange);

  const dateStr = typeof dateRange === 'string' ? dateRange : 'custom';
  saveResult(results, 'searchconsole', 'seo_page_performance', dateStr);

  console.log('✅ SEO page performance analysis complete\n');
  return results;
}

/**
 * Request re-indexing for updated URLs
 * @param urls - Array of URLs to reindex
 */
export async function reindexUrls(urls: string[]) {
  console.log(`\n🔄 Requesting re-indexing for ${urls.length} URL(s)...`);
  const results: Array<{ url: string; status: string; error?: string }> = [];

  for (const url of urls) {
    try {
      console.log(`  → Requesting indexing: ${url}`);
      const result = await requestIndexing(url, { save: false });
      results.push({ url, status: 'submitted', ...result });
    } catch (error) {
      console.log(`  ✗ Failed: ${url}`);
      results.push({ url, status: 'failed', error: String(error) });
    }
  }

  saveResult(results, 'indexing', 'reindex_batch');
  console.log('✅ Re-indexing requests complete\n');
  return results;
}

/**
 * Check index status for URLs
 * @param siteUrl - Search Console site URL (required for inspection)
 * @param urls - Array of URLs to check
 */
export async function checkIndexStatus(siteUrl: string, urls: string[]) {
  console.log(`\n🔎 Checking index status for ${urls.length} URL(s)...`);
  const results: Array<{ url: string; indexed: boolean; status: unknown }> = [];

  for (const url of urls) {
    try {
      console.log(`  → Inspecting: ${url}`);
      const result = await inspectUrl(url, { siteUrl, save: false });
      results.push({
        url,
        indexed: result.indexStatus.verdict === 'PASS',
        status: result.indexStatus,
      });
    } catch (error) {
      console.log(`  ✗ Failed: ${url}`);
      results.push({ url, indexed: false, status: { error: String(error) } });
    }
  }

  saveResult(results, 'indexing', 'index_status_check');
  console.log('✅ Index status check complete\n');
  return results;
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Get available dimensions and metrics for a property
 * @param propertyId - GA4 Property ID (numeric)
 */
export async function getAvailableFields(propertyId: string) {
  console.log('\n📋 Getting available fields...');
  const metadata = await getPropertyMetadata(propertyId);
  console.log(`  → Found ${metadata.dimensions?.length || 0} dimensions`);
  console.log(`  → Found ${metadata.metrics?.length || 0} metrics`);
  console.log('✅ Field retrieval complete\n');
  return metadata;
}

// Print help when run directly
if (process.argv[1] === new URL(import.meta.url).pathname) {
  console.log(`
GA4 Analytics Toolkit (Nexus Edition)
=====================================

Discovery functions:
  - listGa4Properties()              List all accessible GA4 properties
  - listSearchConsoleSites()         List all accessible Search Console sites

GA4 High-level functions:
  - siteOverview(propertyId, dateRange?)        Comprehensive site snapshot
  - trafficAnalysis(propertyId, dateRange?)     Deep dive on sources
  - contentPerformance(propertyId, dateRange?)  Top pages analysis
  - userBehavior(propertyId, dateRange?)        Engagement patterns
  - compareDateRanges(propertyId, range1, range2)  Period comparison
  - liveSnapshot(propertyId)                    Real-time data

Search Console functions:
  - searchConsoleOverview(siteUrl, dateRange?)  Combined SEO snapshot
  - keywordAnalysis(siteUrl, dateRange?)        Query/keyword analysis
  - seoPagePerformance(siteUrl, dateRange?)     Page-level SEO metrics
  - getTopQueries(siteUrl, dateRange?)          Top search queries
  - getTopPages(siteUrl, dateRange?)            Top pages by clicks
  - getDevicePerformance(siteUrl, dateRange?)   Mobile vs desktop
  - getCountryPerformance(siteUrl, dateRange?)  Traffic by country

Indexing functions:
  - reindexUrls(urls)                           Request re-indexing for URLs
  - checkIndexStatus(siteUrl, urls)             Check if URLs are indexed
  - requestIndexing(url)                        Request single URL re-crawl
  - inspectUrl(url, { siteUrl })                Inspect URL index status

Low-level GA4 functions:
  - runReport({ propertyId, dimensions, metrics, dateRange })
  - getPageViews(propertyId, dateRange?)
  - getTrafficSources(propertyId, dateRange?)
  - getUserDemographics(propertyId, dateRange?)
  - getEventCounts(propertyId, dateRange?)
  - getActiveUsers(propertyId)
  - getRealtimeEvents(propertyId)
  - getPropertyMetadata(propertyId)

All results are automatically saved to /results directory.

Configuration:
  Set GOOGLE_APPLICATION_CREDENTIALS env var to the path of your service account JSON.
  Example: /home/node/.openclaw/credentials/google/analytics-sa.json
`);
}

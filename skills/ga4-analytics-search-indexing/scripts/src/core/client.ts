/**
 * GA4 API Client - Multi-property version with ADC support
 * Also includes Search Console and Indexing API clients
 */

import { BetaAnalyticsDataClient } from '@google-analytics/data';
import { AnalyticsAdminServiceClient } from '@google-analytics/admin';
import { searchconsole } from '@googleapis/searchconsole';
import { indexing } from '@googleapis/indexing';
import { google } from 'googleapis';
import { getSettings, validateSettings } from '../config/settings.js';

// Singleton client instances
let clientInstance: BetaAnalyticsDataClient | null = null;
let adminClientInstance: AnalyticsAdminServiceClient | null = null;
let searchConsoleClientInstance: ReturnType<typeof searchconsole> | null = null;
let indexingClientInstance: ReturnType<typeof indexing> | null = null;

/**
 * Get the Google Auth client configuration
 * Uses GOOGLE_APPLICATION_CREDENTIALS if set, otherwise falls back to ADC
 */
function getAuthConfig() {
  const settings = getSettings();
  
  if (settings.googleApplicationCredentials) {
    // Use explicit credentials file
    return {
      keyFile: settings.googleApplicationCredentials,
      scopes: [
        'https://www.googleapis.com/auth/analytics.readonly',
        'https://www.googleapis.com/auth/webmasters.readonly',
        'https://www.googleapis.com/auth/indexing',
      ],
    };
  }
  
  // Fall back to Application Default Credentials
  return {
    scopes: [
      'https://www.googleapis.com/auth/analytics.readonly',
      'https://www.googleapis.com/auth/webmasters.readonly',
      'https://www.googleapis.com/auth/indexing',
    ],
  };
}

/**
 * Get the GA4 Analytics Data API client (singleton)
 *
 * @returns The BetaAnalyticsDataClient instance
 * @throws Error if credentials are invalid
 */
export function getClient(): BetaAnalyticsDataClient {
  if (clientInstance) {
    return clientInstance;
  }

  const validation = validateSettings();
  if (!validation.valid) {
    throw new Error(`Invalid settings: ${validation.errors.join(', ')}`);
  }

  const authConfig = getAuthConfig();
  clientInstance = new BetaAnalyticsDataClient(authConfig);

  return clientInstance;
}

/**
 * Get the GA4 Admin API client for property discovery (singleton)
 *
 * @returns The AnalyticsAdminServiceClient instance
 */
export function getAdminClient(): AnalyticsAdminServiceClient {
  if (adminClientInstance) {
    return adminClientInstance;
  }

  const authConfig = getAuthConfig();
  adminClientInstance = new AnalyticsAdminServiceClient(authConfig);

  return adminClientInstance;
}

/**
 * Format a property ID for API calls
 *
 * @param propertyId - The GA4 property ID (numeric)
 * @returns Property ID with "properties/" prefix
 */
export function formatPropertyId(propertyId: string): string {
  return `properties/${propertyId}`;
}

/**
 * Reset the client singleton (useful for testing)
 */
export function resetClient(): void {
  clientInstance = null;
  adminClientInstance = null;
  searchConsoleClientInstance = null;
  indexingClientInstance = null;
}

/**
 * Get Google Auth client for Search Console and Indexing APIs
 */
function getGoogleAuth() {
  const settings = getSettings();
  
  if (settings.googleApplicationCredentials) {
    return new google.auth.GoogleAuth({
      keyFile: settings.googleApplicationCredentials,
      scopes: [
        'https://www.googleapis.com/auth/webmasters.readonly',
        'https://www.googleapis.com/auth/indexing',
      ],
    });
  }
  
  return new google.auth.GoogleAuth({
    scopes: [
      'https://www.googleapis.com/auth/webmasters.readonly',
      'https://www.googleapis.com/auth/indexing',
    ],
  });
}

/**
 * Get the Search Console API client (singleton)
 *
 * @returns The Search Console client instance
 * @throws Error if credentials are invalid
 */
export function getSearchConsoleClient(): ReturnType<typeof searchconsole> {
  if (searchConsoleClientInstance) {
    return searchConsoleClientInstance;
  }

  const auth = getGoogleAuth();
  searchConsoleClientInstance = searchconsole({ version: 'v1', auth });

  return searchConsoleClientInstance;
}

/**
 * Get the Indexing API client (singleton)
 *
 * @returns The Indexing client instance
 * @throws Error if credentials are invalid
 */
export function getIndexingClient(): ReturnType<typeof indexing> {
  if (indexingClientInstance) {
    return indexingClientInstance;
  }

  const auth = getGoogleAuth();
  indexingClientInstance = indexing({ version: 'v3', auth });

  return indexingClientInstance;
}

/**
 * List all GA4 properties accessible to the service account
 *
 * @returns Array of properties with their IDs and display names
 */
export async function listGa4Properties(): Promise<Array<{ propertyId: string; displayName: string; accountId: string }>> {
  const adminClient = getAdminClient();
  const [accounts] = await adminClient.listAccounts();
  
  const properties: Array<{ propertyId: string; displayName: string; accountId: string }> = [];
  
  for (const account of accounts || []) {
    if (!account.name) continue;
    const accountId = account.name.split('/')[1];
    
    try {
      const [accountProperties] = await adminClient.listProperties({
        filter: `parent:accounts/${accountId}`,
      });
      
      for (const property of accountProperties || []) {
        if (property.name) {
          const propertyId = property.name.split('/')[1];
          properties.push({
            propertyId,
            displayName: property.displayName || 'Unnamed Property',
            accountId,
          });
        }
      }
    } catch (error) {
      // Skip accounts we can't access
      console.warn(`Could not list properties for account ${accountId}: ${error}`);
    }
  }
  
  return properties;
}

/**
 * List all Search Console properties accessible to the service account
 *
 * @returns Array of site URLs
 */
export async function listSearchConsoleSites(): Promise<Array<{ siteUrl: string; permissionLevel: string }>> {
  const client = getSearchConsoleClient();
  const response = await client.sites.list();
  
  return (response.data.siteEntry || []).map((entry: any) => ({
    siteUrl: entry.siteUrl || '',
    permissionLevel: entry.permissionLevel || 'unknown',
  }));
}

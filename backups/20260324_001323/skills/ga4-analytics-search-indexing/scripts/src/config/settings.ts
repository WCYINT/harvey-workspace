/**
 * Settings Module - Environment configuration for GA4 API
 * Multi-property version - supports GOOGLE_APPLICATION_CREDENTIALS
 */

import { config } from 'dotenv';
import { join } from 'path';

// Load .env file from current working directory
config();

/**
 * Settings interface for GA4 API configuration
 */
export interface Settings {
  /** Default date range for reports (e.g., "30d", "7d") */
  defaultDateRange: string;
  /** Directory path for storing results */
  resultsDir: string;
  /** Path to Google Application Credentials JSON (optional - uses ADC if not set) */
  googleApplicationCredentials?: string;
}

/**
 * Validation result from validateSettings()
 */
export interface ValidationResult {
  valid: boolean;
  errors: string[];
}

/**
 * Get current settings from environment variables
 */
export function getSettings(): Settings {
  return {
    defaultDateRange: process.env.GA4_DEFAULT_DATE_RANGE || '30d',
    resultsDir: join(process.cwd(), 'results'),
    googleApplicationCredentials: process.env.GOOGLE_APPLICATION_CREDENTIALS,
  };
}

/**
 * Validate that basic settings are present
 * Note: Property IDs and site URLs are now passed as parameters, not env vars
 */
export function validateSettings(): ValidationResult {
  const settings = getSettings();
  const errors: string[] = [];

  // No required env vars anymore - GOOGLE_APPLICATION_CREDENTIALS is optional
  // (falls back to Application Default Credentials)

  return {
    valid: errors.length === 0,
    errors,
  };
}

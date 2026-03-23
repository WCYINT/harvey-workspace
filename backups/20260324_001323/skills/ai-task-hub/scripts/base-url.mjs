const DEFAULT_BASE_URL = 'https://gateway-api.binaryworks.app';

export function getDefaultBaseUrl() {
  return DEFAULT_BASE_URL;
}

export function normalizeBaseUrl(baseUrlRaw) {
  const candidate = readToken(baseUrlRaw) || DEFAULT_BASE_URL;
  try {
    const parsed = new URL(candidate);
    if (parsed.protocol !== 'https:') {
      throw new Error('invalid protocol');
    }
    const normalized = parsed.toString().replace(/\/+$/, '');
    if (normalized !== DEFAULT_BASE_URL) {
      throw createBaseUrlError(
        400,
        `base_url is locked to ${DEFAULT_BASE_URL} in the published package`
      );
    }
    return DEFAULT_BASE_URL;
  } catch (error) {
    if (error && typeof error === 'object' && error.code === 'VALIDATION_BAD_REQUEST') {
      throw error;
    }
    throw createBaseUrlError(400, `invalid base_url: ${String(baseUrlRaw ?? '')}`);
  }
}

function readToken(value) {
  if (typeof value !== 'string') {
    return '';
  }
  return value.trim();
}

function createBaseUrlError(status, message) {
  const error = new Error(message);
  error.status = status;
  error.code = 'VALIDATION_BAD_REQUEST';
  return error;
}

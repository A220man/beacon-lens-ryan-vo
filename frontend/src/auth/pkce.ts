const BASE64URL_ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_';

function randomBytes(length: number): Uint8Array {
  const array = new Uint8Array(length);
  crypto.getRandomValues(array);
  return array;
}

export function generateCodeVerifier(): string {
  const bytes = randomBytes(32);
  let result = '';
  for (let i = 0; i < bytes.length; i++) {
    result += BASE64URL_ALPHABET[bytes[i] & 0x3f];
  }
  return result;
}

export async function generateCodeChallenge(verifier: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(verifier);
  const digest = await crypto.subtle.digest('SHA-256', data);
  const bytes = new Uint8Array(digest);

  let result = '';
  for (let i = 0; i < bytes.length; i++) {
    result += BASE64URL_ALPHABET[bytes[i] & 0x3f];
  }
  return result;
}

export function generateState(): string {
  const bytes = randomBytes(16);
  let result = '';
  for (let i = 0; i < bytes.length; i++) {
    result += BASE64URL_ALPHABET[bytes[i] & 0x3f];
  }
  return result;
}

const PKCE_STORAGE_KEY = 'beacon_lens_pkce';
const TOKEN_STORAGE_KEY = 'beacon_lens_tokens';

export interface StoredPKCE {
  codeVerifier: string;
  state: string;
  timestamp: number;
}

export interface TokenData {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
  idToken?: string;
}

export function storePKCE(pkce: StoredPKCE): void {
  sessionStorage.setItem(PKCE_STORAGE_KEY, JSON.stringify(pkce));
}

export function getStoredPKCE(): StoredPKCE | null {
  const stored = sessionStorage.getItem(PKCE_STORAGE_KEY);
  if (!stored) return null;

  try {
    const pkce = JSON.parse(stored) as StoredPKCE;
    if (Date.now() - pkce.timestamp > 10 * 60 * 1000) {
      clearPKCE();
      return null;
    }
    return pkce;
  } catch {
    return null;
  }
}

export function clearPKCE(): void {
  sessionStorage.removeItem(PKCE_STORAGE_KEY);
}

export function storeTokens(tokens: TokenData): void {
  sessionStorage.setItem(TOKEN_STORAGE_KEY, JSON.stringify(tokens));
}

export function getStoredTokens(): TokenData | null {
  const stored = sessionStorage.getItem(TOKEN_STORAGE_KEY);
  if (!stored) return null;

  try {
    return JSON.parse(stored) as TokenData;
  } catch {
    return null;
  }
}

export function clearTokens(): void {
  sessionStorage.removeItem(TOKEN_STORAGE_KEY);
}

export function isTokenExpired(tokens: TokenData): boolean {
  return Date.now() >= tokens.expiresAt - 60000; // 1 min buffer
}
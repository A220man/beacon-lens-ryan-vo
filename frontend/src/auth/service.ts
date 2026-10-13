import { getAuthConfig, buildAuthUrl, buildLogoutUrl } from './config';
import {
  generateCodeVerifier,
  generateCodeChallenge,
  generateState,
  storePKCE,
  getStoredPKCE,
  clearPKCE,
  storeTokens,
  getStoredTokens,
  clearTokens,
  isTokenExpired,
  type TokenData,
} from './pkce';

export { getStoredTokens, type TokenData } from './pkce';

export interface UserInfo {
  sub: string;
  email?: string;
  preferred_username?: string;
  realm_access?: { roles: string[] };
  resource_access?: Record<string, { roles: string[] }>;
}

export async function initiateLogin(): Promise<void> {
  const config = getAuthConfig();
  const codeVerifier = generateCodeVerifier();
  const codeChallenge = await generateCodeChallenge(codeVerifier);
  const state = generateState();

  storePKCE({ codeVerifier, state, timestamp: Date.now() });

  const authUrl = buildAuthUrl(config, state, codeChallenge);
  window.location.href = authUrl;
}

export async function handleCallback(): Promise<TokenData | null> {
  const urlParams = new URLSearchParams(window.location.search);
  const code = urlParams.get('code');
  const state = urlParams.get('state');
  const error = urlParams.get('error');
  const errorDescription = urlParams.get('error_description');

  const storedPKCE = getStoredPKCE();

  if (!storedPKCE) {
    throw new Error('Missing PKCE data - login session expired');
  }

  if (state !== storedPKCE.state) {
    clearPKCE();
    throw new Error('Invalid state parameter - possible CSRF attack');
  }

  if (error) {
    clearPKCE();
    throw new Error(errorDescription || error);
  }

  if (!code) {
    throw new Error('No authorization code received');
  }

  const config = getAuthConfig();
  const tokenResponse = await fetch(`${config.keycloakUrl}/realms/${config.realm}/protocol/openid-connect/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'authorization_code',
      client_id: config.clientId,
      code,
      redirect_uri: config.redirectUri,
      code_verifier: storedPKCE.codeVerifier,
    }),
  });

  if (!tokenResponse.ok) {
    const errorData = await tokenResponse.json().catch(() => ({}));
    throw new Error(errorData.error_description || `Token exchange failed: ${tokenResponse.status}`);
  }

  const tokens = await tokenResponse.json();
  clearPKCE();

  const tokenData: TokenData = {
    accessToken: tokens.access_token,
    refreshToken: tokens.refresh_token,
    expiresAt: Date.now() + (tokens.expires_in || 300) * 1000,
    idToken: tokens.id_token,
  };

  storeTokens(tokenData);
  return tokenData;
}

export async function refreshAccessToken(): Promise<TokenData | null> {
  const tokens = getStoredTokens();
  if (!tokens || !tokens.refreshToken) {
    return null;
  }

  const config = getAuthConfig();
  const response = await fetch(`${config.keycloakUrl}/realms/${config.realm}/protocol/openid-connect/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'refresh_token',
      client_id: config.clientId,
      refresh_token: tokens.refreshToken,
    }),
  });

  if (!response.ok) {
    clearTokens();
    return null;
  }

  const newTokens = await response.json();
  const tokenData: TokenData = {
    accessToken: newTokens.access_token,
    refreshToken: newTokens.refresh_token || tokens.refreshToken,
    expiresAt: Date.now() + (newTokens.expires_in || 300) * 1000,
    idToken: newTokens.id_token,
  };

  storeTokens(tokenData);
  return tokenData;
}

export async function getValidAccessToken(): Promise<string | null> {
  let tokens = getStoredTokens();
  if (!tokens) return null;

  if (isTokenExpired(tokens)) {
    tokens = await refreshAccessToken();
    if (!tokens) return null;
  }

  return tokens.accessToken;
}

export function logout(): void {
  const config = getAuthConfig();
  clearTokens();
  clearPKCE();
  window.location.href = buildLogoutUrl(config);
}

export function hasRole(tokens: TokenData, role: string): boolean {
  if (!tokens.idToken) return false;
  try {
    const payload = JSON.parse(atob(tokens.idToken.split('.')[1])) as UserInfo;
    if (payload.realm_access?.roles.includes(role)) return true;
    if (payload.resource_access) {
      for (const clientRoles of Object.values(payload.resource_access)) {
        if (clientRoles.roles.includes(role)) return true;
      }
    }
    return false;
  } catch {
    return false;
  }
}

export function getUserInfo(tokens: TokenData): UserInfo | null {
  if (!tokens.idToken) return null;
  try {
    return JSON.parse(atob(tokens.idToken.split('.')[1])) as UserInfo;
  } catch {
    return null;
  }
}

export async function authenticatedFetch(
  input: RequestInfo | URL,
  init: RequestInit = {}
): Promise<Response> {
  const accessToken = await getValidAccessToken();
  if (!accessToken) {
    throw new Error('Not authenticated');
  }

  return fetch(input, {
    ...init,
    headers: {
      ...init.headers,
      Authorization: `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
  });
}
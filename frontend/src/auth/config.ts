export interface AuthConfig {
  keycloakUrl: string;
  realm: string;
  clientId: string;
  redirectUri: string;
  scopes: string[];
}

export function getAuthConfig(): AuthConfig {
  return {
    keycloakUrl: import.meta.env.VITE_KEYCLOAK_URL || 'http://localhost:8080',
    realm: import.meta.env.VITE_KEYCLOAK_REALM || 'beacon-lens',
    clientId: import.meta.env.VITE_KEYCLOAK_CLIENT_ID || 'beacon-lens-frontend',
    redirectUri: `${window.location.origin}/callback`,
    scopes: ['openid', 'profile', 'email', 'offline_access'],
  };
}

export function buildAuthUrl(config: AuthConfig, state: string, codeChallenge: string): string {
  const params = new URLSearchParams({
    response_type: 'code',
    client_id: config.clientId,
    redirect_uri: config.redirectUri,
    scope: config.scopes.join(' '),
    state,
    code_challenge: codeChallenge,
    code_challenge_method: 'S256',
  });

  return `${config.keycloakUrl}/realms/${config.realm}/protocol/openid-connect/auth?${params.toString()}`;
}

export function buildLogoutUrl(config: AuthConfig): string {
  const params = new URLSearchParams({
    client_id: config.clientId,
    post_logout_redirect_uri: window.location.origin,
  });

  return `${config.keycloakUrl}/realms/${config.realm}/protocol/openid-connect/logout?${params.toString()}`;
}
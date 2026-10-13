import { createContext, useContext, useEffect, useState, ReactNode, useCallback } from 'react';
import {
  getValidAccessToken,
  getStoredTokens,
  handleCallback,
  logout as authLogout,
  type UserInfo,
} from './service';

interface AuthContextValue {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: UserInfo | null;
  accessToken: string | null;
  login: () => void;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<UserInfo | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);

  const refreshUser = useCallback(async () => {
    const tokens = getStoredTokens();
    if (!tokens) {
      setIsAuthenticated(false);
      setUser(null);
      setAccessToken(null);
      setIsLoading(false);
      return;
    }

    const token = await getValidAccessToken();
    if (token) {
      setIsAuthenticated(true);
      setAccessToken(token);
      const userInfo = tokens.idToken ? JSON.parse(atob(tokens.idToken.split('.')[1])) as UserInfo : null;
      setUser(userInfo);
    } else {
      setIsAuthenticated(false);
      setUser(null);
      setAccessToken(null);
    }
    setIsLoading(false);
  }, []);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.has('code') || params.has('error')) {
      handleCallback()
        .then(() => refreshUser())
        .catch((err) => {
          console.error('Auth callback failed:', err);
          setIsAuthenticated(false);
          setUser(null);
          setAccessToken(null);
          setIsLoading(false);
        });
    } else {
      refreshUser();
    }
  }, [refreshUser]);

  const login = useCallback(() => {
    import('./service').then(({ initiateLogin }) => initiateLogin());
  }, []);

  const logout = useCallback(() => {
    authLogout();
  }, []);

  return (
    <AuthContext.Provider value={{ isAuthenticated, isLoading, user, accessToken, login, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
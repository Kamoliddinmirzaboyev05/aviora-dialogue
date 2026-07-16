import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";

import { api, tokenStore } from "../../services/api";
import type { MeResponse, Workspace } from "../../types/api";

type AuthContextValue = {
  me?: MeResponse;
  workspace?: Workspace;
  isAuthenticated: boolean;
  isLoading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [hasToken, setHasToken] = useState(Boolean(tokenStore.access));
  const meQuery = useQuery({
    queryKey: ["me", hasToken],
    queryFn: api.me,
    enabled: hasToken
  });

  const value = useMemo<AuthContextValue>(() => {
    const workspace = meQuery.data?.memberships[0]?.workspace;
    return {
      me: meQuery.data,
      workspace,
      isAuthenticated: hasToken,
      isLoading: meQuery.isLoading,
      signIn: async (email, password) => {
        await api.login(email, password);
        setHasToken(true);
      },
      signOut: () => {
        tokenStore.clear();
        setHasToken(false);
      }
    };
  }, [hasToken, meQuery.data, meQuery.isLoading]);

  useEffect(() => {
    if (meQuery.isError) {
      tokenStore.clear();
      setHasToken(false);
    }
  }, [meQuery.isError]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside AuthProvider");
  return value;
}

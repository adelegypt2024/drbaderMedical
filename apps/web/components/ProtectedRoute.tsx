'use client';

import { useRouter } from 'next/router';
import { ReactNode, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import type { UserRole } from '../context/AuthContext';

interface ProtectedRouteProps {
  roles?: UserRole[];
  children: ReactNode;
}

export function ProtectedRoute({ roles, children }: ProtectedRouteProps) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      if (!user) {
        void router.replace('/login');
      } else if (roles && !roles.includes(user.role)) {
        void router.replace('/');
      }
    }
  }, [user, loading, roles, router]);

  if (loading || !user) {
    return <p>Loading...</p>;
  }

  if (roles && !roles.includes(user.role)) {
    return <p>You do not have permission to view this page.</p>;
  }

  return <>{children}</>;
}

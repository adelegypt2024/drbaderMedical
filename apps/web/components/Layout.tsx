'use client';

import Link from 'next/link';
import { useRouter } from 'next/router';
import { ReactNode, useMemo } from 'react';
import { useAuth } from '../hooks/useAuth';

interface LayoutProps {
  title?: string;
  children: ReactNode;
}

export function Layout({ title, children }: LayoutProps) {
  const { user, logout } = useAuth();
  const router = useRouter();

  const links = useMemo(() => {
    if (!user) {
      return [
        { href: '/login', label: 'Login' },
        { href: '/register', label: 'Register' }
      ];
    }

    const baseLinks = [
      { href: '/', label: 'Dashboard' },
      { href: '/appointments', label: 'Appointments' }
    ];
    if (user.role === 'client') {
      baseLinks.push({ href: '/requests/new', label: 'New Request' });
    }
    if (user.role === 'consultant') {
      baseLinks.push({ href: '/consultant/profile', label: 'My Profile' });
      baseLinks.push({ href: '/consultant/requests', label: 'Open Requests' });
    }
    if (user.role === 'admin') {
      baseLinks.push({ href: '/admin', label: 'Admin' });
    }
    return baseLinks;
  }, [user]);

  return (
    <div className="container">
      <header>
        <div>
          <h1>{title ?? 'Medical Consulting Platform'}</h1>
          {user && (
            <span className="badge">{`${user.firstName} ${user.lastName}`} ({user.role})</span>
          )}
        </div>
        <nav>
          {links.map((link) => (
            <Link key={link.href} href={link.href} legacyBehavior>
              <a className={router.pathname === link.href ? 'active' : ''}>{link.label}</a>
            </Link>
          ))}
          {user && (
            <button
              onClick={() => {
                logout();
                void router.push('/login');
              }}
            >
              Logout
            </button>
          )}
        </nav>
      </header>
      <main className="card">{children}</main>
    </div>
  );
}

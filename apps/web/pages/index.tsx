'use client';

import { useQuery } from '@tanstack/react-query';
import { Layout } from '../components/Layout';
import { ProtectedRoute } from '../components/ProtectedRoute';
import api from '../lib/api';

interface DashboardStats {
  requests: number;
  proposals: number;
  contracts: number;
  invoices: number;
  notifications: string[];
}

export default function Dashboard() {
  const { data, isLoading } = useQuery<DashboardStats>(['dashboard'], async () => {
    const response = await api.get('/dashboard');
    return response.data as DashboardStats;
  });

  return (
    <ProtectedRoute>
      <Layout title="Dashboard">
        {isLoading && <p>Loading dashboard...</p>}
        {data && (
          <div>
            <section>
              <h2>Key metrics</h2>
              <ul>
                <li>Total requests: {data.requests}</li>
                <li>Active proposals: {data.proposals}</li>
                <li>Contracts in flight: {data.contracts}</li>
                <li>Open invoices: {data.invoices}</li>
              </ul>
            </section>
            <section>
              <h2>Notifications</h2>
              <ul>
                {data.notifications.map((note) => (
                  <li key={note}>{note}</li>
                ))}
              </ul>
            </section>
          </div>
        )}
      </Layout>
    </ProtectedRoute>
  );
}

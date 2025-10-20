'use client';

import { useQuery } from '@tanstack/react-query';
import { Layout } from '../../components/Layout';
import { ProtectedRoute } from '../../components/ProtectedRoute';
import api from '../../lib/api';

type AdminDashboard = {
  users: number;
  requests: number;
  contracts: number;
  revenue: number;
  reports: Array<{ label: string; value: string }>;
};

export default function AdminPage() {
  const { data } = useQuery<AdminDashboard>(['admin-dashboard'], async () => {
    const response = await api.get('/admin/dashboard');
    return response.data as AdminDashboard;
  });

  return (
    <ProtectedRoute roles={['admin']}>
      <Layout title="Admin panel">
        {data ? (
          <div>
            <section>
              <h2>Platform overview</h2>
              <ul>
                <li>Total users: {data.users}</li>
                <li>Active requests: {data.requests}</li>
                <li>Contracts in progress: {data.contracts}</li>
                <li>Projected revenue: ${data.revenue.toFixed(2)}</li>
              </ul>
            </section>
            <section>
              <h2>Reports</h2>
              <ul>
                {data.reports.map((report) => (
                  <li key={report.label}>
                    <strong>{report.label}:</strong> {report.value}
                  </li>
                ))}
              </ul>
            </section>
          </div>
        ) : (
          <p>Loading admin data…</p>
        )}
      </Layout>
    </ProtectedRoute>
  );
}

'use client';

import { useMutation, useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { Layout } from '../../components/Layout';
import { ProtectedRoute } from '../../components/ProtectedRoute';
import api from '../../lib/api';

type RequestListItem = {
  id: string;
  title: string;
  category: string;
  budget: string;
  targetDate: string;
  status: string;
};

export default function ConsultantRequestsPage() {
  const [filters, setFilters] = useState({ category: '', budget: '', timeframe: '' });
  const { data, refetch } = useQuery<RequestListItem[]>(['open-requests', filters], async () => {
    const response = await api.get('/consultants/requests', { params: filters });
    return response.data as RequestListItem[];
  });
  const proposalMutation = useMutation(async (payload: { requestId: string; scope: string; timeline: string; cost: number }) => {
    const { requestId, ...data } = payload;
    await api.post(`/requests/${requestId}/proposals`, data);
  });

  return (
    <ProtectedRoute roles={['consultant']}>
      <Layout title="Open requests">
        <section>
          <h2>Filters</h2>
          <div style={{ display: 'grid', gap: '1rem', gridTemplateColumns: 'repeat(auto-fit,minmax(180px,1fr))' }}>
            <input
              placeholder="Category"
              value={filters.category}
              onChange={(event) => setFilters((prev) => ({ ...prev, category: event.target.value }))}
            />
            <input
              placeholder="Budget"
              value={filters.budget}
              onChange={(event) => setFilters((prev) => ({ ...prev, budget: event.target.value }))}
            />
            <input
              placeholder="Target before"
              type="date"
              value={filters.timeframe}
              onChange={(event) => setFilters((prev) => ({ ...prev, timeframe: event.target.value }))}
            />
            <button onClick={() => refetch()}>Apply</button>
          </div>
        </section>
        <section>
          <h2>Requests</h2>
          <table className="table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Category</th>
                <th>Budget</th>
                <th>Target</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {(data ?? []).map((item) => (
                <tr key={item.id}>
                  <td>{item.title}</td>
                  <td>{item.category}</td>
                  <td>{item.budget}</td>
                  <td>{new Date(item.targetDate).toLocaleDateString()}</td>
                  <td>
                    <ProposalForm
                      requestId={item.id}
                      onSubmit={(proposal) =>
                        proposalMutation.mutate(
                          { requestId: item.id, ...proposal },
                          {
                            onSuccess: () => {
                              void refetch();
                            }
                          }
                        )
                      }
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </Layout>
    </ProtectedRoute>
  );
}

function ProposalForm({
  requestId,
  onSubmit
}: {
  requestId: string;
  onSubmit: (payload: { body: string; timeline: string; cost: number }) => void;
}) {
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ scope: '', timeline: '', cost: 0 });
  if (!open) {
    return (
      <button onClick={() => setOpen(true)} aria-label={`Propose work for request ${requestId}`}>
        Send proposal
      </button>
    );
  }
  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit(form);
        setOpen(false);
      }}
    >
      <textarea
        placeholder="Scope of work"
        value={form.scope}
        onChange={(event) => setForm((prev) => ({ ...prev, scope: event.target.value }))}
        required
      />
      <input
        placeholder="Timeline"
        value={form.timeline}
        onChange={(event) => setForm((prev) => ({ ...prev, timeline: event.target.value }))}
        required
      />
      <input
        type="number"
        placeholder="Cost"
        value={form.cost}
        onChange={(event) => setForm((prev) => ({ ...prev, cost: Number(event.target.value) }))}
        required
      />
      <button type="submit">Submit</button>
    </form>
  );
}

'use client';

import { useMutation, useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { Layout } from '../../components/Layout';
import { ProtectedRoute } from '../../components/ProtectedRoute';
import api from '../../lib/api';

type Appointment = {
  id: string;
  title: string;
  startTime: string;
  endTime: string;
  timezone: string;
};

export default function AppointmentsPage() {
  const { data, refetch } = useQuery<Appointment[]>(['appointments'], async () => {
    const response = await api.get('/appointments');
    return response.data as Appointment[];
  });
  const [form, setForm] = useState({
    title: '',
    startTime: '',
    endTime: '',
    timezone: 'UTC'
  });
  const mutation = useMutation(async () => {
    await api.post('/appointments', form);
  });

  return (
    <ProtectedRoute>
      <Layout title="Appointments">
        <section>
          <h2>Schedule an appointment</h2>
          <form
            onSubmit={(event) => {
              event.preventDefault();
              mutation.mutate(undefined, {
                onSuccess: () => {
                  setForm({ title: '', startTime: '', endTime: '', timezone: 'UTC' });
                  void refetch();
                }
              });
            }}
          >
            <label htmlFor="title">Title</label>
            <input id="title" value={form.title} onChange={(event) => setForm((prev) => ({ ...prev, title: event.target.value }))} required />
            <label htmlFor="startTime">Start</label>
            <input
              id="startTime"
              type="datetime-local"
              value={form.startTime}
              onChange={(event) => setForm((prev) => ({ ...prev, startTime: event.target.value }))}
              required
            />
            <label htmlFor="endTime">End</label>
            <input
              id="endTime"
              type="datetime-local"
              value={form.endTime}
              onChange={(event) => setForm((prev) => ({ ...prev, endTime: event.target.value }))}
              required
            />
            <label htmlFor="timezone">Timezone</label>
            <input
              id="timezone"
              value={form.timezone}
              onChange={(event) => setForm((prev) => ({ ...prev, timezone: event.target.value }))}
              required
            />
            <button type="submit">Schedule</button>
          </form>
        </section>
        <section>
          <h2>Upcoming</h2>
          <ul>
            {(data ?? []).map((appointment) => (
              <li key={appointment.id}>
                <strong>{appointment.title}</strong> —{' '}
                {new Date(appointment.startTime).toLocaleString()} to {new Date(appointment.endTime).toLocaleString()} ({appointment.timezone})
              </li>
            ))}
          </ul>
        </section>
      </Layout>
    </ProtectedRoute>
  );
}

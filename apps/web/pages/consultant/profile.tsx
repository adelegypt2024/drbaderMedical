'use client';

import { useMutation, useQuery } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { Layout } from '../../components/Layout';
import { ProtectedRoute } from '../../components/ProtectedRoute';
import api from '../../lib/api';

interface ConsultantProfile {
  specialties: string[];
  hourlyRate: number;
  yearsExperience: number;
  portfolioUrl?: string;
  bio?: string;
  availability?: string;
}

export default function ConsultantProfilePage() {
  const { data } = useQuery<ConsultantProfile>(['consultant-profile'], async () => {
    const response = await api.get('/consultants/me');
    return response.data as ConsultantProfile;
  });
  const [form, setForm] = useState<ConsultantProfile>(
    data ?? {
      specialties: [],
      hourlyRate: 0,
      yearsExperience: 0,
      portfolioUrl: '',
      bio: '',
      availability: ''
    }
  );
  useEffect(() => {
    if (data) {
      setForm(data);
    }
  }, [data]);
  const mutation = useMutation(async (payload: ConsultantProfile) => {
    await api.put('/consultants/me', payload);
  });

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    mutation.mutate(form);
  };

  return (
    <ProtectedRoute roles={['consultant']}>
      <Layout title="Consultant profile">
        <form onSubmit={handleSubmit}>
          <label htmlFor="specialties">Specialties (comma separated)</label>
          <input
            id="specialties"
            value={form.specialties.join(', ')}
            onChange={(event) =>
              setForm((prev) => ({ ...prev, specialties: event.target.value.split(',').map((v) => v.trim()) }))
            }
          />
          <label htmlFor="hourlyRate">Hourly rate</label>
          <input
            id="hourlyRate"
            type="number"
            value={form.hourlyRate}
            onChange={(event) => setForm((prev) => ({ ...prev, hourlyRate: Number(event.target.value) }))}
            required
          />
          <label htmlFor="yearsExperience">Years of experience</label>
          <input
            id="yearsExperience"
            type="number"
            value={form.yearsExperience}
            onChange={(event) => setForm((prev) => ({ ...prev, yearsExperience: Number(event.target.value) }))}
            required
          />
          <label htmlFor="availability">Availability</label>
          <input
            id="availability"
            value={form.availability ?? ''}
            onChange={(event) => setForm((prev) => ({ ...prev, availability: event.target.value }))}
          />
          <label htmlFor="portfolioUrl">Portfolio link</label>
          <input
            id="portfolioUrl"
            value={form.portfolioUrl ?? ''}
            onChange={(event) => setForm((prev) => ({ ...prev, portfolioUrl: event.target.value }))}
          />
          <label htmlFor="bio">Bio</label>
          <textarea
            id="bio"
            rows={4}
            value={form.bio ?? ''}
            onChange={(event) => setForm((prev) => ({ ...prev, bio: event.target.value }))}
          />
          <button type="submit">Save profile</button>
          {mutation.isSuccess && <p>Profile updated</p>}
        </form>
      </Layout>
    </ProtectedRoute>
  );
}

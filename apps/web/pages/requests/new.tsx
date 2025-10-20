'use client';

import { useMutation } from '@tanstack/react-query';
import { useRouter } from 'next/router';
import { useState } from 'react';
import { Layout } from '../../components/Layout';
import { ProtectedRoute } from '../../components/ProtectedRoute';
import api from '../../lib/api';

const budgetOptions = ['<$5k', '$5k-$10k', '$10k-$25k', '$25k+'];

export default function NewRequestPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    title: '',
    description: '',
    category: '',
    budget: budgetOptions[0],
    targetDate: '',
    attachments: [] as File[]
  });
  const mutation = useMutation(async () => {
    const data = new FormData();
    data.append('title', form.title);
    data.append('description', form.description);
    data.append('category', form.category);
    data.append('budget', form.budget);
    data.append('targetDate', form.targetDate);
    for (const file of form.attachments) {
      data.append('files', file);
    }
    await api.post('/requests', data, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  });

  const handleChange = (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setForm((prev) => ({ ...prev, [event.target.name]: event.target.value }));
  };

  return (
    <ProtectedRoute roles={['client']}>
      <Layout title="Submit a service request">
        <form
          onSubmit={(event) => {
            event.preventDefault();
            mutation.mutate(undefined, {
              onSuccess: () => {
                void router.push('/');
              }
            });
          }}
        >
          <label htmlFor="title">Title</label>
          <input id="title" name="title" value={form.title} onChange={handleChange} required />
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            name="description"
            rows={5}
            value={form.description}
            onChange={handleChange}
            required
          />
          <label htmlFor="category">Category</label>
          <input id="category" name="category" value={form.category} onChange={handleChange} required />
          <label htmlFor="budget">Budget</label>
          <select id="budget" name="budget" value={form.budget} onChange={handleChange}>
            {budgetOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
          <label htmlFor="targetDate">Target date</label>
          <input id="targetDate" name="targetDate" type="date" value={form.targetDate} onChange={handleChange} required />
          <label htmlFor="attachments">Attachments</label>
          <input
            id="attachments"
            name="attachments"
            type="file"
            multiple
            onChange={(event) => {
              const files = event.target.files ? Array.from(event.target.files) : [];
              setForm((prev) => ({ ...prev, attachments: files }));
            }}
          />
          <button type="submit" disabled={mutation.isLoading}>
            {mutation.isLoading ? 'Submitting…' : 'Submit request'}
          </button>
          {mutation.isError && <p role="alert">Unable to submit request.</p>}
          {mutation.isSuccess && <p>Your request has been submitted.</p>}
        </form>
      </Layout>
    </ProtectedRoute>
  );
}

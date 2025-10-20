'use client';

import { useState } from 'react';
import { useRouter } from 'next/router';
import { Layout } from '../components/Layout';
import api from '../lib/api';

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    email: '',
    password: '',
    firstName: '',
    lastName: '',
    role: 'client'
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm((prev) => ({ ...prev, [event.target.name]: event.target.value }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError('');
    try {
      await api.post('/auth/register', form);
      setSuccess('Account created! Check your email to verify.');
      setTimeout(() => {
        void router.push('/login');
      }, 1200);
    } catch (err) {
      setError('Unable to register. This email may already be in use.');
    }
  };

  return (
    <Layout title="Create account">
      <form onSubmit={handleSubmit}>
        <label htmlFor="firstName">First name</label>
        <input id="firstName" name="firstName" value={form.firstName} onChange={handleChange} required />
        <label htmlFor="lastName">Last name</label>
        <input id="lastName" name="lastName" value={form.lastName} onChange={handleChange} required />
        <label htmlFor="email">Email</label>
        <input id="email" type="email" name="email" value={form.email} onChange={handleChange} required />
        <label htmlFor="password">Password</label>
        <input id="password" type="password" name="password" value={form.password} onChange={handleChange} required />
        <label htmlFor="role">Role</label>
        <select id="role" name="role" value={form.role} onChange={handleChange}>
          <option value="client">Client</option>
          <option value="consultant">Consultant</option>
        </select>
        {error && <p role="alert">{error}</p>}
        {success && <p>{success}</p>}
        <button type="submit">Create account</button>
      </form>
    </Layout>
  );
}

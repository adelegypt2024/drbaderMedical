'use client';

import { useState } from 'react';
import { Layout } from '../../components/Layout';
import api from '../../lib/api';

export default function RequestResetPage() {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      await api.post('/auth/password-reset', { email });
      setMessage('If your email exists we sent you reset instructions.');
    } catch (error) {
      setMessage('Unable to send reset instructions.');
    }
  };

  return (
    <Layout title="Reset password">
      <form onSubmit={handleSubmit}>
        <label htmlFor="email">Email</label>
        <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <button type="submit">Send reset link</button>
      </form>
      {message && <p>{message}</p>}
    </Layout>
  );
}

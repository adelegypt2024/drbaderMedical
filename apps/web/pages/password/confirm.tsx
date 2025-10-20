'use client';

import { useRouter } from 'next/router';
import { useState } from 'react';
import { Layout } from '../../components/Layout';
import api from '../../lib/api';

export default function ConfirmResetPage() {
  const router = useRouter();
  const { token } = router.query;
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!token || typeof token !== 'string') {
      setMessage('Missing or invalid token.');
      return;
    }
    try {
      await api.post('/auth/password-reset/confirm', { token, password });
      setMessage('Password updated. You can now sign in.');
    } catch (error) {
      setMessage('Unable to update password. The link may have expired.');
    }
  };

  return (
    <Layout title="Choose a new password">
      <form onSubmit={handleSubmit}>
        <label htmlFor="password">New password</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
        />
        <button type="submit">Save password</button>
      </form>
      {message && <p>{message}</p>}
    </Layout>
  );
}

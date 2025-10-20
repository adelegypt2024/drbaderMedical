'use client';

import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';
import { Layout } from '../components/Layout';
import api from '../lib/api';

export default function VerifyEmailPage() {
  const router = useRouter();
  const { token } = router.query;
  const [message, setMessage] = useState('Verifying email…');

  useEffect(() => {
    if (token && typeof token === 'string') {
      api
        .post('/auth/verify-email', { token })
        .then(() => {
          setMessage('Email verified successfully. You may sign in.');
        })
        .catch(() => {
          setMessage('Unable to verify email. The link may have expired.');
        });
    }
  }, [token]);

  return (
    <Layout title="Verify email">
      <p>{message}</p>
    </Layout>
  );
}

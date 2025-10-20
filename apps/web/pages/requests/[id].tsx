'use client';

import { useMutation, useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/router';
import { useState } from 'react';
import { Layout } from '../../components/Layout';
import { ProtectedRoute } from '../../components/ProtectedRoute';
import api from '../../lib/api';

type Message = {
  id: string;
  author: string;
  body: string;
  createdAt: string;
};

type RequestDetail = {
  id: string;
  title: string;
  description: string;
  status: string;
  messages: Message[];
};

export default function RequestDetailPage() {
  const router = useRouter();
  const { id } = router.query;
  const [body, setBody] = useState('');
  const { data, refetch } = useQuery<RequestDetail>(
    ['request-detail', id],
    async () => {
      const response = await api.get(`/requests/${id}`);
      return response.data as RequestDetail;
    },
    { enabled: typeof id === 'string' }
  );
  const mutation = useMutation(async () => {
    await api.post(`/requests/${id}/messages`, { body });
  });

  return (
    <ProtectedRoute>
      <Layout title={data?.title ?? 'Request detail'}>
        {data ? (
          <div>
            <p>{data.description}</p>
            <p>Status: {data.status}</p>
            <section>
              <h2>Conversation</h2>
              <ul>
                {data.messages.map((message) => (
                  <li key={message.id}>
                    <strong>{message.author}</strong>: {message.body}
                    <small> {new Date(message.createdAt).toLocaleString()}</small>
                  </li>
                ))}
              </ul>
              <form
                onSubmit={(event) => {
                  event.preventDefault();
                  mutation.mutate(undefined, {
                    onSuccess: () => {
                      setBody('');
                      void refetch();
                    }
                  });
                }}
              >
                <textarea
                  value={body}
                  onChange={(event) => setBody(event.target.value)}
                  rows={3}
                  required
                  placeholder="Write a message"
                />
                <button type="submit">Send</button>
              </form>
            </section>
          </div>
        ) : (
          <p>Loading request…</p>
        )}
      </Layout>
    </ProtectedRoute>
  );
}

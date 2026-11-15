'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowLeft } from '@fortawesome/free-solid-svg-icons';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';

export default function ForgotPasswordPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setSent(true);
    }, 1500);
  };

  return (
    <div className="flex flex-col justify-center min-h-screen max-w-sm mx-auto w-full">
      <button 
        onClick={() => router.back()} 
        className="absolute top-8 left-6 text-white"
      >
        <FontAwesomeIcon icon={faArrowLeft} className="w-5 h-5" />
      </button>

      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Reset password</h1>
        <p className="text-gray-400">Enter your email and we'll send you a link to reset it.</p>
      </div>

      {sent ? (
        <div className="bg-surface border border-border p-6 rounded-2xl text-center">
          <p className="text-white mb-2">Link sent!</p>
          <p className="text-sm text-gray-400">Check your inbox for instructions.</p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input 
            label="Email" 
            type="email" 
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <Button type="submit" isLoading={loading}>
            Send reset link
          </Button>
        </form>
      )}
    </div>
  );
}

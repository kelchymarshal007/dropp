'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { apiFetch } from '@/lib/api';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { AuthProvider } from '@/components/AuthProvider';
import { GoogleLogin } from '@react-oauth/google';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleGoogleLogin = async (credentialResponse: any) => {
    setLoading(true);
    setError('');
    try {
      const data = await apiFetch('/auth/google', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ credential: credentialResponse.credential })
      });
      localStorage.setItem('dropp_token', data.access_token);
      localStorage.setItem('dropp_user_id', data.user_id);
      router.push('/reels');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const data = await apiFetch('/auth/login/email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      localStorage.setItem('dropp_token', data.access_token);
      localStorage.setItem('dropp_user_id', data.user_id);
      router.push('/reels');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthProvider>
      <div className="flex flex-col justify-center min-h-screen max-w-sm mx-auto w-full p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Welcome back</h1>
          <p className="text-gray-400">Log in to continue to Dropp</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-4">
          <Input label="Email" type="email" placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <Input label="Password" type="password" placeholder="••••••••" value={password} onChange={(e) => setPassword(e.target.value)} required />
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <Button type="submit" isLoading={loading}>Log in</Button>
        </form>

        <div className="mt-6 flex flex-col items-center">
          <div className="w-full flex items-center gap-4 my-4">
            <div className="flex-1 h-px bg-border"></div>
            <span className="text-gray-500 text-xs">OR</span>
            <div className="flex-1 h-px bg-border"></div>
          </div>
          <GoogleLogin
            onSuccess={handleGoogleLogin}
            onError={() => setError('Google Sign In was unsuccessful')}
            theme="filled_black"
            shape="pill"
            width="300"
          />
        </div>

        <p className="text-center text-gray-400 mt-6 text-sm">
          Don't have an account? <Link href="/signup" className="text-white font-semibold">Sign up</Link>
        </p>
      </div>
    </AuthProvider>
  );
}

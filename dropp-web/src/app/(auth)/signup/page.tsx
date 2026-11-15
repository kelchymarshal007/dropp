'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { apiFetch } from '@/lib/api';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';

export default function SignupPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSeller, setIsSeller] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const data = await apiFetch('/auth/signup/email', { 
        method: 'POST', 
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, is_seller: isSeller }) 
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
    <div className="flex flex-col justify-center min-h-screen max-w-sm mx-auto w-full p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Create account</h1>
        <p className="text-gray-400">Join Dropp in seconds</p>
      </div>

      <form onSubmit={handleSignup} className="space-y-4">
        <Input label="Email" type="email" placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <Input label="Password" type="password" placeholder="Min 6 characters" value={password} onChange={(e) => setPassword(e.target.value)} required />
        
        <div className="flex items-center gap-2 py-2">
          <input type="checkbox" id="seller" checked={isSeller} onChange={(e) => setIsSeller(e.target.checked)} className="w-4 h-4 rounded border-gray-600 bg-surface text-dropp-orange focus:ring-dropp-orange" />
          <label htmlFor="seller" className="text-sm text-gray-300">I want to sell on Dropp</label>
        </div>

        {error && <p className="text-red-500 text-sm">{error}</p>}
        <Button type="submit" isLoading={loading}>Create Account</Button>
      </form>

      <p className="text-center text-gray-400 mt-6 text-sm">
        Already have an account? <Link href="/login" className="text-white font-semibold">Log in</Link>
      </p>
    </div>
  );
}

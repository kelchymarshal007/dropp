'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { apiFetch } from '@/lib/api';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { PasswordStrengthMeter } from '@/components/ui/PasswordStrengthMeter';
import { emailSchema, passwordSchema } from '@/lib/validation';
import { AuthProvider } from '@/components/AuthProvider';
import { GoogleLogin } from '@react-oauth/google';

export default function SignupPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSeller, setIsSeller] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');

  const handleGoogleSignup = async (credentialResponse: any) => {
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

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setEmailError('');
    setPasswordError('');
    setError('');

    const emailCheck = emailSchema.safeParse(email);
    if (!emailCheck.success) { setEmailError(emailCheck.error.errors[0].message); return; }

    const passCheck = passwordSchema.safeParse(password);
    if (!passCheck.success) { setPasswordError(passCheck.error.errors[0].message); return; }

    setLoading(true);
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
    <AuthProvider>
      <div className="flex flex-col justify-center min-h-screen max-w-sm mx-auto w-full p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Create account</h1>
          <p className="text-gray-400">Join Dropp in seconds</p>
        </div>

        <form onSubmit={handleSignup} className="space-y-4">
          <Input label="Email" type="email" placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} required error={emailError} />
          <div>
            <Input label="Password" type="password" placeholder="Min 8 characters" value={password} onChange={(e) => setPassword(e.target.value)} required error={passwordError} />
            <PasswordStrengthMeter password={password} />
          </div>

          <div className="flex items-center gap-2 py-2">
            <input type="checkbox" id="seller" checked={isSeller} onChange={(e) => setIsSeller(e.target.checked)} className="w-4 h-4 rounded border-gray-600 bg-surface text-dropp-orange focus:ring-dropp-orange" />
            <label htmlFor="seller" className="text-sm text-gray-300">I want to sell on Dropp</label>
          </div>

          {error && <p className="text-red-500 text-sm">{error}</p>}
          <Button type="submit" isLoading={loading}>Create Account</Button>
        </form>

        <div className="mt-6 flex flex-col items-center">
          <div className="w-full flex items-center gap-4 my-4">
            <div className="flex-1 h-px bg-border"></div>
            <span className="text-gray-500 text-xs">OR</span>
            <div className="flex-1 h-px bg-border"></div>
          </div>
          <GoogleLogin
            onSuccess={handleGoogleSignup}
            onError={() => setError('Google Sign Up was unsuccessful')}
            theme="filled_black"
            shape="pill"
            width="300"
          />
        </div>

        <p className="text-center text-gray-400 mt-6 text-sm">
          Already have an account? <Link href="/login" className="text-white font-semibold">Log in</Link>
        </p>
      </div>
    </AuthProvider>
  );
}

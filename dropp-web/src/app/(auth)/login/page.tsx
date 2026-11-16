'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { apiFetch } from '@/lib/api';
import { AuthProvider } from '@/components/AuthProvider';
import { GoogleLogin } from '@react-oauth/google';

export default function LoginPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [step, setStep] = useState<'identifier' | 'password' | 'otp'>('identifier');
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [otp, setOtp] = useState('');

  const formatPhone = (raw: string) => raw.startsWith('+') ? raw : `+234${raw.replace(/^0/, '')}`;

  const finish = (data: any) => {
    localStorage.setItem('dropp_token', data.access_token);
    localStorage.setItem('dropp_user_id', data.user_id);
    router.push('/reels');
  };

  const handleNext = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!identifier) return;
    setLoading(true); setError('');
    try {
      if (identifier.includes('@')) {
        setStep('password');
      } else {
        await apiFetch('/auth/login/phone/request', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ phone_e164: formatPhone(identifier) }),
        });
        setStep('otp');
      }
    } catch (e: any) { setError(e.message); } finally { setLoading(false); }
  };

  const handlePasswordLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setError('');
    try {
      const data = await apiFetch('/auth/login/email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: identifier, password }),
      });
      finish(data);
    } catch (e: any) { setError(e.message); } finally { setLoading(false); }
  };

  const handleOtpLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setError('');
    try {
      const data = await apiFetch('/auth/login/phone/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone_e164: formatPhone(identifier), otp_code: otp }),
      });
      finish(data);
    } catch (e: any) { setError(e.message); } finally { setLoading(false); }
  };

  const handleGoogle = async (cr: any) => {
    setLoading(true); setError('');
    try {
      const data = await apiFetch('/auth/google', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ credential: cr.credential }),
      });
      finish(data);
    } catch (e: any) { setError(e.message); } finally { setLoading(false); }
  };

  return (
    <AuthProvider>
      <div className="flex items-center justify-center min-h-[100dvh] bg-black px-4 py-6">
        <div className="w-full max-w-[340px] bg-black border border-gray-800 rounded-2xl p-6 relative">
          
          <button onClick={() => router.push('/reels')} className="absolute top-4 left-4 text-white hover:bg-gray-900 p-2 rounded-full transition">
            <svg viewBox="0 0 24 24" className="w-5 h-5 fill-current"><path d="M13.414 12l5.793-5.793c.39-.39.39-1.023 0-1.414s-1.023-.39-1.414 0L12 10.586 6.207 4.793c-.39-.39-1.023-.39-1.414 0s-.39 1.023 0 1.414L10.586 12l-5.793 5.793c-.39.39-.39 1.023 0 1.414.195.195.45.293.707.293s.512-.098.707-.293L12 13.414l5.793 5.793c.195.195.45.293.707.293s.512-.098.707-.293c.39-.39.39-1.023 0-1.414L13.414 12z"></path></svg>
          </button>

          <div className="flex justify-center mb-4 mt-2">
            <h1 style={{ fontFamily: 'var(--font-coiny)' }} className="text-3xl text-white">Dropp</h1>
          </div>

          <h2 className="text-xl font-bold mb-5 text-center text-white">
            {step === 'identifier' ? 'Log in to Dropp' : step === 'password' ? 'Enter your password' : 'Enter code'}
          </h2>

          {step === 'identifier' && (
            <div className="space-y-3">
              <div className="flex justify-center [&>div]:w-full [&>div>div]:w-full [&_iframe]:w-full scale-90 origin-top mb-[-10px]">
                <GoogleLogin onSuccess={handleGoogle} onError={() => setError('Google Sign In failed')} theme="outline" shape="pill" width="100%" />
              </div>
              
              <button type="button" className="w-full flex items-center justify-center gap-2 py-2 bg-white text-black rounded-full font-semibold text-sm hover:bg-gray-200 transition">
                <svg viewBox="0 0 384 512" className="w-4 h-4 fill-current"><path d="M318.7 268.7c-.2-36.7 16.4-64.4 50-84.8-18.8-26.9-47.2-41.7-84.7-44.6-35.5-2.8-74.3 20.7-88.5 20.7-15 0-49.4-19.7-76.4-19.7C63.3 141.2 4 184.8 4 273.5q0 39.3 14.4 81.2c12.8 36.7 59 126.7 107.2 125.2 25.2-.6 43-17.9 75.8-17.9 31.8 0 48.3 17.9 76.4 17.9 48.6-.7 90.4-82.5 102.6-119.3-65.2-30.7-61.7-90-61.7-91.9zm-56.6-164.2c27.3-32.4 24.8-61.9 24-72.5-24.1 1.4-52 16.4-67.9 34.9-17.5 19.8-27.8 44.3-25.6 71.9 26.1 2 49.9-11.4 69.5-34.3z"/></svg>
                Sign in with Apple
              </button>

              <div className="flex items-center gap-2 my-2">
                <div className="flex-1 h-px bg-gray-800"></div><span className="text-gray-500 text-xs">or</span><div className="flex-1 h-px bg-gray-800"></div>
              </div>

              <form onSubmit={handleNext} className="space-y-3">
                <input type="text" placeholder="Phone, email, or username" value={identifier} onChange={(e) => setIdentifier(e.target.value)} className="w-full bg-black border border-gray-700 rounded-md px-3 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-dropp-orange transition" required />
                {error && <p className="text-red-500 text-xs text-center">{error}</p>}
                <button type="submit" disabled={loading || !identifier} className="w-full py-2 bg-white text-black rounded-full font-bold text-sm hover:bg-gray-200 transition disabled:opacity-50">Next</button>
              </form>

              <button type="button" className="w-full py-2 bg-black text-white border border-gray-700 rounded-full font-bold text-sm hover:bg-gray-900 transition mt-2">Forgot password?</button>
            </div>
          )}

          {step === 'password' && (
            <form onSubmit={handlePasswordLogin} className="space-y-3">
              <p className="text-gray-500 text-xs mb-1 text-center">Logging in as <span className="text-white">{identifier}</span></p>
              <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full bg-black border border-gray-700 rounded-md px-3 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-dropp-orange transition" required />
              {error && <p className="text-red-500 text-xs text-center">{error}</p>}
              <button type="submit" disabled={loading} className="w-full py-2 bg-white text-black rounded-full font-bold text-sm hover:bg-gray-200 transition disabled:opacity-50">Log in</button>
              <button type="button" onClick={() => setStep('identifier')} className="w-full text-xs text-gray-400 hover:underline mt-2">Use a different account</button>
            </form>
          )}

          {step === 'otp' && (
            <form onSubmit={handleOtpLogin} className="space-y-3">
              <p className="text-gray-500 text-xs mb-1 text-center">Code sent to {formatPhone(identifier)}</p>
              <input type="text" maxLength={6} placeholder="------" value={otp} onChange={(e) => setOtp(e.target.value)} className="w-full bg-black border border-gray-700 rounded-md px-3 py-2.5 text-white placeholder-gray-500 text-center tracking-[0.5em] text-lg font-mono focus:outline-none focus:border-dropp-orange transition" required />
              {error && <p className="text-red-500 text-xs text-center">{error}</p>}
              <button type="submit" disabled={loading} className="w-full py-2 bg-white text-black rounded-full font-bold text-sm hover:bg-gray-200 transition disabled:opacity-50">Verify & Log in</button>
              <button type="button" onClick={() => setStep('identifier')} className="w-full text-xs text-gray-400 hover:underline mt-2">Use a different account</button>
            </form>
          )}

          <p className="text-center text-gray-500 mt-5 text-xs">Don't have an account? <Link href="/signup" className="text-blue-500 hover:underline">Sign up</Link></p>
        </div>
      </div>
    </AuthProvider>
  );
}

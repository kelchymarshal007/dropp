'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { apiFetch } from '@/lib/api';
import { PasswordStrengthMeter } from '@/components/ui/PasswordStrengthMeter';
import { emailSchema, passwordSchema } from '@/lib/validation';
import { AuthProvider } from '@/components/AuthProvider';
import { GoogleLogin } from '@react-oauth/google';

type Step = 'identity' | 'security' | 'verify-email';

export default function SignupPage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>('identity');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [isSeller, setIsSeller] = useState(false);
  const [emailOtp, setEmailOtp] = useState('');

  const [googlePhoneModal, setGooglePhoneModal] = useState(false);
  const [googleUserId, setGoogleUserId] = useState('');
  const [googlePhone, setGooglePhone] = useState('');
  const [googleOtp, setGoogleOtp] = useState('');
  const [googlePhoneStep, setGooglePhoneStep] = useState<'request' | 'verify'>('request');

  const formatPhone = (raw: string) => raw.startsWith('+') ? raw : `+234${raw.replace(/^0/, '')}`;

  const finish = (data: any) => {
    localStorage.setItem('dropp_token', data.access_token);
    localStorage.setItem('dropp_user_id', data.user_id);
    router.push('/reels');
  };

  const handleStep1 = (e: React.FormEvent) => {
    e.preventDefault();
    const ec = emailSchema.safeParse(email);
    if (!ec.success) { setError(ec.error.errors[0].message); return; }
    if (!firstName || !lastName) { setError('Please enter your full name'); return; }
    setError('');
    setStep('security');
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    const pc = passwordSchema.safeParse(password);
    if (!pc.success) { setError(pc.error.errors[0].message); return; }
    if (!phone) { setError('Please enter your phone number'); return; }

    setLoading(true);
    try {
      await apiFetch('/auth/signup/email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, first_name: firstName, last_name: lastName, phone_e164: formatPhone(phone), is_seller: isSeller }),
      });
      setStep('verify-email');
    } catch (e: any) { setError(e.message); } finally { setLoading(false); }
  };

  const handleVerifyEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setError('');
    try {
      const data = await apiFetch('/auth/signup/verify-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, otp_code: emailOtp }),
      });
      finish(data);
    } catch (e: any) { setError(e.message); } finally { setLoading(false); }
  };

  const handleGoogleSignup = async (cr: any) => {
    setLoading(true); setError('');
    try {
      const data = await apiFetch('/auth/google', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ credential: cr.credential }),
      });
      localStorage.setItem('dropp_token', data.access_token);
      localStorage.setItem('dropp_user_id', data.user_id);
      if (data.phone_missing) {
        setGoogleUserId(data.user_id);
        setGooglePhoneModal(true);
      } else {
        router.push('/reels');
      }
    } catch (e: any) { setError(e.message); } finally { setLoading(false); }
  };

  const handleGooglePhoneRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setError('');
    try {
      await apiFetch('/auth/google/phone/request', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone_e164: formatPhone(googlePhone) }),
      });
      setGooglePhoneStep('verify');
    } catch (e: any) { setError(e.message); } finally { setLoading(false); }
  };

  const handleGooglePhoneVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setError('');
    try {
      await apiFetch('/auth/google/phone/verify', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: googleUserId, phone_e164: formatPhone(googlePhone), otp_code: googleOtp }),
      });
      setGooglePhoneModal(false);
      router.push('/reels');
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

          {error && (
            <div className="bg-red-500/10 border border-red-500/50 text-red-500 text-xs p-2 rounded-md mb-4 text-center">
              {error}
            </div>
          )}

          {step === 'identity' && (
            <>
              <h2 className="text-xl font-bold mb-5 text-white text-center">Create account</h2>
              <div className="space-y-3 mb-5">
                <div className="flex justify-center [&>div]:w-full [&>div>div]:w-full [&_iframe]:w-full scale-90 origin-top mb-[-10px]">
                  <GoogleLogin onSuccess={handleGoogleSignup} onError={() => setError('Google Sign Up failed')} theme="outline" shape="pill" width="100%" />
                </div>
                <button type="button" className="w-full flex items-center justify-center gap-2 py-2 bg-white text-black rounded-full font-semibold text-sm hover:bg-gray-200 transition">
                  <svg viewBox="0 0 384 512" className="w-4 h-4 fill-current"><path d="M318.7 268.7c-.2-36.7 16.4-64.4 50-84.8-18.8-26.9-47.2-41.7-84.7-44.6-35.5-2.8-74.3 20.7-88.5 20.7-15 0-49.4-19.7-76.4-19.7C63.3 141.2 4 184.8 4 273.5q0 39.3 14.4 81.2c12.8 36.7 59 126.7 107.2 125.2 25.2-.6 43-17.9 75.8-17.9 31.8 0 48.3 17.9 76.4 17.9 48.6-.7 90.4-82.5 102.6-119.3-65.2-30.7-61.7-90-61.7-91.9zm-56.6-164.2c27.3-32.4 24.8-61.9 24-72.5-24.1 1.4-52 16.4-67.9 34.9-17.5 19.8-27.8 44.3-25.6 71.9 26.1 2 49.9-11.4 69.5-34.3z"/></svg>
                  Sign up with Apple
                </button>
              </div>

              <div className="flex items-center gap-2 mb-4"><div className="flex-1 h-px bg-gray-800"></div><span className="text-gray-500 text-xs">or</span><div className="flex-1 h-px bg-gray-800"></div></div>

              <form onSubmit={handleStep1} className="space-y-3">
                <div className="flex gap-2">
                  <input type="text" placeholder="First name" value={firstName} onChange={e => setFirstName(e.target.value)} className="w-1/2 bg-black border border-gray-700 rounded-md px-2 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-dropp-orange transition" required />
                  <input type="text" placeholder="Last name" value={lastName} onChange={e => setLastName(e.target.value)} className="w-1/2 bg-black border border-gray-700 rounded-md px-2 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-dropp-orange transition" required />
                </div>
                <input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} className="w-full bg-black border border-gray-700 rounded-md px-3 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-dropp-orange transition" required />
                <button type="submit" className="w-full py-2 bg-white text-black rounded-full font-bold text-sm hover:bg-gray-200 transition mt-2">Next</button>
              </form>
            </>
          )}

          {step === 'security' && (
            <form onSubmit={handleSignup} className="space-y-3">
              <h2 className="text-xl font-bold mb-2 text-white text-center">Secure account</h2>
              <p className="text-gray-500 text-xs text-center mb-4">Setting up for {email}</p>
              
              <input type="tel" placeholder="Phone (e.g. 08012345678)" value={phone} onChange={e => setPhone(e.target.value)} className="w-full bg-black border border-gray-700 rounded-md px-3 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-dropp-orange transition" required />
              <div>
                <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} className="w-full bg-black border border-gray-700 rounded-md px-3 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-dropp-orange transition" required />
                <PasswordStrengthMeter password={password} />
              </div>
              <div className="flex items-center gap-2 py-1">
                <input id="seller" type="checkbox" checked={isSeller} onChange={e => setIsSeller(e.target.checked)} className="w-4 h-4 rounded border-gray-600 bg-black text-dropp-orange focus:ring-dropp-orange" />
                <label htmlFor="seller" className="text-xs text-gray-300">I want to sell on Dropp</label>
              </div>
              
              <button type="submit" disabled={loading} className="w-full py-2 bg-white text-black rounded-full font-bold text-sm hover:bg-gray-200 transition mt-2 disabled:opacity-50">
                {loading ? '...' : 'Create account'}
              </button>
              
              <button type="button" onClick={() => setStep('identity')} className="w-full text-xs text-gray-400 hover:underline mt-2">Back</button>
            </form>
          )}

          {step === 'verify-email' && (
            <form onSubmit={handleVerifyEmail} className="space-y-3">
              <h2 className="text-xl font-bold text-white text-center">Verify email</h2>
              <p className="text-gray-500 text-xs text-center">Code sent to {email}</p>
              <input type="text" maxLength={6} value={emailOtp} onChange={e => setEmailOtp(e.target.value)} className="w-full bg-black border border-gray-700 rounded-md px-3 py-2.5 text-white placeholder-gray-500 text-center tracking-[0.5em] text-lg font-mono focus:outline-none focus:border-dropp-orange transition" placeholder="------" required />
              <button type="submit" disabled={loading} className="w-full py-2 bg-white text-black rounded-full font-bold text-sm hover:bg-gray-200 transition mt-2 disabled:opacity-50">Verify & Log in</button>
            </form>
          )}

          {googlePhoneModal && (
            <div className="absolute inset-0 bg-black/95 flex items-center justify-center p-6 rounded-2xl z-50">
              <div className="w-full">
                <h3 className="text-xl font-bold mb-2 text-white text-center">Add your phone</h3>
                <p className="text-gray-500 text-xs mb-4 text-center">We need a phone number on your Dropp profile.</p>
                {googlePhoneStep === 'request' ? (
                  <form onSubmit={handleGooglePhoneRequest} className="space-y-3">
                    <input type="tel" placeholder="Phone number" value={googlePhone} onChange={e => setGooglePhone(e.target.value)} className="w-full bg-black border border-gray-700 rounded-md px-3 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-dropp-orange transition" required />
                    <button type="submit" disabled={loading} className="w-full py-2 bg-white text-black rounded-full font-bold text-sm hover:bg-gray-200 transition disabled:opacity-50">Send OTP</button>
                    <button type="button" onClick={() => router.push('/reels')} className="w-full py-2 bg-black text-gray-400 border border-gray-700 rounded-full font-bold text-sm hover:bg-gray-900 transition mt-2">Skip for now</button>
                  </form>
                ) : (
                  <form onSubmit={handleGooglePhoneVerify} className="space-y-3">
                    <input type="text" maxLength={6} placeholder="------" value={googleOtp} onChange={e => setGoogleOtp(e.target.value)} className="w-full bg-black border border-gray-700 rounded-md px-3 py-2.5 text-white placeholder-gray-500 text-center tracking-[0.5em] text-lg font-mono focus:outline-none focus:border-dropp-orange transition" required />
                    <button type="submit" disabled={loading} className="w-full py-2 bg-white text-black rounded-full font-bold text-sm hover:bg-gray-200 transition disabled:opacity-50">Verify</button>
                    <button type="button" onClick={() => router.push('/reels')} className="w-full py-2 bg-black text-gray-400 border border-gray-700 rounded-full font-bold text-sm hover:bg-gray-900 transition mt-2">Skip for now</button>
                  </form>
                )}
              </div>
            </div>
          )}

          {step !== 'verify-email' && (
            <p className="text-center text-gray-500 mt-5 text-xs">Already have an account? <Link href="/login" className="text-blue-500 hover:underline">Log in</Link></p>
          )}
        </div>
      </div>
    </AuthProvider>
  );
}

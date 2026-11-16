'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { apiFetch } from '@/lib/api';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowLeft } from '@fortawesome/free-solid-svg-icons';

export default function PhoneLoginPage() {
  const router = useRouter();
  const [step, setStep] = useState<'phone' | 'otp'>('phone');
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleRequestOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      // Assuming Nigeria for now, prepend +234 if no country code
      const formattedPhone = phone.startsWith('+') ? phone : `+234${phone.replace(/^0/, '')}`;
      await apiFetch('/auth/otp/request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone_e164: formattedPhone })
      });
      setPhone(formattedPhone);
      setStep('otp');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const data = await apiFetch('/auth/otp/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone_e164: phone, otp_code: otp })
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
      <button onClick={() => router.back()} className="absolute top-8 left-6 text-white">
        <FontAwesomeIcon icon={faArrowLeft} className="w-5 h-5" />
      </button>

      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">
          {step === 'phone' ? 'Welcome to Dropp' : 'Enter Code'}
        </h1>
        <p className="text-gray-400">
          {step === 'phone' ? 'Enter your phone number to continue' : `We sent a code to ${phone}`}
        </p>
      </div>

      {step === 'phone' ? (
        <form onSubmit={handleRequestOtp} className="space-y-4">
          <Input 
            label="Phone Number" 
            type="tel" 
            placeholder="801 234 5678" 
            value={phone} 
            onChange={(e) => setPhone(e.target.value)} 
            required 
          />
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <Button type="submit" isLoading={loading}>Send Code</Button>
        </form>
      ) : (
        <form onSubmit={handleVerifyOtp} className="space-y-4">
          <Input 
            label="6-Digit Code" 
            type="text" 
            placeholder="123456" 
            maxLength={6}
            value={otp} 
            onChange={(e) => setOtp(e.target.value)} 
            className="text-center text-2xl tracking-[1em] font-mono"
            required 
          />
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <Button type="submit" isLoading={loading}>Verify & Log In</Button>
        </form>
      )}

      <p className="text-center text-gray-400 mt-6 text-sm">
        Use email instead? <Link href="/login" className="text-white font-semibold">Log in</Link>
      </p>
    </div>
  );
}

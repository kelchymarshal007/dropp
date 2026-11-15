'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowLeft } from '@fortawesome/free-solid-svg-icons';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';

export default function VerifyOtpPage() {
  const router = useRouter();
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    // In a real app, this calls the API with the OTP
    setTimeout(() => {
      setLoading(false);
      router.push('/role'); // Go to role selection after verify
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
        <h1 className="text-3xl font-bold text-white mb-2">Check your phone</h1>
        <p className="text-gray-400">We sent a 6-digit code to your phone number.</p>
      </div>

      <form onSubmit={handleVerify} className="space-y-4">
        <Input 
          label="Verification Code" 
          type="text" 
          placeholder="000000"
          maxLength={6}
          value={otp}
          onChange={(e) => setOtp(e.target.value)}
          className="text-center tracking-[1em] text-2xl font-mono"
          required
        />

        <Button type="submit" isLoading={loading}>
          Verify Account
        </Button>
      </form>

      <p className="text-center text-gray-400 mt-6 text-sm">
        Didn't receive it? <button className="text-dropp-orange font-semibold">Resend code</button>
      </p>
    </div>
  );
}

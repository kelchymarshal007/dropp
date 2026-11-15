'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faBagShopping, faStore } from '@fortawesome/free-solid-svg-icons';
import { Button } from '@/components/ui/Button';

export default function RoleSelectionPage() {
  const router = useRouter();
  const [selected, setSelected] = useState<'buyer' | 'seller' | null>(null);
  const [loading, setLoading] = useState(false);

  const handleContinue = () => {
    if (!selected) return;
    setLoading(true);
    // In a real app, this might hit an API to update the user's profile
    setTimeout(() => {
      router.push('/reels');
    }, 1000);
  };

  return (
    <div className="flex flex-col min-h-screen justify-center max-w-sm mx-auto w-full">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">How will you use Dropp?</h1>
        <p className="text-gray-400">You can change this later in settings.</p>
      </div>

      <div className="space-y-4 mb-8">
        {/* Buyer Card */}
        <button 
          onClick={() => setSelected('buyer')}
          className={`w-full flex items-center gap-4 p-5 rounded-2xl border transition-all ${
            selected === 'buyer' ? 'border-dropp-orange bg-dropp-orange/10' : 'border-border bg-surface'
          }`}
        >
          <div className="w-12 h-12 rounded-full bg-black flex items-center justify-center">
            <FontAwesomeIcon icon={faBagShopping} className="text-white w-5 h-5" />
          </div>
          <div className="text-left">
            <h3 className="text-white font-bold text-lg">I'm buying</h3>
            <p className="text-gray-400 text-sm">Find items and pay safely</p>
          </div>
        </button>

        {/* Seller Card */}
        <button 
          onClick={() => setSelected('seller')}
          className={`w-full flex items-center gap-4 p-5 rounded-2xl border transition-all ${
            selected === 'seller' ? 'border-dropp-orange bg-dropp-orange/10' : 'border-border bg-surface'
          }`}
        >
          <div className="w-12 h-12 rounded-full bg-black flex items-center justify-center">
            <FontAwesomeIcon icon={faStore} className="text-white w-5 h-5" />
          </div>
          <div className="text-left">
            <h3 className="text-white font-bold text-lg">I'm selling</h3>
            <p className="text-gray-400 text-sm">List items and get paid</p>
          </div>
        </button>
      </div>

      <Button onClick={handleContinue} disabled={!selected} isLoading={loading}>
        Continue
      </Button>
    </div>
  );
}

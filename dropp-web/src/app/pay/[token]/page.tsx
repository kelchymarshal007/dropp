'use client';
import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { apiFetch } from '@/lib/api';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faLock, faShieldHalved, faArrowLeft } from '@fortawesome/free-solid-svg-icons';

export default function CheckoutPage() {
  const params = useParams();
  const router = useRouter();
  const token = params.token as string;
  
  const [deal, setDeal] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) return;
    apiFetch(`/payments/checkout/${token}`)
      .then(data => { setDeal(data); setLoading(false); })
      .catch(err => { setError(err.message); setLoading(false); });
  }, [token]);

  if (loading) return <div className="h-screen bg-black flex items-center justify-center text-white">Loading checkout...</div>;
  if (error) return (
    <div className="h-screen bg-black flex flex-col items-center justify-center text-white p-6 text-center">
      <p className="text-red-500 font-bold mb-2">Invalid Checkout Link</p>
      <p className="text-gray-400 text-sm mb-4">{error}</p>
      <button onClick={() => router.push('/reels')} className="bg-white text-black px-6 py-2 rounded-full font-semibold">Go Home</button>
    </div>
  );

  return (
    <main className="bg-black min-h-screen text-white flex flex-col">
      <div className="flex items-center gap-4 p-4 border-b border-border">
        <button onClick={() => router.back()} className="text-white">
          <FontAwesomeIcon icon={faArrowLeft} className="w-5 h-5" />
        </button>
        <h1 className="text-lg font-bold">Secure Checkout</h1>
        <div className="ml-auto flex items-center gap-1 text-xs text-green-500">
          <FontAwesomeIcon icon={faLock} className="w-3 h-3" />
          <span>Encrypted</span>
        </div>
      </div>

      <div className="flex-1 p-6 space-y-6 max-w-md mx-auto w-full">
        <div className="bg-surface rounded-2xl p-6 border border-border">
          <div className="flex items-center gap-2 text-sm text-gray-400 mb-4">
            <FontAwesomeIcon icon={faShieldHalved} className="text-dropp-orange" />
            <span>Dropp Escrow Protection</span>
          </div>
          <h2 className="text-2xl font-bold mb-1">{deal.title}</h2>
          <p className="text-gray-400 text-sm mb-4">Delivery: {deal.dispatch_mode}</p>
          
          <div className="border-t border-border pt-4 space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Item Price</span>
              <span>${(deal.final_minor / 100).toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Protection Fee</span>
              <span>${((deal.final_minor * 0.03) / 100).toFixed(2)}</span>
            </div>
            <div className="flex justify-between font-bold text-lg pt-2 border-t border-border">
              <span>Total</span>
              <span className="text-dropp-orange">${((deal.final_minor * 1.03) / 100).toFixed(2)}</span>
            </div>
          </div>
        </div>

        <button className="w-full bg-dropp-orange text-black font-bold py-4 rounded-full hover:bg-dropp-orange/90 transition">
          Pay & Lock in Escrow
        </button>

        <p className="text-center text-xs text-gray-500">
          Your funds are held safely until you confirm delivery.
        </p>
      </div>
    </main>
  );
}

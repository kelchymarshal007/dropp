'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowLeft, faLink } from '@fortawesome/free-solid-svg-icons';

export default function CreateDroppPage() {
  const router = useRouter();
  const [url, setUrl] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Temporary: Redirect to home after creating
    alert('Card creation coming soon!');
    router.push('/reels');
  };

  return (
    <main className="bg-black min-h-screen text-white flex flex-col">
      <div className="flex items-center gap-4 p-4 border-b border-border">
        <Link href="/reels" className="text-white"><FontAwesomeIcon icon={faArrowLeft} className="w-5 h-5" /></Link>
        <h1 className="text-lg font-bold">Create Dropp Card</h1>
      </div>

      <div className="p-6 space-y-6">
        <p className="text-gray-400">Paste a link from Instagram, TikTok, or WhatsApp to create a secure escrow card.</p>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative">
            <FontAwesomeIcon icon={faLink} className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" />
            <input 
              type="url" 
              placeholder="https://instagram.com/p/..." 
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="w-full bg-surface border border-border rounded-xl pl-12 pr-4 py-4 text-white focus:outline-none focus:border-white"
              required
            />
          </div>
          <button type="submit" className="w-full bg-dropp-orange text-black font-bold py-4 rounded-full hover:bg-dropp-orange/90 transition">
            Generate Card
          </button>
        </form>
      </div>
    </main>
  );
}

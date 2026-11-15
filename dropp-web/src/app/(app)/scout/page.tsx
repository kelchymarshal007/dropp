'use client';
import Link from 'next/link';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowLeft, faMagnifyingGlass } from '@fortawesome/free-solid-svg-icons';

export default function ScoutPage() {
  return (
    <main className="bg-black min-h-screen text-white flex flex-col">
      <div className="flex items-center gap-4 p-4 border-b border-border">
        <Link href="/reels" className="text-white">
          <FontAwesomeIcon icon={faArrowLeft} className="w-5 h-5" />
        </Link>
        <h1 className="text-lg font-bold">Dropp Scout</h1>
      </div>

      <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
        <div className="w-20 h-20 bg-dropp-orange/10 rounded-full flex items-center justify-center mb-6">
          <FontAwesomeIcon icon={faMagnifyingGlass} className="w-8 h-8 text-dropp-orange" />
        </div>
        <h2 className="text-2xl font-bold mb-2">Pro Feature</h2>
        <p className="text-gray-400 text-sm max-w-xs mb-6">
          Dropp Scout is coming soon. Post Wanted Requests and let our AI find the best sellers for you.
        </p>
        <Link href="/profile">
          <button className="bg-dropp-orange text-black font-semibold px-6 py-3 rounded-full">
            Upgrade to Pro
          </button>
        </Link>
      </div>
    </main>
  );
}

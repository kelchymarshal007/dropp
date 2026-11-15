'use client';
import { useState } from 'react';
import Link from 'next/link';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowRightArrowLeft, faWallet, faGavel, faGear, faXmark, faBookmark } from '@fortawesome/free-solid-svg-icons';
import { BookmarksModal } from './BookmarksModal';

export function ProfileMenuModal({ isOpen, onClose }: { isOpen: boolean, onClose: () => void }) {
  const [showBookmarks, setShowBookmarks] = useState(false);
  
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4" onClick={onClose}>
      <div className="w-full max-w-sm bg-surface border border-border rounded-3xl p-6" onClick={e => e.stopPropagation()}>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-white">Account Menu</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <FontAwesomeIcon icon={faXmark} className="w-5 h-5" />
          </button>
        </div>
        
        <div className="space-y-3">
          <Link href="/profile/trades" onClick={onClose} className="flex items-center gap-4 p-4 bg-black rounded-2xl border border-border hover:border-gray-600 transition">
            <div className="w-10 h-10 rounded-full bg-surface flex items-center justify-center">
              <FontAwesomeIcon icon={faArrowRightArrowLeft} className="w-4 h-4 text-white" />
            </div>
            <span className="font-semibold text-white">My Trades</span>
          </Link>

          <Link href="/profile/wallet" onClick={onClose} className="flex items-center gap-4 p-4 bg-black rounded-2xl border border-border hover:border-gray-600 transition">
            <div className="w-10 h-10 rounded-full bg-surface flex items-center justify-center">
              <FontAwesomeIcon icon={faWallet} className="w-4 h-4 text-white" />
            </div>
            <span className="font-semibold text-white">Wallet & Payouts</span>
          </Link>

          {/* Bookmarks Button */}
          <button 
            onClick={() => setShowBookmarks(true)} 
            className="w-full flex items-center gap-4 p-4 bg-black rounded-2xl border border-border hover:border-gray-600 transition text-left"
          >
            <div className="w-10 h-10 rounded-full bg-surface flex items-center justify-center">
              <FontAwesomeIcon icon={faBookmark} className="w-4 h-4 text-white" />
            </div>
            <span className="font-semibold text-white">Saved Posts</span>
          </button>

          <Link href="/profile/disputes" onClick={onClose} className="flex items-center gap-4 p-4 bg-black rounded-2xl border border-border hover:border-gray-600 transition">
            <div className="w-10 h-10 rounded-full bg-surface flex items-center justify-center">
              <FontAwesomeIcon icon={faGavel} className="w-4 h-4 text-white" />
            </div>
            <span className="font-semibold text-white">Disputes</span>
          </Link>

          <Link href="/profile/settings" onClick={onClose} className="flex items-center gap-4 p-4 bg-black rounded-2xl border border-border hover:border-gray-600 transition">
            <div className="w-10 h-10 rounded-full bg-surface flex items-center justify-center">
              <FontAwesomeIcon icon={faGear} className="w-4 h-4 text-white" />
            </div>
            <span className="font-semibold text-white">Settings</span>
          </Link>
        </div>
      </div>

      <BookmarksModal isOpen={showBookmarks} onClose={() => setShowBookmarks(false)} />
    </div>
  );
}

'use client';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faArrowRightArrowLeft, 
  faWallet, 
  faGavel, 
  faGear, 
  faXmark, 
  faBookmark,
  faRightFromBracket
} from '@fortawesome/free-solid-svg-icons';
import { BookmarksModal } from './BookmarksModal';
import { useState } from 'react';

export function ProfileMenuModal({ isOpen, onClose }: { isOpen: boolean, onClose: () => void }) {
  const [showBookmarks, setShowBookmarks] = useState(false);
  const router = useRouter();

  if (!isOpen) return null;

  const handleLogout = () => {
    localStorage.removeItem('dropp_token');
    localStorage.removeItem('dropp_user_id');
    onClose();
    router.push('/login');
  };

  const menuItems = [
    { name: 'My Trades', icon: faArrowRightArrowLeft, href: '/profile/trades' },
    { name: 'Wallet & Payouts', icon: faWallet, href: '/profile/wallet' },
    { name: 'Saved Posts', icon: faBookmark, action: () => setShowBookmarks(true) },
    { name: 'Disputes', icon: faGavel, href: '/profile/disputes' },
    { name: 'Settings', icon: faGear, href: '/profile/settings' },
  ];

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4" onClick={onClose}>
      <div className="w-full max-w-sm bg-surface border border-border rounded-3xl p-6" onClick={e => e.stopPropagation()}>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-white">Account Menu</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white"><FontAwesomeIcon icon={faXmark} className="w-5 h-5" /></button>
        </div>
        
        <div className="space-y-3">
          {menuItems.map((item) => {
            if (item.href) {
              return (
                <Link key={item.name} href={item.href} onClick={onClose} className="flex items-center gap-4 p-4 bg-black rounded-2xl border border-border hover:border-gray-600 transition">
                  <div className="w-10 h-10 rounded-full bg-surface flex items-center justify-center">
                    <FontAwesomeIcon icon={item.icon} className="w-4 h-4 text-white" />
                  </div>
                  <span className="font-semibold text-white">{item.name}</span>
                </Link>
              );
            }
            return (
              <button key={item.name} onClick={() => { if (item.action) item.action(); }} className="w-full flex items-center gap-4 p-4 bg-black rounded-2xl border border-border hover:border-gray-600 transition">
                <div className="w-10 h-10 rounded-full bg-surface flex items-center justify-center">
                  <FontAwesomeIcon icon={item.icon} className="w-4 h-4 text-white" />
                </div>
                <span className="font-semibold text-white">{item.name}</span>
              </button>
            );
          })}
        </div>

        {/* Logout Button */}
        <button 
          onClick={handleLogout} 
          className="w-full flex items-center justify-center gap-3 p-4 mt-6 bg-red-500/10 text-red-500 rounded-2xl border border-red-500/20 hover:bg-red-500/20 transition"
        >
          <FontAwesomeIcon icon={faRightFromBracket} className="w-4 h-4" />
          <span className="font-semibold">Log Out</span>
        </button>

        <BookmarksModal isOpen={showBookmarks} onClose={() => setShowBookmarks(false)} />
      </div>
    </div>
  );
}

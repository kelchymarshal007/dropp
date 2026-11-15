'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faXmark } from '@fortawesome/free-solid-svg-icons';
import { apiFetch } from '@/lib/api';

export function FollowListModal({ isOpen, onClose, userId, type }: { isOpen: boolean, onClose: () => void, userId: string, type: 'followers' | 'following' }) {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && userId) {
      setLoading(true);
      apiFetch(`/users/${userId}/${type}`)
        .then(data => { setUsers(data); setLoading(false); })
        .catch(() => setLoading(false));
    }
  }, [isOpen, userId, type]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4" onClick={onClose}>
      <div className="w-full max-w-sm bg-surface border border-border rounded-3xl p-6 h-[60vh] flex flex-col" onClick={e => e.stopPropagation()}>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-white capitalize">{type}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white"><FontAwesomeIcon icon={faXmark} className="w-5 h-5" /></button>
        </div>
        
        <div className="flex-1 overflow-y-auto space-y-3">
          {loading ? <p className="text-center text-gray-500 mt-10">Loading...</p> : users.length === 0 ? <p className="text-center text-gray-500 mt-10">No users yet.</p> : (
            users.map(u => (
              <Link key={u.id} href={`/u/${u.handle.replace('@', '')}`} onClick={onClose} className="flex items-center gap-3 p-2 rounded-xl hover:bg-white/5 transition">
                <div className="w-10 h-10 rounded-full bg-gray-700 flex items-center justify-center font-bold text-white">
                  {u.handle.charAt(1).toUpperCase()}
                </div>
                <span className="text-white font-semibold">{u.handle}</span>
              </Link>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlus, faEye, faHeart, faArrowLeft } from '@fortawesome/free-solid-svg-icons';

export default function MyReelsPage() {
  const [reels, setReels] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('dropp_token');
    fetch('/api/v1/posts/my-reels', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => {
        setReels(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  return (
    <main className="p-6 pb-24 bg-black min-h-screen text-white">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Link href="/profile" className="text-white">
            <FontAwesomeIcon icon={faArrowLeft} className="w-5 h-5" />
          </Link>
          <h1 className="text-2xl font-bold">My Reels</h1>
        </div>
        <Link href="/profile/reels/upload">
          <button className="bg-dropp-orange text-black font-semibold px-4 py-2 rounded-full text-sm flex items-center gap-2">
            <FontAwesomeIcon icon={faPlus} className="w-3 h-3" /> Upload
          </button>
        </Link>
      </div>

      {loading ? (
        <p className="text-center text-gray-500 mt-10">Loading your reels...</p>
      ) : reels.length === 0 ? (
        <div className="text-center mt-20">
          <p className="text-gray-400 mb-4">You haven't uploaded any reels yet.</p>
          <Link href="/profile/reels/upload">
            <button className="bg-white text-black font-semibold px-6 py-3 rounded-full">
              Create your first Reel
            </button>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          {reels.map((reel) => (
            <div key={reel.id} className="bg-surface border border-border rounded-xl overflow-hidden relative aspect-[9/16]">
              <video src={reel.media_url} className="w-full h-full object-cover opacity-70" muted />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent flex flex-col justify-end p-3">
                <p className="text-xs font-bold truncate mb-1">{reel.caption || 'No caption'}</p>
                <p className="text-dropp-orange text-xs font-bold mb-2">
                  ${(reel.price_minor / 100).toFixed(2)}
                </p>
                <div className="flex gap-3 text-[10px] text-gray-300">
                  <span className="flex items-center gap-1"><FontAwesomeIcon icon={faHeart} /> {reel.likes}</span>
                  <span className="flex items-center gap-1"><FontAwesomeIcon icon={faEye} /> {reel.views}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}

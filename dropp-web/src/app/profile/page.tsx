'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlus, faPlay, faBars } from '@fortawesome/free-solid-svg-icons';
import { apiFetch } from '@/lib/api';
import { ProfileMenuModal } from '@/components/ProfileMenuModal';
import { FollowListModal } from '@/components/FollowListModal';

export default function ProfilePage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [reels, setReels] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showMenu, setShowMenu] = useState(false);
  
  // Follow Modal State
  const [followModalType, setFollowModalType] = useState<'followers' | 'following' | null>(null);

  const fetchProfile = () => {
    const token = localStorage.getItem('dropp_token');
    if (!token) { router.push('/login'); return; }
    
    Promise.all([
      apiFetch('/users/me'),
      apiFetch('/posts/my-reels')
    ]).then(([userData, reelsData]) => {
      setUser(userData);
      setReels(Array.isArray(reelsData) ? reelsData : []);
      setLoading(false);
    }).catch(() => setLoading(false));
  };

  useEffect(() => {
    fetchProfile();
    // Real-time counter poller (every 5 seconds)
    const interval = setInterval(fetchProfile, 5000);
    return () => clearInterval(interval);
  }, [router]);

  if (loading) return <div className="h-screen bg-black flex items-center justify-center text-white">Loading...</div>;
  if (!user) return null;

  return (
    <main className="pb-24 bg-black min-h-screen text-white relative">
      <div className="flex justify-between items-center p-4">
        <div />
        <button onClick={() => setShowMenu(true)} className="p-2 text-white"><FontAwesomeIcon icon={faBars} className="w-6 h-6" /></button>
      </div>

      <div className="px-6 flex flex-col items-center text-center">
        <div className="w-24 h-24 rounded-full bg-surface border-2 border-border flex items-center justify-center text-4xl font-bold mb-4">
          {user.handle?.charAt(1).toUpperCase() || 'U'}
        </div>
        <h1 className="text-2xl font-bold">{user.handle || '@user'}</h1>
        <p className="text-gray-400 text-sm mb-4">{user.email}</p>

        <div className="flex justify-center gap-8 mb-6">
          <button onClick={() => setFollowModalType('following')} className="text-center hover:opacity-80">
            <p className="font-bold text-lg">{user.following || 0}</p>
            <p className="text-xs text-gray-500 uppercase tracking-wide">Following</p>
          </button>
          <button onClick={() => setFollowModalType('followers')} className="text-center hover:opacity-80">
            <p className="font-bold text-lg">{user.followers || 0}</p>
            <p className="text-xs text-gray-500 uppercase tracking-wide">Followers</p>
          </button>
          <div className="text-center">
            <p className="font-bold text-lg">{reels.length}</p>
            <p className="text-xs text-gray-500 uppercase tracking-wide">Reels</p>
          </div>
        </div>
      </div>

      <div className="border-t border-border mt-2">
        <div className="flex justify-center border-b border-border mb-1">
          <div className="py-3 px-8 border-b-2 border-white flex items-center gap-2 text-white">
            <FontAwesomeIcon icon={faPlay} className="w-4 h-4" />
            <span className="text-sm font-semibold">My Reels</span>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-[2px]">
          {reels.length === 0 ? (
            <div className="col-span-3 text-center py-12 text-gray-500">No reels yet. Tap + to upload!</div>
          ) : (
            reels.map((reel) => (
              <Link href={`/reels?user=${user.id}&start=${reel.id}`} key={reel.id} className="relative aspect-[9/16] bg-surface block">
                {reel.media_type === 'video' ? (
                  <video src={reel.media_urls?.[0]} className="w-full h-full object-cover opacity-80" muted playsInline />
                ) : (
                  <img src={reel.media_urls?.[0]} className="w-full h-full object-cover opacity-80" alt="" />
                )}
                <div className="absolute bottom-1 left-1 flex items-center gap-1 text-white text-xs font-semibold drop-shadow-md">
                  <FontAwesomeIcon icon={faPlay} className="w-3 h-3" />
                  <span>{reel.likes || 0}</span>
                </div>
              </Link>
            ))
          )}
        </div>
      </div>

      <Link href="/profile/reels/upload">
        <div className="fixed inset-0 pointer-events-none z-[90] flex justify-center">
          <div className="w-full max-w-md relative">
            <div className="pointer-events-auto absolute bottom-24 right-6 w-16 h-16 rounded-full flex items-center justify-center shadow-[0_8px_32px_rgba(0,0,0,0.6)] cursor-pointer hover:scale-105 transition-transform">
              <div className="absolute inset-0 bg-white/10 backdrop-blur-md rounded-full border border-white/20 shadow-inner" />
              <FontAwesomeIcon icon={faPlus} className="w-7 h-7 text-white relative z-10 drop-shadow-lg" />
            </div>
          </div>
        </div>
      </Link>

      <ProfileMenuModal isOpen={showMenu} onClose={() => setShowMenu(false)} />
      <FollowListModal isOpen={!!followModalType} onClose={() => setFollowModalType(null)} userId={user.id} type={followModalType as any} />
    </main>
  );
}

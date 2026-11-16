'use client';
import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowLeft, faPlay } from '@fortawesome/free-solid-svg-icons';
import { apiFetch } from '@/lib/api';
import { FollowListModal } from '@/components/FollowListModal';

export default function PublicProfilePage() {
  const params = useParams();
  const router = useRouter();
  const handle = params.handle as string;
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [followModalType, setFollowModalType] = useState<'followers' | 'following' | null>(null);

  useEffect(() => {
    apiFetch(`/users/profile/${handle}`)
      .then(res => { setData(res); setLoading(false); })
      .catch(() => setLoading(false));
  }, [handle]);

  if (loading) return <div className="h-screen bg-black flex items-center justify-center text-white">Loading...</div>;
  if (!data) return <div className="h-screen bg-black flex items-center justify-center text-white">User not found</div>;

  return (
    <main className="pb-24 bg-black min-h-screen text-white relative">
      <div className="flex items-center p-4">
        <button onClick={() => router.back()} className="text-white mr-4"><FontAwesomeIcon icon={faArrowLeft} className="w-5 h-5" /></button>
        <h1 className="text-lg font-bold">{data.handle}</h1>
      </div>
      
      <div className="flex flex-col items-center mt-4">
        <div className="w-24 h-24 rounded-full bg-surface border-2 border-border flex items-center justify-center text-4xl font-bold mb-4">
          {data.handle.charAt(1).toUpperCase()}
        </div>
        <h2 className="text-2xl font-bold">{data.handle}</h2>
        
        <div className="flex justify-center gap-8 mt-4 mb-6">
          <button onClick={() => setFollowModalType('following')} className="text-center hover:opacity-80">
            <p className="font-bold text-lg">{data.following}</p>
            <p className="text-xs text-gray-500 uppercase">Following</p>
          </button>
          <button onClick={() => setFollowModalType('followers')} className="text-center hover:opacity-80">
            <p className="font-bold text-lg">{data.followers}</p>
            <p className="text-xs text-gray-500 uppercase">Followers</p>
          </button>
          <div className="text-center">
            <p className="font-bold text-lg">{data.posts.length}</p>
            <p className="text-xs text-gray-500 uppercase">Reels</p>
          </div>
        </div>
      </div>

      <div className="border-t border-border mt-2">
        <div className="grid grid-cols-3 gap-[2px]">
          {data.posts.map((reel: any) => (
            <Link href={`/reels?user=${data.id}&start=${reel.id}`} key={reel.id} className="relative aspect-[9/16] bg-surface block">
              {reel.media_type === 'video' ? (
                <video src={reel.media_urls[0]} className="w-full h-full object-cover opacity-80" muted playsInline />
              ) : (
                <img src={reel.media_urls[0]} className="w-full h-full object-cover opacity-80" />
              )}
              <div className="absolute bottom-1 left-1 text-white text-xs font-semibold"><FontAwesomeIcon icon={faPlay} className="w-3 h-3 mr-1" />{reel.likes}</div>
            </Link>
          ))}
        </div>
      </div>

      <FollowListModal isOpen={!!followModalType} onClose={() => setFollowModalType(null)} userId={data.id} type={followModalType as any} />
    </main>
  );
}

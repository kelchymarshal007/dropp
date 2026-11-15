'use client';
import { useState, useEffect, useRef } from 'react';
import { ReelPlayer } from '@/components/ReelPlayer';
import { AuthWallModal } from '@/components/AuthWallModal';
import { CommentModal } from '@/components/CommentModal';
import { apiFetch } from '@/lib/api';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSpinner } from '@fortawesome/free-solid-svg-icons';

const Preloader = ({ url }: { url: string }) => {
  return (
    <video src={url} preload="auto" muted playsInline style={{ display: 'none' }} />
  );
};

const BUFFER_AHEAD = 2;
const BUFFER_BEHIND = 1;
const FETCH_LIMIT = 20;

export default function ReelsPage() {
  const [reels, setReels] = useState<any[]>([]);
  const [activeIndex, setActiveIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [error, setError] = useState<string>('');
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [isGlobalMuted, setIsGlobalMuted] = useState(true);
  const [activeCommentPost, setActiveCommentPost] = useState<string | null>(null);
  
  const containerRef = useRef<HTMLDivElement>(null);
  const socketsRef = useRef<WebSocket[]>([]);

  useEffect(() => {
    fetchBatch(0);
  }, []);

  // Deep Linking: Read URL, calculate index, and scroll mathematically
  useEffect(() => {
    if (reels.length === 0) return;
    
    const params = new URLSearchParams(window.location.search);
    const startId = params.get('start');
    if (!startId) return;

    const index = reels.findIndex((r: any) => r.id === startId);
    if (index !== -1 && containerRef.current) {
      setTimeout(() => {
        if (containerRef.current) {
          // Since every reel is exactly 100vh, we multiply by window height to get the exact pixel position
          containerRef.current.scrollTop = index * window.innerHeight;
          setActiveIndex(index);
        }
      }, 100);
    }
  }, [reels.length]);

  const fetchBatch = async (offset: number) => {
    if (offset === 0) setLoading(true);
    else setLoadingMore(true);

    try {
      const data = await apiFetch(`/feed/?limit=${FETCH_LIMIT}&offset=${offset}`);
      if (Array.isArray(data)) {
        if (data.length < FETCH_LIMIT) setHasMore(false);
        setReels(prev => offset === 0 ? data : [...prev, ...data]);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  useEffect(() => {
    if (reels.length === 0) return;
    socketsRef.current.forEach(ws => ws.close());
    socketsRef.current = [];

    reels.forEach(reel => {
      try {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const ws = new WebSocket(`${protocol}//${window.location.host}/api/v1/feed/ws/${reel.id}`);
        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'like_update' || data.type === 'comment_update') {
              setReels(prev => prev.map(r => 
                r.id === data.post_id ? { ...r, likes: data.likes ?? r.likes, comments: data.comments ?? r.comments } : r
              ));
            }
          } catch (e) {}
        };
        socketsRef.current.push(ws);
      } catch (err) {}
    });

    return () => socketsRef.current.forEach(ws => ws.close());
  }, [reels.length]);

  useEffect(() => {
    if (reels.length === 0) return;

    if (activeIndex >= reels.length - 3 && hasMore && !loadingMore) {
      fetchBatch(reels.length);
    }

    const activeReelId = reels[activeIndex]?.id;
    if (activeReelId) {
      apiFetch(`/feed/${activeReelId}`)
        .then(freshData => {
          setReels(prev => prev.map((r, i) => i === activeIndex ? { ...r, ...freshData } : r));
        })
        .catch(() => {});
    }

    const poller = setInterval(() => {
      if (activeReelId) {
        apiFetch(`/feed/${activeReelId}`)
          .then(freshData => {
            setReels(prev => prev.map((r, i) => {
              if (i === activeIndex && (r.likes !== freshData.likes || r.comments !== freshData.comments || r.is_following !== freshData.is_following)) {
                return { ...r, ...freshData };
              }
              return r;
            }));
          })
          .catch(() => {});
      }
    }, 3000);

    return () => clearInterval(poller);
  }, [activeIndex, reels.length, hasMore, loadingMore]);

  useEffect(() => {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          setActiveIndex(parseInt(entry.target.getAttribute('data-index') || '0'));
        }
      });
    }, { threshold: 0.6 });
    
    document.querySelectorAll('.reel-container').forEach(el => observer.observe(el));
    return () => observer.disconnect();
  }, [reels.length]);

  const handleToggleLike = async (postId: string, currentIsLiked: boolean) => {
    if (!localStorage.getItem('dropp_token')) { setShowAuthModal(true); return; }
    setReels(prev => prev.map(r => r.id === postId ? { ...r, is_liked: !currentIsLiked, likes: currentIsLiked ? r.likes - 1 : r.likes + 1 } : r));
    try {
      const data = await apiFetch(`/feed/${postId}/like`, { method: 'POST' });
      setReels(prev => prev.map(r => r.id === postId ? { ...r, is_liked: data.status === 'liked', likes: data.likes } : r));
    } catch (err) { }
  };

  const handleToggleBookmark = async (postId: string, isBookmarked: boolean) => {
    if (!localStorage.getItem('dropp_token')) { setShowAuthModal(true); return; }
    setReels(prev => prev.map(r => r.id === postId ? { ...r, is_bookmarked: !isBookmarked } : r));
    try {
      await apiFetch(`/feed/${postId}/bookmark`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ item_id: postId, item_type: 'post' }) });
    } catch (err) {
      setReels(prev => prev.map(r => r.id === postId ? { ...r, is_bookmarked: isBookmarked } : r));
    }
  };

  const handleToggleFollow = async (sellerId: string) => {
    if (!localStorage.getItem('dropp_token')) { setShowAuthModal(true); return; }
    setReels(prev => prev.map(r => r.seller_id === sellerId ? { ...r, is_following: !r.is_following } : r));
    try {
      await apiFetch(`/users/${sellerId}/follow`, { method: 'POST' });
    } catch (err) {
      setReels(prev => prev.map(r => r.seller_id === sellerId ? { ...r, is_following: !r.is_following } : r));
    }
  };

  if (loading) return <div className="h-screen bg-black flex items-center justify-center text-white">Loading...</div>;
  if (error) return <div className="h-screen bg-black flex items-center justify-center text-red-500 text-center px-4">{error}</div>;
  if (reels.length === 0) return <div className="h-screen bg-black flex items-center justify-center text-white">No reels found.</div>;

  return (
    <main ref={containerRef} className="h-screen overflow-y-scroll snap-y snap-mandatory bg-black [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
      {reels.map((reel, index) => {
        const isWithinBuffer = index >= activeIndex - BUFFER_BEHIND && index <= activeIndex + BUFFER_AHEAD;
        return (
          <div key={reel.id} id={`reel-${reel.id}`} data-index={index} className="reel-container h-screen w-full snap-start bg-black">
            {isWithinBuffer ? (
              <ReelPlayer
                postId={reel.id} mediaUrls={reel.media_urls} mediaType={reel.media_type}
                sellerId={reel.seller_id} sellerHandle={reel.seller_handle}
                caption={reel.caption} price={`$${(reel.price_minor / 100).toFixed(2)}`}
                likes={reel.likes} comments={reel.comments} shares={reel.shares} 
                isLiked={reel.is_liked} isBookmarked={reel.is_bookmarked} isFollowing={reel.is_following}
                isOwner={reel.seller_id === localStorage.getItem('dropp_user_id')}
                isActive={index === activeIndex} isGlobalMuted={isGlobalMuted}
                onToggleMute={() => setIsGlobalMuted(!isGlobalMuted)}
                onToggleLike={() => handleToggleLike(reel.id, reel.is_liked)}
                onToggleBookmark={() => handleToggleBookmark(reel.id, reel.is_bookmarked)}
                onToggleFollow={() => handleToggleFollow(reel.seller_id)}
                onOpenComments={() => setActiveCommentPost(reel.id)}
                onRequireAuth={() => setShowAuthModal(true)}
                createdAt={reel.created_at}
                shouldPreload={index === activeIndex}
                isNext={index === activeIndex + 1}
              />
            ) : (
              <div className="w-full h-full bg-black flex items-center justify-center">
                <p className="text-gray-700 text-sm">Scroll to load</p>
              </div>
            )}
          </div>
        );
      })}

      {loadingMore && (
        <div className="h-20 w-full flex items-center justify-center text-white snap-start">
          <FontAwesomeIcon icon={faSpinner} className="w-6 h-6 animate-spin text-dropp-orange" />
        </div>
      )}
      {!hasMore && reels.length > 5 && (
        <div className="h-20 w-full flex items-center justify-center text-gray-500 snap-start text-sm">
          You've reached the end of the feed.
        </div>
      )}

      {activeIndex < reels.length - 1 && reels[activeIndex + 1]?.media_type === 'video' && (
        <Preloader url={reels[activeIndex + 1].media_urls[0]} />
      )}
      
      <AuthWallModal isOpen={showAuthModal} />
      <CommentModal 
        isOpen={!!activeCommentPost} 
        onClose={() => setActiveCommentPost(null)}
        postId={activeCommentPost}
        commentCount={reels.find(r => r.id === activeCommentPost)?.comments || 0}
        onCommentAdded={(newCount: number) => {
          setReels(prev => prev.map(r => r.id === activeCommentPost ? { ...r, comments: newCount } : r));
        }}
      />
    </main>
  );
}

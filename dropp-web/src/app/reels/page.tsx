"use client";
import { useState, useEffect, useRef, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSpinner, faXmark } from "@fortawesome/free-solid-svg-icons";
import { ReelPlayer } from "@/components/ReelPlayer";
import { AuthWallModal } from "@/components/AuthWallModal";
import { CommentModal } from "@/components/CommentModal";
import { apiFetch } from "@/lib/api";



const BUFFER_AHEAD = 2;
const BUFFER_BEHIND = 1;
const FETCH_LIMIT = 20;

function ReelsPageContent() {
  const searchParams = useSearchParams();
  const key = searchParams.toString();
  return <ReelsPageCore key={key} />;
}

function ReelsPageCore() {
  const searchParams = useSearchParams();
  const scopeUserId = searchParams.get("user");
  const startReelId = searchParams.get("start");

  const [reels, setReels] = useState<any[]>([]);
  const [activeIndex, setActiveIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [error, setError] = useState<string>("");
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [isGlobalMuted, setIsGlobalMuted] = useState(true);
  const [activeCommentPost, setActiveCommentPost] = useState<string | null>(null);

  const containerRef = useRef<HTMLDivElement>(null);
  const socketsRef = useRef<WebSocket[]>([]);

  const scopeHandle = scopeUserId && reels.length > 0 ? reels[0]?.seller_handle : null;

  const fetchBatch = async (offset: number) => {
    if (offset === 0) setLoading(true);
    else setLoadingMore(true);

    try {
      const endpoint = scopeUserId
        ? `/feed/user/${scopeUserId}?limit=${FETCH_LIMIT}&offset=${offset}`
        : `/feed/?limit=${FETCH_LIMIT}&offset=${offset}`;

      const data = await apiFetch(endpoint);
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
    fetchBatch(0);
  }, [scopeUserId]);

  useEffect(() => {
    if (reels.length === 0 || !startReelId) return;
    const index = reels.findIndex((r: any) => r.id === startReelId);
    if (index !== -1 && containerRef.current) {
      setTimeout(() => {
        if (containerRef.current) {
          containerRef.current.scrollTop = index * window.innerHeight;
          setActiveIndex(index);
        }
      }, 100);
    }
  }, [reels.length, startReelId]);

  useEffect(() => {
    if (reels.length === 0) return;
    socketsRef.current.forEach(ws => ws.close());
    socketsRef.current = [];

    reels.forEach(reel => {
      try {
        const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        const ws = new WebSocket(`${protocol}//${window.location.host}/api/v1/feed/ws/${reel.id}`);
        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === "like_update" || data.type === "comment_update") {
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
        .catch((err) => {
          console.warn("Polling failed for active reel (ignoring):", err.message);
        });
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
          .catch(() => {}); // Silently fail the interval
      }
    }, 10000);

    return () => clearInterval(poller);
  }, [activeIndex, reels.length, hasMore, loadingMore]);

  useEffect(() => {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          setActiveIndex(parseInt(entry.target.getAttribute("data-index") || "0"));
        }
      });
    }, { threshold: 0.6 });
    document.querySelectorAll(".reel-container").forEach(el => observer.observe(el));
    return () => observer.disconnect();
  }, [reels.length]);

  const handleToggleLike = async (postId: string, currentIsLiked: boolean) => {
    if (!localStorage.getItem("dropp_token")) { setShowAuthModal(true); return; }
    setReels(prev => prev.map(r => r.id === postId ? { ...r, is_liked: !currentIsLiked, likes: currentIsLiked ? r.likes - 1 : r.likes + 1 } : r));
    try {
      const data = await apiFetch(`/feed/${postId}/like`, { method: "POST" });
      setReels(prev => prev.map(r => r.id === postId ? { ...r, is_liked: data.status === "liked", likes: data.likes } : r));
    } catch (err) {}
  };

  const handleToggleBookmark = async (postId: string, isBookmarked: boolean) => {
    if (!localStorage.getItem("dropp_token")) { setShowAuthModal(true); return; }
    setReels(prev => prev.map(r => r.id === postId ? { ...r, is_bookmarked: !isBookmarked } : r));
    try {
      await apiFetch(`/feed/${postId}/bookmark`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ item_id: postId, item_type: "post" }) });
    } catch (err) {
      setReels(prev => prev.map(r => r.id === postId ? { ...r, is_bookmarked: isBookmarked } : r));
    }
  };

  const handleToggleFollow = async (sellerId: string) => {
    if (!localStorage.getItem("dropp_token")) { setShowAuthModal(true); return; }
    setReels(prev => prev.map(r => r.seller_id === sellerId ? { ...r, is_following: !r.is_following } : r));
    try {
      await apiFetch(`/users/${sellerId}/follow`, { method: "POST" });
    } catch (err) {
      setReels(prev => prev.map(r => r.seller_id === sellerId ? { ...r, is_following: !r.is_following } : r));
    }
  };

  const exitScope = () => {
    window.location.href = "/reels";
  };

  if (loading) return <div className="h-screen bg-black flex items-center justify-center text-white">Loading...</div>;
  if (error) return <div className="h-screen bg-black flex items-center justify-center text-red-500 text-center px-4">{error}</div>;
  if (reels.length === 0) return (
    <div className="h-screen bg-black flex flex-col items-center justify-center text-white gap-4">
      <p className="text-gray-400">No reels found.</p>
      {scopeUserId && (
        <button onClick={exitScope} className="bg-dropp-orange text-black px-6 py-2 rounded-full font-semibold">
          Explore All Reels
        </button>
      )}
    </div>
  );

  return (
    <main ref={containerRef} className="h-screen overflow-y-scroll snap-y snap-mandatory bg-black [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
      {scopeUserId && scopeHandle && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-40 bg-black/70 backdrop-blur-md px-4 py-2 rounded-full flex items-center gap-2 border border-white/20">
          <span className="text-white text-xs font-semibold">{scopeHandle}&apos;s Reels</span>
          <button onClick={exitScope} className="text-white/70 hover:text-white">
            <FontAwesomeIcon icon={faXmark} className="w-3 h-3" />
          </button>
        </div>
      )}

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
                isOwner={reel.seller_id === localStorage.getItem("dropp_user_id")}
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
          You&apos;ve reached the end {scopeUserId ? "of this user's reels" : "of the feed"}.
        </div>
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

export default function ReelsPage() {
  return (
    <Suspense fallback={<div className="h-screen bg-black flex items-center justify-center text-white">Loading...</div>}>
      <ReelsPageContent />
    </Suspense>
  );
}

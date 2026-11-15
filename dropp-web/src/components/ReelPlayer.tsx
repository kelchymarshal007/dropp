'use client';
import { useState, useRef, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faHeart, faComment, faShare, faPlus, faBookmark, faCheck,
  faVolumeHigh, faVolumeMute, faPlay, faSpinner
} from '@fortawesome/free-solid-svg-icons';

export function ReelPlayer({ 
  postId, mediaUrls, mediaType, sellerHandle, caption, price, likes, comments, shares, isLiked, isBookmarked,
  isOwner, isFollowing, isActive, isGlobalMuted, onToggleMute, onToggleLike, onToggleBookmark, onToggleFollow, onOpenComments, onRequireAuth, createdAt, shouldPreload, isNext
}: any) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPaused, setIsPaused] = useState(false);
  const [progress, setProgress] = useState(0);
  const [showHeartAnim, setShowHeartAnim] = useState(false);
  const [carouselIndex, setCarouselIndex] = useState(0);
  
  const [imageLoaded, setImageLoaded] = useState(false);
  const [videoLoaded, setVideoLoaded] = useState(false);
  const [showForcePlay, setShowForcePlay] = useState(false);
  const uploadDate = createdAt ? new Date(createdAt).toLocaleDateString('en-GB') : '';
  
  const lastTap = useRef<number>(0);
  const tapTimeout = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // If video takes more than 5 seconds to load, show the Force Play button
    let timer: NodeJS.Timeout;
    if (isActive && !videoLoaded) {
      timer = setTimeout(() => setShowForcePlay(true), 5000);
    } else {
      setShowForcePlay(false);
    }
    return () => clearTimeout(timer);
  }, [isActive, videoLoaded]);

  useEffect(() => {
    if (mediaType === 'video' && videoRef.current) {
      videoRef.current.muted = isGlobalMuted;
      if (isActive) {
        videoRef.current.play().catch(() => { if (videoRef.current) videoRef.current.muted = true; });
        setIsPaused(false);
      } else {
        videoRef.current.pause();
        videoRef.current.currentTime = 0; 
        setIsPaused(true);
      }
    }
  }, [isActive, isGlobalMuted, mediaType]);

  const handleTap = (e: React.MouseEvent) => {
    if (mediaType !== 'video') return;
    const now = Date.now();
    if (now - lastTap.current < 300) {
      if (tapTimeout.current) clearTimeout(tapTimeout.current);
      setShowHeartAnim(true);
      setTimeout(() => setShowHeartAnim(false), 800);
      if (!isLiked) onToggleLike();
    } else {
      tapTimeout.current = setTimeout(() => {
        if (!videoRef.current) return;
        if (isPaused) { videoRef.current.play(); setIsPaused(false); }
        else { videoRef.current.pause(); setIsPaused(true); }
      }, 300);
    }
    lastTap.current = now;
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      const p = (videoRef.current.currentTime / videoRef.current.duration) * 100;
      setProgress(p);
    }
  };

  const nextImage = (e: React.MouseEvent) => { 
    e.stopPropagation(); 
    setImageLoaded(false);
    setCarouselIndex(prev => Math.min(mediaUrls.length - 1, prev + 1)); 
  };
  const prevImage = (e: React.MouseEvent) => { 
    e.stopPropagation(); 
    setImageLoaded(false);
    setCarouselIndex(prev => Math.max(0, prev - 1)); 
  };

  return (
    <div className="relative h-[100dvh] w-full bg-black overflow-hidden pb-safe">
      {mediaType === 'carousel' ? (
        <div className="relative w-full h-full">
          {!imageLoaded && (
            <div className="absolute inset-0 flex items-center justify-center bg-surface z-0">
              <FontAwesomeIcon icon={faSpinner} className="text-white/50 w-8 h-8 animate-spin" />
            </div>
          )}
          
          <img 
            src={mediaUrls[carouselIndex]} 
            className={`w-full h-full object-cover transition-opacity duration-300 ${imageLoaded ? 'opacity-100' : 'opacity-0'}`} 
            alt="Carousel" 
            onLoad={() => setImageLoaded(true)}
          />
          
          <div className="absolute top-16 left-0 right-0 flex justify-center gap-1 z-20 pointer-events-none">
            {mediaUrls.map((_: any, i: number) => (
              <div key={i} className={`h-1 rounded-full transition-all ${i === carouselIndex ? 'bg-white w-4' : 'bg-white/40 w-1.5'}`} />
            ))}
          </div>
          <div className="absolute inset-y-0 left-0 w-1/3 z-10" onClick={prevImage} />
          <div className="absolute inset-y-0 right-0 w-1/3 z-10" onClick={nextImage} />
        </div>
      ) : (
        <div onClick={handleTap} className="absolute inset-0 cursor-pointer overflow-hidden">
          {/* Skeleton / Blur-up Spinner */}
          {!videoLoaded && isActive && (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-black z-20">
              <FontAwesomeIcon icon={faSpinner} className="text-dropp-orange w-10 h-10 animate-spin mb-4" />
              
              {/* Force Play Fallback */}
              {showForcePlay && (
                <button 
                  onClick={(e) => { e.stopPropagation(); videoRef.current?.load(); videoRef.current?.play(); }}
                  className="bg-white/20 backdrop-blur-md text-white px-6 py-2 rounded-full text-sm font-semibold border border-white/20"
                >
                  Tap to Load Video
                </button>
              )}
            </div>
          )}
          
          <video 
            ref={videoRef} 
            src={mediaUrls[0]} 
            className={`w-full h-full object-cover transition-all duration-700 ${videoLoaded ? 'opacity-100 blur-0' : 'opacity-50 blur-md'}`} 
            loop 
            playsInline 
            preload={shouldPreload ? "auto" : (isNext ? "metadata" : "none")} 
            onTimeUpdate={handleTimeUpdate}
            onCanPlay={() => setVideoLoaded(true)}
            onError={() => setVideoLoaded(true)} // Fallback if video fails to load
          />

          {isPaused && isActive && videoLoaded && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/20">
              <div className="w-20 h-20 bg-black/50 rounded-full flex items-center justify-center backdrop-blur-sm">
                <FontAwesomeIcon icon={faPlay} className="w-8 h-8 text-white ml-2" />
              </div>
            </div>
          )}
        </div>
      )}

      <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent pointer-events-none" />
      <div className="absolute top-0 inset-x-0 h-32 bg-gradient-to-b from-black/60 to-transparent pointer-events-none" />

      {showHeartAnim && (
        <div className="absolute inset-0 flex items-center justify-center z-40 pointer-events-none">
          <FontAwesomeIcon icon={faHeart} className="w-32 h-32 text-red-500 animate-[ping_0.5s_ease-out_forwards] drop-shadow-xl opacity-90" />
        </div>
      )}

      {mediaType === 'video' && (
        <div className="absolute bottom-0 w-full h-1 bg-white/20">
          <div className="h-full bg-white transition-all duration-100 ease-linear" style={{ width: `${progress}%` }} />
        </div>
      )}

      {/* RIGHT ACTION STACK - Everything grouped tightly together */}
      <div className="absolute bottom-24 right-3 flex flex-col items-center space-y-4 z-10">
        
        {/* Mute Button */}
        {mediaType === 'video' && (
          <button onClick={(e) => { e.stopPropagation(); onToggleMute(); }} className="text-white p-2 bg-black/30 rounded-full backdrop-blur-sm">
            <FontAwesomeIcon icon={isGlobalMuted ? faVolumeMute : faVolumeHigh} className="w-4 h-4" />
          </button>
        )}

        {/* Follow Button - Hidden for owner */}
        {!isOwner && (
          <button 
            onClick={(e) => { e.stopPropagation(); onToggleFollow(); }} 
            className={`w-10 h-10 rounded-full flex items-center justify-center shadow-lg mb-1 transition-all ${isFollowing ? 'bg-white/20 backdrop-blur-sm' : 'bg-red-500'}`}
          >
            <FontAwesomeIcon icon={isFollowing ? faCheck : faPlus} className="text-white w-5 h-5" />
          </button>
        )}

        <button onClick={(e) => { e.stopPropagation(); onToggleLike(); }} className="flex flex-col items-center space-y-1">
          <div className={`p-2.5 rounded-full backdrop-blur-sm ${isLiked ? 'bg-red-500/20' : 'bg-black/30'}`}>
            <FontAwesomeIcon icon={faHeart} className={`w-6 h-6 ${isLiked ? 'text-red-500' : 'text-white'}`} />
          </div>
          <span className="text-white text-xs font-medium">{likes}</span>
        </button>
        
        <button onClick={(e) => { e.stopPropagation(); onOpenComments(); }} className="flex flex-col items-center space-y-1">
          <div className="p-2.5 rounded-full backdrop-blur-sm bg-black/30">
            <FontAwesomeIcon icon={faComment} className="w-6 h-6 text-white" />
          </div>
          <span className="text-white text-xs font-medium">{comments}</span>
        </button>
        
        <button onClick={(e) => { e.stopPropagation(); onToggleBookmark(); }} className="flex flex-col items-center space-y-1">
          <div className="p-2.5 rounded-full backdrop-blur-sm bg-black/30">
            <FontAwesomeIcon icon={faBookmark} className={`w-6 h-6 ${isBookmarked ? 'text-dropp-orange' : 'text-white'}`} />
          </div>
          <span className="text-white text-xs font-medium">Save</span>
        </button>

        <button onClick={(e) => e.stopPropagation()} className="flex flex-col items-center space-y-1">
          <div className="p-2.5 rounded-full backdrop-blur-sm bg-black/30">
            <FontAwesomeIcon icon={faShare} className="w-6 h-6 text-white" />
          </div>
          <span className="text-white text-xs font-medium">{shares}</span>
        </button>
      </div>

            {/* BOTTOM LEFT INFO */}
      <div className="absolute bottom-24 left-4 right-20 z-20">
        {/* Clickable Username - Fully independent element */}
        <button 
          onClick={(e) => { 
            e.stopPropagation(); 
            window.location.href = isOwner ? '/profile' : `/u/${sellerHandle?.replace('@', '')}`;
          }}
          className="flex items-center space-x-2 mb-2 cursor-pointer hover:opacity-80 transition-opacity"
        >
          <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center text-xs font-bold border border-white/20">
            {sellerHandle?.charAt(1).toUpperCase()}
          </div>
          <span className="text-white font-semibold text-sm">{sellerHandle}</span>
        </button>
        
        {/* Non-clickable text that passes through to video for play/pause */}
        <div className="pointer-events-none">
          <p className="text-white text-sm mb-1 line-clamp-2">{caption}</p>
          <div className="flex flex-col">
            <p className="text-dropp-orange font-bold text-base">{price}</p>
            {uploadDate && <span className="text-gray-400 text-[10px]">{uploadDate}</span>}
          </div>
        </div>
      </div>

      {/* DROPP BUTTON - Narrower and text changed */}
      <div className="absolute bottom-20 left-4 right-4 flex justify-center z-10">
        <button onClick={(e) => e.stopPropagation()} className="bg-white text-black font-bold text-[14px] py-2.5 px-8 rounded-full shadow-lg hover:bg-gray-200 transition">
          DROPP
        </button>
      </div>
    </div>
  );
}

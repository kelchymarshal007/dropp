export default function SplashPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-black">
      {/* 
        This meta tag forces the browser to redirect.
        It works 100% of the time, even if React fails to load.
      */}
      <meta httpEquiv="refresh" content="1.5;url=/reels" />
      
      <h1 className="text-6xl font-extrabold tracking-tighter text-white flex space-x-1">
        <span className="animate-wiggle" style={{ animationDelay: '0ms' }}>D</span>
        <span className="animate-wiggle" style={{ animationDelay: '100ms' }}>r</span>
        <span className="animate-wiggle" style={{ animationDelay: '200ms' }}>o</span>
        <span className="animate-wiggle" style={{ animationDelay: '300ms' }}>p</span>
        <span className="animate-wiggle" style={{ animationDelay: '400ms' }}>p</span>
      </h1>
    </main>
  );
}

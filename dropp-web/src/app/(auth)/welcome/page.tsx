import Link from 'next/link';

export default function WelcomePage() {
  return (
    <div className="flex flex-col min-h-screen justify-between py-12">
      
      {/* Top Section */}
      <div className="flex-1 flex flex-col items-center justify-center text-center space-y-6">
        <h1 className="text-6xl font-extrabold tracking-tighter text-white">
          Dropp
        </h1>
        <p className="text-xl text-gray-400 max-w-[250px]">
          Chat. Pay. Trust. The safest way to trade on social media.
        </p>
      </div>

      {/* Bottom Section */}
      <div className="space-y-4 w-full">
        <Link href="/signup" className="block w-full">
          <button className="w-full py-4 rounded-full font-semibold text-[15px] bg-dropp-orange text-black hover:bg-dropp-orange/90 transition-all active:scale-[0.98]">
            Get Started
          </button>
        </Link>
        
        <Link href="/login" className="block w-full">
          <button className="w-full py-4 rounded-full font-semibold text-[15px] bg-transparent text-white border border-border hover:bg-surface transition-all active:scale-[0.98]">
            I already have an account
          </button>
        </Link>
      </div>

    </div>
  );
}

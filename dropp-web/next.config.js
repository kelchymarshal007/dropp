/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: { ignoreBuildErrors: true },
  eslint: { ignoreDuringBuilds: true },
  
  // CRITICAL FIX: Stop Next.js from issuing 308 redirects for trailing slashes
  skipTrailingSlashRedirect: true,

  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://dropp-api-1:8000/:path*',
      },
      {
        source: '/media/:path*',
        destination: 'http://dropp-api-1:8000/media/:path*',
      },
    ];
  },
};

module.exports = nextConfig;

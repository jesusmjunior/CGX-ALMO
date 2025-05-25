/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  
  // Configurações para API externa
  async rewrites() {
    return [
      {
        source: '/api/backend/:path*',
        destination: process.env.BACKEND_URL ? `${process.env.BACKEND_URL}/:path*` : 'http://localhost:8000/:path*'
      }
    ];
  },

  // Configurações de ambiente
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    GEMINI_API_KEY: process.env.GEMINI_API_KEY,
    DATAWORLD_TOKEN: process.env.DATAWORLD_TOKEN,
  },

  // Configurações para build
  output: 'standalone',
  
  // Otimizações de imagem
  images: {
    domains: ['localhost'],
    formats: ['image/webp', 'image/avif'],
  },

  // Headers de segurança
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
        ],
      },
    ];
  },

  // Configurações experimentais
  experimental: {
    appDir: false,
  },
  
  // Configuração para Vercel
  trailingSlash: false,
  
  // Configurações de webpack (se necessário)
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Configurações customizadas de webpack aqui se necessário
    return config;
  },
}

module.exports = nextConfig;

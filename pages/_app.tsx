import type { AppProps } from 'next/app';
import Head from 'next/head';
import '../styles/globals.css';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <>
      <Head>
        <title>Sistema de Controle de Estoque</title>
        <meta name="description" content="Sistema inteligente de controle de estoque com IA integrada" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta charSet="utf-8" />
        
        {/* Favicon */}
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
        
        {/* Meta tags para SEO */}
        <meta name="keywords" content="estoque, controle, inventory, management, sistema, IA, AI" />
        <meta name="author" content="Sistema de Controle de Estoque" />
        <meta name="robots" content="index, follow" />
        
        {/* Open Graph / Facebook */}
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://stock-control.vercel.app/" />
        <meta property="og:title" content="Sistema de Controle de Estoque" />
        <meta property="og:description" content="Sistema inteligente de controle de estoque com IA integrada" />
        <meta property="og:image" content="/og-image.png" />
        
        {/* Twitter */}
        <meta property="twitter:card" content="summary_large_image" />
        <meta property="twitter:url" content="https://stock-control.vercel.app/" />
        <meta property="twitter:title" content="Sistema de Controle de Estoque" />
        <meta property="twitter:description" content="Sistema inteligente de controle de estoque com IA integrada" />
        <meta property="twitter:image" content="/og-image.png" />
        
        {/* PWA Support */}
        <meta name="theme-color" content="#2563eb" />
        <link rel="manifest" href="/manifest.json" />
        
        {/* Preconnect para otimização */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </Head>
      
      <Component {...pageProps} />
    </>
  );
}

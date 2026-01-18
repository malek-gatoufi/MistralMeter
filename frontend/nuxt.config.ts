// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },

  modules: [
    '@nuxtjs/tailwindcss',
    '@nuxtjs/seo',
  ],

  tailwindcss: {
    cssPath: '~/assets/css/main.css',
    configPath: 'tailwind.config.ts',
  },

  // SEO Configuration
  site: {
    url: 'https://mistralmeter.dev',
    name: 'MistralMeter',
    description: 'Production-grade LLM evaluation platform with variance analysis, human-in-the-loop ratings, and model comparison. Built for Mistral AI.',
    defaultLocale: 'en',
  },

  app: {
    head: {
      htmlAttrs: { lang: 'en' },
      title: '⚡ MistralMeter - LLM Evaluation Platform',
      titleTemplate: '%s | MistralMeter',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1, viewport-fit=cover' },
        { name: 'description', content: 'Production-grade LLM evaluation platform with variance analysis, human-in-the-loop ratings, and model comparison. Built with Mistral AI.' },
        { name: 'theme-color', content: '#f97316' },
        { name: 'author', content: 'Malek Gatoufi' },
        { name: 'robots', content: 'index, follow' },
        // Open Graph
        { property: 'og:type', content: 'website' },
        { property: 'og:site_name', content: 'MistralMeter' },
        { property: 'og:title', content: '⚡ MistralMeter - LLM Evaluation Platform' },
        { property: 'og:description', content: 'Production-grade LLM evaluation platform with variance analysis and model comparison.' },
        { property: 'og:image', content: '/og-image.png' },
        // Twitter Card
        { name: 'twitter:card', content: 'summary_large_image' },
        { name: 'twitter:title', content: '⚡ MistralMeter' },
        { name: 'twitter:description', content: 'LLM Evaluation Platform powered by Mistral AI' },
        // PWA / Mobile
        { name: 'apple-mobile-web-app-capable', content: 'yes' },
        { name: 'mobile-web-app-capable', content: 'yes' },
        { name: 'apple-mobile-web-app-status-bar-style', content: 'black-translucent' },
        { name: 'format-detection', content: 'telephone=no' },
      ],
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
        { rel: 'icon', type: 'image/png', sizes: '32x32', href: '/favicon-32x32.png' },
        { rel: 'apple-touch-icon', sizes: '180x180', href: '/apple-touch-icon.png' },
        { rel: 'manifest', href: '/manifest.json' },
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
      ]
    },
    pageTransition: { name: 'page', mode: 'out-in' },
    layoutTransition: { name: 'layout', mode: 'out-in' },
  },

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000'
    }
  },

  // Experimental features for better performance
  experimental: {
    viewTransition: true,
  },

  ssr: false, // SPA mode for this dashboard

  compatibilityDate: '2025-01-15'
})

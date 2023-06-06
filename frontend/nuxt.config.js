// https://nuxt.com/docs/api/configuration/nuxt-config
import { defineNuxtConfig } from "nuxt/config"
export default defineNuxtConfig({

  app: {
    head: {
      charset: 'utf-8',
      viewport: 'width=device-width, initial-scale=1',
      htmlAttrs: {
        lang: 'ja', prefix: 'og: https://ogp.me/ns#'
      },
      title: "kagomma.i",
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { hid: 'description', name: 'description', content: '' },
        { hid: 'og:site_name', property: 'og:site_name', content: 'kagomma.i' },
        { hid: 'og:type', property: 'og:type', content: 'website' },
        { hid: 'og:url', property: 'og:url', content: 'https://kagomma.info' },
        { hid: 'og:title', property: 'og:title', content: 'kagomma.i' },
        { hid: 'og:description', property: 'og:description', content: '鹿児島（かごんま）製AIが、どんな質問にも、鹿児島愛100%で答えます' },
        { hid: 'og:image', property: 'og:image', content: 'https://kagomma.info/img/screen.jpg' },
        { hid: 'twitter.card', name: 'twitter:card', content: 'summary' },
        { hid: 'twitter:title', property: 'twitter:title', content: 'kagomma.i' },
        { hid: 'twitter:description', property: 'twitter:description', content: '鹿児島（かごんま）製AIが、どんな質問にも、鹿児島愛100%で答えます' },
        { hid: 'twitter:image', property: 'twitter:image', content: 'https://kagomma.info/img/screen.jpg' },
      ],
      link: [
        {
          rel: "stylesheet",
          href: "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css",
        },
      ],
    }
  },
  css: ["assets/styles/main.scss", "@fortawesome/fontawesome-svg-core/styles.css"],
  plugins: ["@/plugins/fontawesome.js", "@/plugins/analytics.js"],
  modules: [
    "@nuxt/content",
    "@nuxtjs/google-fonts"
  ],
  googleFonts: {
    families: {
      // 'Jost': [400, 500, 600, 700], // just example
    },
  },
  // in case that you are coding on windows(IDE) with WSL2(launching this app)
  vite: {
    server: {
      watch: {
        usePolling: true,
      },
    },
  },
  runtimeConfig: {
    public: {
      apiUrl: "http://localhost:5000/api", // overwritten if env vairable 'NUXT_PUBLIC_API_URL' exists
    },
  },
})

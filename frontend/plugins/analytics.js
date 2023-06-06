import VueGtag from "vue-gtag-next"
import { defineNuxtPlugin } from "nuxt/app"
export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.use(VueGtag, {
    property: {
      id: "G-ELQ0KL1WBL",
    },
  })
})

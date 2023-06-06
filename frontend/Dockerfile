#FROM node:18-slim
FROM node:18

ENV TZ Asia/Tokyo

RUN mkdir -p /usr/src/nuxt-app
WORKDIR /usr/src/nuxt-app
COPY . .
COPY .env.production .env

RUN curl -f https://get.pnpm.io/v6.16.js | node - add --global pnpm

#RUN npm ci && npm cache clean --force
RUN pnpm install

ENV NUXT_PUBLIC_API_URL=/api

# refs: https://stackoverflow.com/questions/20635472/using-the-run-instruction-in-a-dockerfile-with-source-does-not-work
RUN pnpm run build

ENV NUXT_HOST=0.0.0.0
ENV NUXT_PORT=3000

EXPOSE 3000

ENTRYPOINT ["node", ".output/server/index.mjs"]

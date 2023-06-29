# build front-end
FROM node:lts-alpine AS frontend

RUN npm install pnpm -g

WORKDIR /app

COPY ./package.json /app

COPY ./pnpm-lock.yaml /app

RUN pnpm install

COPY . /app

RUN pnpm run build-only

FROM frontend AS final

COPY --from=frontend /app/dist /app/public

EXPOSE 4173

CMD ["pnpm", "run", "preview"]

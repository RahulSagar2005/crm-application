# Stage 1: build the Vite app
FROM node:20-alpine AS build

WORKDIR /app

# Install deps first for better layer caching
COPY package*.json ./
RUN npm ci

# Copy source and build
COPY . .

# Vite bakes import.meta.env.VITE_* at build time, so this ARG must be
# provided via Railway's "Build Command" / "Variables" so the bundle
# points at the deployed backend URL, not localhost.
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# Stage 2: serve dist/ via nginx with SPA rewrite
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

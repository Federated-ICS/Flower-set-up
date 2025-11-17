FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY dashboard/package.json dashboard/pnpm-lock.yaml* ./
RUN npm install -g pnpm && pnpm install --frozen-lockfile

# Copy Next.js app files
COPY dashboard/ ./

# Build Next.js app
RUN pnpm run build

EXPOSE 3000
CMD ["pnpm", "start"]

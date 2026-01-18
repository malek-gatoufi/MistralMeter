# ============================================
# ⚡ MistralMeter - Frontend Dashboard
# Multi-stage Nuxt 3 build
# ============================================

# ---- Build Stage ----
FROM node:20-alpine AS builder

LABEL maintainer="Malek Gatoufi"
LABEL description="MistralMeter Dashboard - Nuxt 3 Frontend"

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies (using npm install since no package-lock.json)
RUN npm install --loglevel=error

# Copy source code
COPY frontend/ .

# Build for production
ENV NODE_ENV=production
RUN npm run build

# ---- Production Stage ----
FROM node:20-alpine AS production

# Create non-root user
RUN addgroup -S mistral && adduser -S mistral -G mistral

WORKDIR /app

# Copy built application
COPY --from=builder --chown=mistral:mistral /app/.output ./.output

# Switch to non-root user
USER mistral

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Expose port
EXPOSE 3000

# Run Nuxt server
ENV HOST=0.0.0.0
ENV PORT=3000
CMD ["node", ".output/server/index.mjs"]

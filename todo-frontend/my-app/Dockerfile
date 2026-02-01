# Dockerfile for todo-frontend
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json yarn.lock* ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy the rest of the application
COPY . .

# Build the Next.js app
RUN yarn build

# Production stage
FROM node:18-alpine AS runner

WORKDIR /app

# Install serve to serve the Next.js app
RUN npm install -g serve

# Copy the build output from the previous stage
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# Expose port
EXPOSE 3000

# Run the application
CMD ["serve", "-s", "."]
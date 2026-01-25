# Multi-stage build for the Next.js frontend application
# Stage 1: Build the application
FROM node:20-alpine AS builder

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json from the my-app directory
COPY my-app/package*.json ./

# Install dependencies
RUN npm ci

# Copy the rest of the application code from my-app directory
COPY my-app/. .

# Build the application for production
RUN npm run build

# Stage 2: Create the production image
FROM node:20-alpine

# Set the working directory
WORKDIR /app

# Install only production dependencies
RUN apk add --no-cache dumb-init

# Copy the build output from the builder stage
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

# Expose the port the app runs on
EXPOSE 3000

# Define the command to run the application
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "server.js"]
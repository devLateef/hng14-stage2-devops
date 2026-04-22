FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm install


FROM node:18-alpine AS runtime

WORKDIR /app

RUN adduser -D -u 1001 appuser

COPY --from=builder /app/node_modules ./node_modules
COPY . .

USER appuser

HEALTHCHECK CMD wget -qO- http://localhost:3000 || exit 1

CMD ["node", "app.js"]

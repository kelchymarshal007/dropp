# Dropp - Global Social Commerce OS

Dropp turns unstructured social media DMs into secure, escrow-protected transactions.

## Current Architecture
- `dropp-api`: FastAPI (REST, WebSockets, State Machine, Auth).
- `dropp-worker`: Celery (Timers, Webhooks, Notifications).
- `dropp-media`: Celery (FFmpeg video compression for Reels).
- `dropp-web`: Next.js 14 PWA.
- `dropp-db`: PostgreSQL 16.
- `dropp-redis`: Redis 7 (Pub/Sub, Broker).

## System Status
- **Foundation & Data Layer:** Complete.
- **Reels Engine (Discovery):** Complete (HLS streaming, likes, comments, bookmarks).
- **Auth Engine (Production):** Complete. Full email OTP (SMTP), phone OTP (Termii), Google SSO, and X-style UI.
- **Creator Tab (Dashboard, Account Menu, Settings):** Architecture defined. UI build pending.
- **TradeChat & Escrow:** Upcoming.

## Local Development
1. Run `docker compose up -d --build`
2. Frontend is available at `http://localhost:8080`
3. API is available at `http://localhost:8000`

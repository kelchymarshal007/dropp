# DROPP: Global Social Commerce OS with Escrow

## 1. Executive Summary
Dropp is a full-scale social commerce platform that turns unstructured social media DMs (Instagram, TikTok, WhatsApp) into secure, escrow-protected transactions. It combines an in-house video discovery feed (Dropp Reels), a 3-way negotiation chat (TradeChat), and a secure payment dashboard (Dropp Card).

## 2. The 3 Pillars of Dropp
1. **Dropp Reels (Discovery):** A TikTok-style vertical video feed where sellers showcase items.
2. **TradeChat (Negotiation):** A 3-way WebSocket chat (Buyer, Seller, Dropp AI Agent). The AI Agent verifies availability, determines dispatch mode, and locks in digital signatures before payment.
3. **Dropp Card (Payments):** An append-only ledger dashboard showing Escrow (Pending), Available Balance, and DroppScore.

## 3. Core Features
- **The Secret Checkout:** Once both parties digitally sign the agreed terms, the AI Agent freezes the chat and sends a unique, time-limited checkout link to the Buyer.
- **Dual Dispatch:** Sellers can either Self-Dispatch (upload own waybill) or use Dropp Dispatch (integrated via 3PL APIs like GIG/DHL, with Dropp taking a 5% logistics margin).
- **Dropp Scout:** A premium AI feature ($5/mo Buyer, $20/mo Seller) that matches "Wanted Requests" with seller inventory across the Dropp network and external platforms.

## 4. Architecture & Microservices
- `dropp-api`: FastAPI (REST, WebSockets, State Machine, Auth).
- `dropp-worker`: Celery (Timers, Webhooks, Notifications).
- `dropp-media`: Celery (FFmpeg video compression for Reels).
- `dropp-web`: Next.js 14 PWA.
- `dropp-db`: PostgreSQL 16.
- `dropp-redis`: Redis 7 (Pub/Sub, Broker).

## 5. The Escrow State Machine
`draft` -> `sent` -> `viewed` -> `negotiating` -> `agreed` -> `awaiting_payment` -> `funded` -> `shipped` -> `delivered` -> `completed`. 
Funds are only released when the state reaches `completed`.

# DROPP: Full Project Scope & Build Guide

> **Version:** MVP 1.1 (Includes In-House Reels and BIKEM Pay Engine)
> **Purpose:** One document that answers: what Dropp is, why it can make money, how it works, what to build, in what order, with which files and folders.

---

## 1. What Dropp Is

### 1.1 The problem
Selling through Instagram, TikTok, WhatsApp, and Facebook is huge, but it runs on DMs and screenshots with no protection:
- Buyers send money to a stranger and hope.
- Sellers get flooded with time-wasters.
- Nobody has a neutral record of the deal.

### 1.2 The product (one sentence)
Dropp turns interest in a social-media post into a verified, escrow-protected deal: the buyer "drops" a card on the seller's post, the seller sees a serious buyer, and the money is held safely until the item arrives.

### 1.3 The three promises
- **Buyer:** Your money is held until you get what you paid for.
- **Seller:** Every Dropp you receive is a real, verified buyer, and you get paid for sure.
- **Both:** One shared record of the deal: price, terms, delivery, chat.

### 1.4 What Dropp is NOT
- Not a standard marketplace (sellers keep selling on their platform, Dropp is the escrow).
- Not a wallet or bank (no stored balances in MVP).
- Not an AI-first product (escrow logic is deterministic code).

---

## 2. How It Works: The Buyer-Initiated Flow

1. Buyer sees a product on social media.
2. Buyer taps Share -> Dropp (or copies link).
3. Dropp builds a preview, buyer confirms offer amount and delivery city.
4. Dropp creates a DROPP CARD (short link).
5. Buyer sends link to seller.
6. Seller taps link, sees the card (no app required), and verifies phone via OTP.
7. Negotiation in the 3-way chat (Buyer + Seller + Dropp Agent).
8. Both agree -> payment link issued.
9. Buyer pays -> money locked in escrow.
10. Seller ships -> buyer confirms -> seller paid.

---

## 3. The Dropp Card (Thumbnail) Specification

- **The Link:** `https://dropp.app/d/{code}` (8-10 URL-safe chars).
- **The Preview Image:** Served as Open Graph / Twitter image via Next.js `next/og`.
- **Elements:** Item image, source-platform badge, seller handle, offer amount, expiry countdown, buyer trust line, shield icon.

---

## 4. In-House Reels & Discovery (MVP 1.1 Amendment)

### 4.1 Rationale
To mitigate the existential risk of social media platforms restricting links to Dropp, we are introducing an in-house "Dropp Reels" feed from Day 1. This provides sellers with a direct storefront on Dropp and creates a defensible discovery loop.

### 4.2 The Lean Reels Spec
- **Format:** Vertical video (9:16) or Image. Max 12 seconds. Max 10MB.
- **Processing:** Backend compresses via FFmpeg to 720p to save bandwidth.
- **Interaction:** Infinite scroll, autoplay muted, tap to unmute.
- **Commerce Integration:** Every Reel is directly linked to a Dropp Card creation flow ("Drop this item").

### 4.3 Data Model Additions
- `posts` table: `id`, `seller_id`, `media_url`, `media_type`, `caption`, `price_minor`, `currency`, `status`, `created_at`.

---

## 5. Social Platform Reality Check

- Do not build on unofficial APIs or scrapers.
- The buyer cannot be removed from the "send" step officially.
- **The Auto-Send Ladder:**
  - L0: Native share sheet.
  - L0.5: Share-in (register as a share target).
  - L1: WhatsApp deep link.
  - L2: Seller Connect (opt-in automation via official business APIs).

---

## 6. Economics & Unit Economics

- **Buyer Protection Fee:** 3% of item price (min N500, cap N7,500).
- **Seller Commission:** 1.5% on completed trades (0% for first 60 days).
- **Contribution Margin:** Profitable above N15,000 AOV. Target high-ticket items (phones, electronics).
- **Take Rate Rule:** Do not rely on 1.2%. Charge the buyer for protection and the seller for the platform.

---

## 7. Escrow, Payments & BIKEM Pay Engine Integration

### 7.1 Payment Provider Strategy: The BIKEM Engine
We do not hardcode payment gateways. We use the **BIKEM Pay Engine** (Parent/Child Plugin Architecture).
- **The Parent:** Handles routing, health checks, atomic deductions, and webhook verification.
- **The Child:** Translates Dropp standard requests into Paystack, Monnify, Flutterwave, or Stripe syntax.

### 7.2 The BaseGateway Contract
Every child must implement these 5 methods:
1. `get_banks(currency)`
2. `resolve_account(bank_code, account_number)`
3. `generate_deposit_account(user_pubkey, amount, currency)`
4. `initiate_withdrawal(bank_code, account_number, amount, currency)`
5. `verify_webhook_signature(raw_body, signature)`

### 7.3 Dynamic Configuration
Gateways are loaded dynamically via `gateways.json` at runtime. No hardcoded currencies. The engine resolves the zone (e.g., NGN -> WEST_AFRICA -> Paystack).

### 7.4 Funds Flow
- Buyer pays item price + protection fee.
- Provider receives (status: PAID, webhook verified).
- Dropp ledger entry: ESCROW_HELD.
- On release: payout to seller (minus commission), recognize fee.
- On refund: reverse ledger entries.

---

## 8. System Architecture (Microservices)

- **dropp-api (FastAPI):** Handles REST endpoints, state machine, and ledger logic.
- **dropp-worker (Celery):** Handles background timers (expiration), webhook queues, and video compression.
- **dropp-web (Next.js):** Public Dropp pages, Reels feed, and Admin console.
- **Database:** PostgreSQL 16 (Single primary for MVP).
- **Cache/Broker:** Redis 7.
- **Storage:** S3-Compatible (Cloudflare R2) for Reels and dispute evidence.

---

## 9. State Machine

Single source of truth: `dropp-api/app/domain/state_machine.py`. Terminal states cannot transition.

### 9.1 States & Funds
- `draft`: none
- `sent`: none (48h timer)
- `viewed`: none (48h timer)
- `negotiating`: none (72h timer)
- `agreed`: none (24h timer to pay)
- `awaiting_payment`: none (24h timer)
- `funded`: ESCROW (Seller must ship in 3 days)
- `shipped`: ESCROW (Delivery window)
- `delivered`: ESCROW (48-72h inspection)
- `completed`: Released to SELLER (Terminal)
- `disputed`: FROZEN (72h for evidence)
- `refunded`: Returned to BUYER (Terminal)
- `declined`, `expired`, `cancelled`: Terminal, no funds.

### 9.2 Transitions
- `draft` -> `sent` -> `viewed` -> `negotiating` -> `agreed` -> `awaiting_payment` -> `funded`
- `funded` -> `shipped` -> `delivered` -> `completed`
- `funded`/`shipped`/`delivered` -> `disputed` -> `refunded` | `completed`
- `delivered` -> `completed` (Buyer confirms OR timer expires).

### 9.3 Rules
- Every transition requires specific actors (buyer/seller/system/admin).
- Transitions and ledger entries happen in one DB transaction.
- Idempotency on all webhooks and button clicks.

---

## 10. Data Model (Key Tables)

All money is stored as integer minor units (kobo, cents) plus a currency code.

- **users**: `id`, `handle`, `phone_e164`, `role`, `phone_verified`, `country`.
- **dropps**: `id`, `code`, `buyer_id`, `seller_id`, `source_url`, `source_platform`, `currency`, `offer_minor`, `final_minor`, `fee_minor`, `status`, `expires_at`, `version`.
- **ledger_entries**: `id`, `dropp_id`, `entry_type` (ESCROW_HELD, ESCROW_RELEASED, REFUND, FEE_EARNED), `amount_minor`, `currency`.
- **posts** (Reels): `id`, `seller_id`, `media_url`, `media_type`, `price_minor`, `currency`.
- **webhook_events**: `provider`, `event_id`, `payload` (for idempotency).
- **disputes**: `dropp_id`, `opened_by`, `reason`, `status`, `decision`.

---

## 11. API Specification

Base path `/v1`. JWT bearer auth.

### Core Endpoints
- `POST /auth/phone/otp` (Send OTP)
- `POST /auth/phone/verify` (Verify -> JWT)
- `POST /dropps` (Create Dropp Card)
- `GET /dropps/{id}` (Dropp details)
- `POST /dropps/{id}/respond` (Seller accept/counter/decline)
- `POST /dropps/{id}/checkout` (Create payment session)
- `POST /dropps/{id}/ship` (Add tracking/proof)
- `POST /dropps/{id}/confirm-received` (Release funds)
- `POST /dropps/{id}/dispute` (Open dispute)

### Webhooks
- `POST /webhooks/paystack`
- `POST /webhooks/flutterwave`
- `POST /webhooks/stripe`

### Public
- `GET /public/dropps/{code}` (Safe public view)
- `POST /public/dropps/{code}/claim` (Seller claims via OTP)

---

## 12. Build Plan & Stages

We build in 7 distinct stages. No stage is marked complete until Docker builds, API responds, and code is committed to Git.

- **Stage 1: Foundation** - Docker, PostgreSQL, Redis, FastAPI skeleton.
- **Stage 2: Data Layer** - SQLAlchemy models (Dropps, Posts, Ledger) and Alembic migrations.
- **Stage 3: The Engine** - State Machine, Dropp creation API, Link parser.
- **Stage 4: Web UI** - Next.js Dropp Card page, OG image generator, Claim flow.
- **Stage 5: Reels** - S3 upload, FFmpeg processing, Next.js Reels feed.
- **Stage 6: BIKEM Integration** - Gateway loading, webhook handlers, real payment flow.
- **Stage 7: Jobs & Admin** - Celery timers for expiration, Admin dispute UI.


---

## 23. AMENDMENT: DUAL-TRACK ARCHITECTURE (PUBLIC LINK + FULL APP)

We are building both a frictionless public web link and a full social commerce app (PWA first, Flutter later).

### Track 1: The Public Web Link (Frictionless Onboarding)
- Buyer lands on `/d/[code]` without an account.
- Views the offer, clicks "Accept & Pay".
- Enters phone number (OTP). Once verified, the Dropp is created and sent to the seller's DM.
- The buyer is prompted: "Download the Dropp App to track your order and chat with the seller."

### Track 2: The Full App (The 3 Pillars)
The app is a PWA built in Next.js (Flutter later). It has 3 core tabs:
1. **Reels Tab (Discovery):** Vertical video feed of items. Tap to create a Dropp or view details.
2. **TradeChat Tab (Negotiation & Escrow):** 3-way chat (Buyer, Seller, AI Agent). System messages are injected by the backend State Machine to confirm funds are locked, shipped, etc.
3. **Card Tab (Payments & Dashboard):** Shows Escrow Balance (Pending), Available Balance, and DroppScore. Powered entirely by the append-only `ledger_entries` table.

### Frontend Route Structure (Next.js App Router)
- `(public)/d/[code]` - The public escrow link.
- `(app)/reels` - The vertical video feed.
- `(app)/chat/[id]` - The TradeChat interface.
- `(app)/card` - The Wallet/Dashboard.

---

## 24. FULL-SCALE BACKEND ARCHITECTURE & TECH STACK

### 24.1 The Microservices
1. **dropp-api (FastAPI):** REST, Auth, State Machine, WebSockets.
2. **dropp-worker (Celery):** State timers, notifications, dispatch webhooks.
3. **dropp-media (Celery Worker):** FFmpeg video compression for Reels.
4. **dropp-web (Next.js PWA):** 3 Pillars (Reels, Chat, Card).
5. **dropp-db (PostgreSQL 16):** Core relational data + Append-only Ledger.
6. **dropp-redis (Redis 7):** Pub/Sub for Chat, Cache, Task Broker.

### 24.2 System Flows
- **Auth:** Phone OTP (Termii) -> Backend verifies -> Issues JWT.
- **Reels:** Upload -> Celery/FFmpeg compress -> S3/R2 -> CDN -> Next.js Video Feed.
- **Chat:** WebSocket -> Postgres (save) -> Redis Pub/Sub (broadcast to Buyer/Seller/AI).
- **Payments:** BIKEM Engine Webhook -> Verify HMAC -> State Machine -> Ledger.
- **Dispatch:** Courier API (DHL/GIG) -> Waybill generation -> Delivery Webhook -> Start Inspection Timer.

### 24.3 Scalability Strategy
- **Database:** PgBouncer for connection pooling, Read Replicas for feed/chat.
- **Redis:** Redis Cluster for WebSocket scaling.
- **Storage:** Cloudflare R2 for zero-egress video storage.
- **Edge:** Cloudflare CDN for global video caching.

### 24.4 Next Build Stages
- **Stage 6:** Auth & User Management (OTP, JWT, User table).
- **Stage 7:** Reels Engine (S3 Upload, FFmpeg Worker, Feed API).
- **Stage 8:** Realtime Chat (WebSockets, Messages table, Redis Pub/Sub).
- **Stage 9:** BIKEM Integration & Ledger (Escrow logic).

## 25. DISPUTE RESOLUTION & AUTO-RELEASE

### 25.1 The 24-Hour Auto-Release Timer
- Once the Seller marks the item as `shipped` and the carrier confirms `delivered`, the state machine starts a 24-hour timer.
- The Buyer is notified via push/chat: "Item delivered. Please confirm receipt within 24 hours."
- If the Buyer does nothing, the Celery worker automatically transitions the state to `completed` and triggers the escrow release. This prevents buyers from holding sellers' money hostage.

### 25.2 The Dispute Flow
- **Trigger:** Buyer or Seller can open a dispute from `funded`, `shipped`, or `delivered`.
- **State:** `disputed`. Funds are **FROZEN**.
- **Evidence Phase (72h):** Both parties are prompted to upload video/photo evidence to the chat/evidence locker.
- **Admin Resolution:**
  - `refunded`: Buyer gets money back. Seller pays return shipping + Dropp penalty fee.
  - `completed`: Seller gets money. Buyer's dispute is rejected.

## 26. DROPP REELS: MEDIA PIPELINE & SOCIAL GRAPH

### 26.1 The Media Pipeline (Seamless Playback)
To ensure Dropp Reels loads instantly like TikTok/Instagram, we do not serve raw MP4 files. We use a multi-step pipeline:
1.  **Ingest & Compress:** The `dropp-media` worker receives the file and uses FFmpeg to compress it to a baseline (1080x1920, H.264, ~5Mbps).
2.  **ABR Ladder Generation:** We transcode the baseline into multiple renditions (1080p, 720p, 480p).
3.  **HLS Packaging:** We chunk the videos into 2-second segments and package them as HLS (HTTP Live Streaming) playlists (.m3u8).
4.  **CDN Delivery:** The `.m3u8` playlists and chunks are stored on Cloudflare R2/S3 and served via CDN. The player uses Adaptive Bitrate Streaming (ABR) to switch quality based on the user's network speed.

### 26.2 The Social Graph
Reels are not just videos; they are social objects. We track:
- **Likes:** `post_likes` table (unique user-post pair).
- **Comments:** `post_comments` table (supports threaded replies via `parent_id`).
- **Drops:** `dropp_count` (how many times a Dropp Card was created from this Reel).
- **Shares:** `share_count` (native share sheet usage).

## 27. DROPP SCOUT: EXTERNAL LEAD GENERATION (PRO FEATURE)

### 27.1 Overview
Dropp Scout is an AI-powered sourcing engine for Pro Buyers. It searches the external web and social media platforms for items matching the buyer's request, scores the sellers based on reputation and price, and generates Dropp Bids.

### 27.2 The Scout Pipeline
1. **Input:** Buyer creates a `WantedRequest` (Item, Target Price, Source Location, Buyer Location).
2. **Discovery:** The `ScoutWorker` calls a Search API (e.g., SerpApi) to find public posts matching the keywords.
3. **Scoring:** Extracts seller handle, post URL, and engagement metrics (likes/comments). If the seller has high engagement and the price matches, the score is high.
4. **Output:** Returns a list of Top 5 Matches to the Buyer.
5. **Action:** Buyer can manually send a Dropp Bid to each match, or use the "Auto-Bid" feature (Pro only) to send links to the top 5.

## 28. THE NOTIFICATION SYSTEM

### 28.1 Overview
A centralized service that fires notifications across In-App (WebSocket), Email, SMS, and Push (FCM).

### 28.2 Data Model
- `notifications` table: `id`, `user_id`, `type` (scout_match, escrow_update, dispute), `title`, `body`, `is_read`, `created_at`.

### 28.3 Channels
- **WebSocket:** Instantly pushes to the UI if the user is online.
- **Celery Worker:** Queues emails (SendGrid) and SMS (Termii) for asynchronous delivery.

## 29. FRONTEND ROUTE MAP & UX RULES

We are building a mobile-first, monochrome Progressive Web App (PWA) in Next.js. Every primary action must be achievable within **3 taps (The 3-Click Rule)**. 

### 29.1 The Auth Phase (Current Build Focus)
This is the scope for Phase 1. We do not build the rest of the app until this is perfect.

| Route | Type | Purpose |
| :--- | :--- | :--- |
| `/auth/welcome` | Page | 3-slide onboarding splash with "Get Started" CTA |
| `/auth/login` | Page | Root login (Tabs: Email / Phone) |
| `/auth/signup` | Page | Root signup (Tabs: Email / Phone / Google / Apple) |
| `/auth/verify-otp` | Page | 6-digit OTP verification (auto-submits) |
| `/auth/role` | Page | Post-signup: Choose "I'm buying" or "I'm selling" |
| `/auth/forgot-password` | Page | Enter email to receive reset link |
| `/auth/reset-password` | Page | Set new password via token |
| `/auth/verify-email` | Page | Landing page for email verification link |
| `/auth/kyc` | Page | Seller KYC (Gate to first payout) - Phase 2 |

### 29.2 The Core App (Future Phases)
| Route | Sub-Routes / Modals | Purpose |
| :--- | :--- | :--- |
| `/reels` | `/upload`, `+comments modal`, `+share modal` | TikTok-style discovery feed |
| `/chat` | `/chat/[id]`, `+availability modal`, `+sign modal`, `+dispute modal` | 3-way TradeChat and Escrow state |
| `/create` | `/preview`, `/manual`, `/offer`, `/share` | Link parser to create a Dropp Card |
| `/d/[code]` | `/expired`, `/claimed`, `+login modal`, `+accept modal` | Public Dropp Card (Buyer-facing) |
| `/pay/[token]` | `/method`, `/card`, `/transfer`, `/success` | Secret Checkout Portal |
| `/card` | `/transactions`, `/escrow`, `/payouts`, `/payouts/new` | Wallet, Balance, and Payouts |
| `/scout` | `/new`, `/requests`, `/requests/[id]/matches` | Pro Buyer Sourcing Engine |
| `/profile` | `/edit`, `/settings`, `/notifications` | User Profile and Settings |

### 29.3 Shared UI Rules
1. **Mobile-First:** All pages built for `375px` width, centered on desktop with `max-w-md`.
2. **Icons:** FontAwesome Solid only. No emojis.
3. **Theme:** Pure black background (`#000000`), white text, Amazon-style Orange (`#FF9900`) for primary CTAs.
4. **Auth Gating:** If a user opens `/reels`, `/chat`, or `/card` without a JWT in `localStorage`, they are instantly redirected to `/auth/login`.

## 30. TIKTOK-STYLE REELS ENGINE & LAZY AUTHENTICATION

### 30.1 The Frictionless Entry (Splash & Public Feed)
We are pivoting the entry point of the app to maximize user acquisition (TikTok model).
- **The Splash:** The root URL (`/`) displays an animated Dropp logo for 1.5 seconds, then immediately redirects to `/reels`.
- **Public Reels:** The `/reels` feed is 100% public. No JWT is required to view videos.
- **Lazy Authentication (Soft Gate):** Authentication is only triggered when the user attempts a protected action (Like, Comment, Share, or "Drop it"). This ensures immediate content delivery.

### 30.2 The Video Pipeline (HLS & ABR)
- **Ingest:** FFmpeg compresses uploads to 720p H.264.
- **ABR Ladder:** Generates multiple resolutions (1080p, 720p, 480p).
- **HLS Packaging:** Chunks video into 2-second segments (.m3u8 playlists) for adaptive streaming.
- **Delivery:** Cloudflare R2 + CDN for edge caching and instant playback.

### 30.3 Client Preloader
- **IntersectionObserver:** Only the video in the viewport plays.
- **Preload Window:** Preloads the next 2-3 videos in the background. Unmounts videos scrolled out of view to save memory.

### 30.4 The Recommendation Engine (MVP)
- **Data Collection:** Logs watch time, completion rate, likes, comments, and shares.
- **Ranking Formula (MVP):** Score = (Watch Time * 0.5) + (Likes * 0.2) + (Comments * 0.3).
- **Caching:** Pre-computed feeds cached in Redis for instant load.

### 30.5 Scalability
- **Load Balancers:** For routing API requests.
- **Database Indexing:** Heavy indexing on `created_at`, `like_count`, and `view_count`.
- **Redis:** For feed caching, session management, and rate limiting.

## 31. USER & CREATOR OPERATIONS (The Profile Tab)

The "Profile" tab is not just a static page; it is a full Creator Dashboard where users manage their entire Dropp ecosystem.

### 31.1 Creator Content (My Reels)
- `/profile/reels`: Grid view of uploaded videos.
- `/profile/reels/[id]/edit`: Edit caption, price, or delete.
- `/profile/reels/[id]/analytics`: Views, likes, comments, and Dropp conversions.

### 31.2 Trade Management
- `/profile/trades`: Active and past escrow deals.
- `/profile/disputes`: Open disputes and evidence submission.
- `/profile/scout`: Manage Wanted Requests (Pro).

### 31.3 Financial Operations
- `/profile/wallet`: Balance (Available vs Pending), transaction history.
- `/profile/payouts`: Withdrawal requests.
- `/profile/banks`: Manage linked bank accounts.

### 31.4 Account Settings
- `/profile/edit`: Update avatar, name, handle.
- `/profile/kyc`: Identity verification.
- `/profile/subscription`: Manage Pro tiers.
- `/profile/settings`: Notifications, security, and logout.

## 32. COMMERCE-ONLY CONTENT & MODERATION

Dropp is strictly a commerce platform, not a social network. 
### 32.1 Content Rules
- **Products Only:** Users can only post videos showcasing items for sale (e.g., electronics, fashion, services). Personal vlogs, memes, or unrelated content are prohibited.
- **No NSFW:** Explicit content of any kind will result in an immediate ban.

### 32.2 Moderation Pipeline
1. **Pre-Upload Checkbox:** Users must agree to the commerce-only policy before the upload starts.
2. **AI Vision Moderation (Backend):** The `media-worker` uses a Vision API to detect NSFW. If flagged, the video is auto-deleted, and the user receives a warning.
3. **Product Verification:** AI checks if the video contains a product. If borderline, it goes to the Admin Moderation Queue.
4. **Admin Moderation:** Admins can approve or reject flagged videos before they go live on the Reels feed.

## 33. THE SPLASH & LAZY AUTH FLOW
- The root URL (`/`) is an animated Splash screen lasting 1.5 seconds.
- It immediately routes to `/reels` (Public, no auth required).
- If a user clicks "Drop this" or "Like", a modal prompts them to log in (Lazy Auth).

## 34. TIKTOK-STYLE PROFILE & VIDEO PROCESSING PIPELINE

### 34.1 The Creator Profile UI
- **Layout:** Mimics TikTok. Header with Avatar, Name, Handle, and Analytics (Trades, Followers, Views).
- **Grid:** 3-column masonry grid showing uploaded Reels. Drafts are shown with a lock/draft icon.
- **FAB (Floating Action Button):** A "Liquid Glass" plus button hovering above the grid to trigger the video upload/editor flow.

### 34.2 Client-Side Video Editor (Phase 2)
- Built using `ffmpeg.wasm` (FFmpeg compiled to WebAssembly) so users can trim, crop, add text, and add music directly in the browser without uploading the raw file first.
- Limits: Max 15 seconds, max 10MB. 

### 34.3 Server-Side Processing Pipeline (The Magic)
To ensure the server never slows down, we use an asynchronous pipeline:
1. **Raw Upload:** Browser uploads the 15s video to an S3/R2 temporary bucket.
2. **Queue:** The API drops a message into Redis (`process_video` task).
3. **Media Worker:** A dedicated Celery container (running FFmpeg) picks up the task, transcodes the video to 720p/1080p H.264, and generates HLS chunks.
4. **CDN Delivery:** The processed chunks are uploaded to Cloudflare R2 and served via CDN. The database is updated with the new `.m3u8` URL.
5. **Scalability:** Because processing happens in the background, the API can accept 10,000 uploads per second without breaking a sweat.

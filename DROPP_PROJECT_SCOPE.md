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


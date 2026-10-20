# Loomola

> **Capture you own.**

Self-hosted screen recording + AI meeting notes. Open-source alternative to Loom + Granola, in one product.

> Active dev. Invite-based multi-user. The live instance at [loom.dissonance.cloud](https://loom.dissonance.cloud) is what I use daily as my own Loom + Granola replacement.

## What it is

Two products in one self-hosted codebase, gated by a single env flag (`ENABLE_GRANOLA`):

- **Screen recording (Loom-shape).** Screen + camera + mic + system audio, captured in the browser via the [companion Chrome extension](extension/). Branded share pages with Slack/Discord link previews, comments, view tracking, AI-generated titles, summaries, chapters, action items, and hover-scrub thumbnails.
- **AI meeting notes (Granola-shape).** Real-time audio transcription from a native macOS desktop app. Live notepad while the meeting runs. Manual AI notes generation when the user is ready. Attendee tracking, folder organization, speaker attribution.

Both surfaces use the same Postgres / R2 / Deepgram / Claude pipeline. Same `media_objects` table with a `type` column, so adding a third product (something like MacWhisper, say) reuses everything.

## Why this vs. the alternatives

| | Loom | Granola | [Cap](https://github.com/CapSoftware/Cap) | **Loomola** |
|---|---|---|---|---|
| Screen recording | ✓ | — | ✓ | ✓ |
| AI meeting notes | — | ✓ | — | ✓ |
| Self-host | — | — | ✓ | ✓ |
| Pricing (you) | $12.50–$20 / user / month | $20 / user / month (Pro) | Free + paid managed | Free; you pay your own infra (~$15–25/mo total across Supabase + R2 + Deepgram + Anthropic on light usage) |
| Transcription | proprietary | proprietary (real-time, no audio kept) | local Whisper | **Deepgram** (best-in-class hosted, ~$0.0043/min) |
| AI summaries | basic | yes | basic | Claude Sonnet 4.6 with structured Zod output |
| Custom branding on share pages | enterprise tier | — | — | ✓ (logo + accent + Google Font + CTA + footer per brand profile) |
| Status | Atlassian-owned; [raised prices ~100× in Feb 2026](https://x.com/heynavtoor/status/2052307308253003921) | Active, free tier locks notes >30d | 18k★ active OSS | Active OSS, invite-based multi-user |

## How this came to exist

I got excited the day I found Cap. Shared it around, dug in, spent a few hours trying to get the transcription path working on real meeting audio. It wasn't behaving the way I expected. I submitted my findings to the repo, a couple of other people chimed in saying they were seeing the same thing, and no fix arrived. Solo OSS with finite time, totally fair. Real respect for what Richie has built, no shade at all.

But I needed something that worked, and I also wanted Granola-shape meeting notes living alongside the screen recordings. That combination didn't exist anywhere I could find on the OSS side, so I started building Loomola. It's been my daily driver for a couple of months now.

If you pay for both Loom AND Granola today, this is the package that replaces both at once.

## Tech stack

**Web.** Next.js 15 (App Router), React 19, TypeScript, Tailwind 4. Supabase for Postgres, Auth, and Realtime. Drizzle ORM. `pg-boss` for the job queue, so no Redis. Cloudflare R2 for object storage with zero egress on the free tier. Deepgram async transcription with signed callbacks. Anthropic Claude via the Vercel AI SDK with Zod-validated structured output. Plyr 3.x for the player. Mailgun for the comment and first-view notification emails.

**Desktop (macOS).** Native SwiftUI app for the audio meeting notes plus a premium composite video recorder. AVAudioEngine, ScreenCaptureKit, AVAssetWriter, CIContext. Bundles Inter and JetBrains Mono. About 10k lines of Swift across capture, UI, and orphan recovery.

**Chrome extension** (`extension/`). Manifest V3. Injects a frameless `/bubble` iframe into every tab the user is on, so the camera bubble survives tab switches during a screen recording. Single source of truth for the bubble pixels.

**Deploy.** Single `node:22-alpine` container with `ffmpeg` baked in for thumbnails and preview sprites. Doppler manages env at boot. Migrations run automatically. I use [Coolify](https://coolify.io) on a $7/mo Hostinger VPS, but any Docker host works.

## Self-host Quickstart

This is the path for a friend cloning the repo and running their own Loomola.
Do not copy Ian's `.env.local`; create fresh accounts and keys.

### Easiest path: let an AI assistant walk you through it

Not a developer? You don't have to follow the steps below by hand. Open this
repository in an AI coding assistant (Claude Code, Cursor, Codex, etc.) and say:

> Help me set up my own private copy of Loomola from scratch. Follow the
> README's "Self-host Quickstart" using the Docker Compose path with a free
> Supabase project. Walk me through it one step at a time. This is my own fresh
> instance — don't push anything to the repo, and don't use anyone else's
> infrastructure (no Doppler, no Coolify, no existing domain).

The assistant will read this README and walk you through creating accounts,
filling in config, launching, and testing. Everything below is the same path
written out for humans — read on if you'd rather do it yourself.

Two choices up front:

- **Loom-only or Loom + Granola.** Start with `ENABLE_GRANOLA=false` if you only want screen recordings. Set it to `true` when you also want the macOS audio-meeting-notes product.
- **Local or deployed.** `http://localhost:3000` is enough to open the app and test auth/UI — and, with `TRANSCRIBE_PROVIDER=openai-whisper`, for the full record-to-transcript pipeline. Deepgram transcription callbacks, public share links, and social unfurls still need a public HTTPS app URL. Use a deploy, ngrok, or Cloudflare Tunnel if you want those.

**Database & auth — two options:**

- **Free Supabase cloud (default, recommended).** A free Supabase project gives you Postgres + auth in a couple of clicks, and it's what the quickstart below uses. Loomola's media (video/audio) is serv
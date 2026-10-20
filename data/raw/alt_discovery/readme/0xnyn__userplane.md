<div align="center">
<h1>Userplane</h1>
  <p><strong>The open-source Loom alternative built for customer support.</strong></p>
  
<img width="1672" height="941" alt="preview" src="https://github.com/user-attachments/assets/e99a508f-1ab3-4737-828c-ab7138fb655f" />


  <p>
    Send customers one recording link. Get back the session replay, console logs,
    network requests, customer notes, metadata, and other session details your
    team needs to resolve issues without the back-and-forth.
  </p>

  <p>
    <a href="https://userplane.io"><strong>Website</strong></a>
    |
    <a href="https://dash.userplane.io"><strong>Dashboard</strong></a>
    |
    <a href="https://docs.userplane.io"><strong>Docs</strong></a>
    |
    <a href="https://userplane.io/demo"><strong>Demo</strong></a>
    |
    <a href="https://docs.userplane.io/api/introduction"><strong>API Reference</strong></a>
    |
    <a href="#contributing"><strong>Contributing</strong></a>
  </p>
</div>

## Table of contents
https://github.com/user-attachments/assets/5e6c71b0-d139-4365-abc3-202d32a7f52f

**Product**

- [Why this exists](#why-this-exists)
- [The information gap in support](#the-information-gap-in-support)
- [How Userplane works](#how-userplane-works)
- [How Userplane compares](#how-userplane-compares)
- [What you get with a recording](#what-comes-back-with-a-recording)
- [Recording playback and analysis](#recording-playback--analysis)
- [Support workflows and integrations](#support-workflows-and-integrations)
- [Privacy, control, and trust](#privacy-control-and-trust)
- [Built for every team that touches support](#built-for-every-team-that-touches-support)

**Developer Guide**

- [Developer platform and AI debugging](#developer-platform-and-ai-debugging)
- [Repo structure](#what-lives-in-this-repo)
- [Architecture](#architecture)
- [Getting started](#getting-started)
- [Common commands](#common-commands)
- [Environment and services](#environment-and-services)

**Reference**

- [Documentation map](#documentation-map)
- [Reader paths](#reader-paths)
- [Contributing](#contributing)
- [Security](#security)
- [License](#license)

## Why this exists

https://github.com/user-attachments/assets/b1ef202b-429f-4ab4-9c05-d10e48367465

A customer reports a bug. Support asks for steps to reproduce. Customer success asks for screenshots. Engineering asks for console logs. By the time everyone has enough context to investigate, the customer has explained the same problem three different ways.

Bug reports lose the details that actually matter: what the customer saw, what they clicked, what failed, and what they expected to happen.

Userplane gives your team all of that in a single recording link. Customers record the issue in their browser and your team gets the video, console logs, network requests, user actions, metadata, and customer notes—all attached to the same recording.

## The information gap in support

https://github.com/user-attachments/assets/5aa19565-8056-4072-af58-47c4e0c3eae7

Support teams don't have a response-time problem. They have an information problem.

Most bug reports are incomplete by the time they reach the people who can fix them. Customers describe symptoms. Support tries to gather context. Engineering guesses at reproduction steps. Everyone spends more time collecting information than solving the actual issue.

Userplane eliminates that back-and-forth. When a customer encounters a problem, they record it. The recording becomes a complete case file that your team can replay, inspect, and debug without asking for screenshots, console logs, or another explanation.

## What you get with a recording

Each recording is a complete case file. Video plus the surrounding session context that makes the issue understandable and actionable.

| Context          | Why it matters                                                                   |
| :--------------- | :------------------------------------------------------------------------------- |
| Screen video     | See the exact user journey and visual state.                                     |
| Console logs     | Catch JavaScript errors, warnings, and debug output.                             |
| Network requests | Inspect failed requests, status codes, timings, and API behavior.                |
| User actions     | Follow clicks, inputs, scrolls, navigation, and interaction order.               |
| Notes            | Let the customer explain what they expected or what felt wrong.                  |
| System metadata  | Browser, OS, page URL, link, project, domain, and workspace context.             |
| Custom metadata  | Attach user IDs, account IDs, plan, flags, app version, route, or any app state. |

Support gets complete context upfront. No chasing customers for details. Engineering doesn't guess from a screenshot. Customers don't need to explain technical concepts they don't have language for.

## How Userplane works

https://github.com/user-attachments/assets/2a247499-0f98-44c4-8105-6b7e5ea44f9c



### 1. Create a recording link

![Create a Userplane recording link](apps/docs/media/links/create-link/create-link-filled.png)

Create a recording link from the dashboard, API, Chrome extension, Raycast, Intercom, Zendesk, Slack, or another support workflow. Choose the project and domain, add a ticket or customer reference, decide if the link is single-use or reusable, and send it to the customer.

![Link creation in progress](apps/docs/media/links/create-link/create-link-project-selection.png)

### 2. The customer records in browser

![Customer recording in Userplane](apps/docs/media/recorder/recording-in-progress.png)

The customer opens the link and records in their browser. No account needed. No install. No extension. They show what went wrong, add notes, and submit. Userplane captures the technical context automatically.

Recorder features: one-click start, real-time capture preview, sensitive data blur, notes and voice narration, review before upload.

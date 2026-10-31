![Reboot Syndicate — Digital Growth Studio](assets/reboot-syndicate-readme-banner.svg)

# Reboot Syndicate

**Website Design · SEO · Digital Marketing · Automation · Business Technology**

**Website:** [rebootsyndicate.com](https://rebootsyndicate.com)

Reboot Syndicate is a digital marketing and business technology studio. This repository contains the live site's FastAPI application, Jinja templates, stylesheet, service pages, and inquiry workflow.

> **GET SEEN. GET FOUND. GET GROWING.**

## What the website offers

- **Website design** — small-business websites, landing pages, redesigns, and e-commerce.
- **Search visibility** — SEO and Google Business Profile management.
- **Growth marketing** — social media, digital advertising, content, email/SMS, and reputation management.
- **Automation and analytics** — lead workflows, reporting, conversion tracking, and integrations.
- **Business technology** — hosting, domains, business systems, IT support, and computer repair.

The homepage features **14 individually linked service tiles**, each with a user-selected **starting price**. Service detail pages explain typical deliverables, FAQs, and illustrative low-end price ranges. Prices are starting estimates, not binding quotations; work is scoped and agreed upon individually.

## Technology

- **Backend:** Python, FastAPI, SQLite
- **Frontend:** Jinja2, responsive HTML/CSS
- **Hosting:** Docker Compose on a self-hosted Ubuntu server (`yeet`)
- **Routing:** Caddy reverse proxy with HTTPS
- **Lead capture:** consultation form, persistent SQLite records, private authenticated admin view
- **Notifications:** optional SMTP email alerts, enabled through private environment variables

## Deploy on `yeet`

The working directory is:

```bash
cd ~/reboot-syndicate
docker compose up -d --build website
docker compose ps
```

The Compose project may still be named `circuit-syndicate` internally. **Do not change the Compose project name casually:** existing service names and persistent database volume are associated with it.

The server currently publishes the application on port **8160** for its reverse proxy; the exact bind address is controlled by the deployment's local Compose configuration.

If you want to fetch changes from GitHub, inspect `git status` first: this server has had locally customized template, stylesheet, and Docker files. Do not blindly overwrite those files or replace the database volume during an update.

## Consultation request flow

```text
Visitor submits consultation form
          ↓
FastAPI validates the inquiry
          ↓
SQLite stores the customer request
          ↓
Visitor sees confirmation page
          ↓
Optional SMTP notification (when configured)
```

Customer requests remain in the persistent Docker data volume. Email notification failures do not erase a saved inquiry.

## Security and privacy

- Never commit `.env`, email app passwords, customer information, or SQLite database files.
- Keep the administrative inbox private; it is not intended for public internet access.
- Configure strong admin credentials and use appropriate reverse-proxy access restrictions.
- Review security and backup practices before collecting production customer information.
- Making the **GitHub repository private** controls source-code visibility but does **not** make the live website private or erase previously shared copies.

---

**Reboot Syndicate** · [rebootsyndicate.com](https://rebootsyndicate.com)

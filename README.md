# Circuit Syndicate

**Computer Repair · Networking · Tech Support**

Dark, industrial-style, mobile-responsive local repair business site with an operational repair-request form, persistent SQLite data, and an optional authenticated request dashboard.

## Deploy on yeet

```bash
cd ~/circuit-syndicate
docker compose up -d --build
```

The server listens on **127.0.0.1:8160** on `yeet`, to avoid public exposure while building.

From Fedora:

```bash
ssh -o ExitOnForwardFailure=yes -N -L 8160:127.0.0.1:8160 yeet
```

Open **http://localhost:8160/** in Fedora's browser.

## Admin requests inbox

Copy `.env.example` to `.env`, then set strong, unique `ADMIN_USER` and `ADMIN_PASSWORD`. Only after both are set will `/admin` accept HTTP Basic authentication. Restart with `docker compose up -d --force-recreate`, and open `http://localhost:8160/admin` over the SSH tunnel. The database persists in the `circuit-syndicate_requests_data` Docker volume. Never commit `.env` or customer data.

## Important before public launch

- This is a **prototype business name**, not verified registration, trademark, or domain availability.
- No actual business phone, address, reviews, prices, or business license are claimed.
- Requests are **stored locally**, not emailed. Check `/admin` to review them.
- Use a public HTTPS domain and proper authentication/CSRF protection, rate limiting, spam protection, privacy terms, and backups before enabling public access or handling real customer information. For admin, use a stronger access-control solution before public deployment.
- The application doesn't take payment or promise repair results.
- Keep the container bound to loopback until a security review.
```

Create an environment file with secure admin credentials.

```bash
cp .env.example .env
nano .env
```

Start the application:

```bash
docker compose up -d --build
```

Open http://localhost:8160/

## Security

Do not commit customer records, database files, or credentials.
Secure the admin dashboard before deploying publicly.

## Developer

Jason Edwards
https://jasonpauledwards.com

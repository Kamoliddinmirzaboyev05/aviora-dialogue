# Separate Superadmin App Design

## Context

The repo currently has:

- `frontend/` for the authenticated workspace dashboard.
- `landing/` for the public marketing site.
- A superadmin page inside `frontend/` at `/app/superadmin`.

The desired structure is three separate frontend projects:

- `landing/` - public marketing site.
- `frontend/` - workspace/admin dashboard for normal workspace operators.
- `superadmin/` - separate platform administration app.

The superadmin UI must be fully in Uzbek and use a polished visual style that is distinct from the workspace dashboard.

## Goals

- Create a separate `superadmin/` Vite React app.
- Remove the superadmin route and sidebar item from `frontend/`.
- Keep `frontend/` focused on workspace operations.
- Keep `superadmin/` focused on platform-level operations.
- Make the superadmin app UI text fully Uzbek.
- Use a refined, professional color palette for the superadmin app.
- Reuse existing backend API endpoints and permissions.

## Non-Goals

- Do not add new backend endpoints.
- Do not expose superadmin data to normal workspace users.
- Do not merge `superadmin/` into `frontend/`.
- Do not move landing content into either admin app.
- Do not commit `.env` files.

## Architecture

### Frontend Projects

The repo will contain three independent frontend apps:

- `landing/`: public product website, default local port `5174`.
- `frontend/`: workspace dashboard, default local port `5173`.
- `superadmin/`: platform administration dashboard, default local port `5175`.

Each app has its own:

- `package.json`
- `package-lock.json`
- `index.html`
- `src/`
- Vite config
- TypeScript config
- Tailwind/PostCSS config
- tests and build command

### Workspace Dashboard Changes

`frontend/` will no longer include platform superadmin functionality.

Remove:

- `/app/superadmin` route.
- `Superadmin` sidebar link.
- `frontend/src/pages/SuperadminPage.tsx`.
- `frontend/src/pages/SuperadminPage.test.tsx`.
- Superadmin API helpers and types from `frontend` if they are no longer used there.

Keep:

- Auth provider and normal workspace dashboard flows.
- Existing workspace pages: overview, Telegram, simulator, opportunities, approvals, conversations, leads, products, triggers, analytics.

### Superadmin App

`superadmin/` will be a standalone Vite React app.

Main routes:

- `/` - redirects based on auth state.
- `/signin` - superadmin sign-in page.
- `/app` - platform operations dashboard.

Auth:

- Use `/api/v1/auth/login/` for JWT login.
- Store access and refresh tokens in local storage under names scoped to this app, such as `superadminAccessToken` and `superadminRefreshToken`.
- Use `/api/v1/auth/me/` to verify the signed-in user.
- If the user is not staff or superuser, show an Uzbek access-denied state and do not fetch superadmin data.

Data:

- `GET /api/v1/superadmin/overview/`
- `GET /api/v1/superadmin/workspaces/?search=<query>`
- `GET /api/v1/superadmin/users/?search=<query>`
- `GET /api/v1/superadmin/integrations/`
- `GET /api/v1/superadmin/events/`

The backend remains the authority through `IsPlatformStaff`.

## Uzbek UI Requirements

All visible superadmin app text must be Uzbek.

Examples:

- `Superadmin` -> `Superadmin`
- `Platform Operations` -> `Platforma boshqaruvi`
- `Users` -> `Foydalanuvchilar`
- `Active workspaces` -> `Faol ish joylari`
- `Opportunities` -> `Imkoniyatlar`
- `Consent grants` -> `Roziliklar`
- `Leads` -> `Lidlar`
- `Telegram connections` -> `Telegram ulanishlari`
- `AI integration` -> `AI integratsiyasi`
- `Telegram integration` -> `Telegram integratsiyasi`
- `Workspaces` -> `Ish joylari`
- `Recent events` -> `So'nggi hodisalar`
- `Access denied` -> `Ruxsat yo'q`
- `Sign in` -> `Kirish`
- `Email` -> `Email`
- `Password` -> `Parol`
- `Signing in` -> `Kirilmoqda`

No English operational copy should remain in `superadmin/`.

## Visual Direction

The superadmin app should feel like a polished platform control room:

- Professional and calm, but visually richer than the workspace dashboard.
- Dense enough for repeated operational use.
- Clear tables, compact metric cards, and strong status signals.
- No decorative gradient orbs.
- No marketing hero layout.

Palette:

- Background: deep green-black or charcoal, paired with light panels.
- Primary accent: emerald/teal.
- Secondary accent: gold or warm amber.
- Error/status: red and amber only for operational status.
- Tables and cards should use high contrast and stable spacing.

Recommended colors:

- `ink`: `#10201c`
- `surface`: `#f5f7f2`
- `panel`: `#ffffff`
- `line`: `#d9e1d6`
- `emerald`: `#087f5b`
- `gold`: `#c58a17`
- `danger`: `#b42318`
- `muted`: `#66746d`

## Testing

`frontend/`:

- The workspace dashboard should no longer render a Superadmin nav item.
- The `/app/superadmin` route should no longer exist in the workspace app.
- Existing frontend tests and build should pass.

`superadmin/`:

- Sign-in page renders Uzbek labels and calls the login API.
- Staff users can see platform metrics and operational rows.
- Non-staff users see `Ruxsat yo'q` and no superadmin data fetch occurs.
- Main app renders Uzbek section labels.
- Build succeeds independently.

Verification commands:

- `cd frontend && npm test`
- `cd frontend && npm run build`
- `cd landing && npm test`
- `cd landing && npm run build`
- `cd superadmin && npm test`
- `cd superadmin && npm run build`

## Documentation

Update `README.md` so local app commands list:

- Landing: `cd landing && npm run dev` on `5174`.
- Workspace dashboard: `cd frontend && npm run dev` on `5173`.
- Superadmin: `cd superadmin && npm run dev` on `5175`.

The README should explain that `superadmin/` is staff-only and uses the same backend API base URL configuration pattern.


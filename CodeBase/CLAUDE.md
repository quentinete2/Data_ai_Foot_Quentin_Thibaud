# CLAUDE.md — Projet dashboard B3

> Stack alignée sur la stack Pando (Qiplim), **version cours** : on garde l'esprit, on allège pour un dashboard d'1 journée.

## Stack
- **Frontend** : React 18 + **Vite** + **TypeScript**.
  - *Note : en prod chez Pando c'est **Next.js**. Ici, une SPA servie par un seul FastAPI → Vite est le bon outil.*
- **Données serveur** : **TanStack React Query** (`useQuery` / `useMutation`) — voir `src/api.ts`. Pas de `fetch` dispersés dans des `useEffect`.
- **State local** : `useState`. Pas de state global (Zustand inutile pour ce petit app).
- **Styling** : **Tailwind CSS** + helper `cn()` (`src/lib/utils.ts`, shadcn-ready). Icônes : **lucide-react**.
- **UI** : ajouter des composants **shadcn/ui** au besoin (`npx shadcn@latest add <composant>`). Ne pas réinventer les primitives (dialog, select, tabs…).
- **Graphes** : **Recharts** (toujours dans un `<ResponsiveContainer>`).
- **Backend** : **FastAPI** (Python), modèle chargé via **joblib** depuis `backend/model.pkl`. Échanges JSON via `/api/...`.

## Commandes
- Frontend : `cd frontend && npm install && npm run dev` (port 5173) · build : `npm run build` · types : `npm run typecheck`
- Backend : `cd backend && python main.py` (port 8000)

## Conventions
- Données serveur → **React Query** ; state local → `useState`.
- Changements **chirurgicaux** ; **simplicité d'abord** ; pas de feature spéculative.
- Ne PAS réentraîner le modèle ici (on charge `model.pkl`). Commits **petits et fréquents**.
- Alias d'import : `@/` → `src/`.

## À ne pas faire
- Pas de réécriture globale d'un fichier qui marche.
- Ne pas modifier le contrat des endpoints sans le signaler.
- Pas de librairie de state global (Zustand/Redux) — inutile ici.

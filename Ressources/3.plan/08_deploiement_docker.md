# Plan D1 — Déploiement Docker

> **Pré-requis** : toutes les tâches B1–B3 et F1–F4 terminées, `model.pkl` présent dans `CodeBase/backend/`.

## Objectif

Créer un `Dockerfile` pour chaque service et un `docker-compose.yml` pour les lancer ensemble.

---

## Tâche D1-a — Dockerfile backend

**Fichier** : `CodeBase/backend/Dockerfile`

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "main.py"]
```

**Vérification** :
```bash
cd CodeBase/backend
docker build -t wc-backend .
docker run -p 8000:8000 wc-backend
# GET http://localhost:8000/api/health → {"status":"ok","model_loaded":true}
```

---

## Tâche D1-b — Dockerfile frontend

**Fichier** : `CodeBase/frontend/Dockerfile`

Build multi-stage : Node compile le React, Nginx sert le `dist/`.

```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Vérification** :
```bash
cd CodeBase/frontend
docker build -t wc-frontend .
docker run -p 80:80 wc-frontend
# Ouvrir http://localhost → dashboard visible
```

---

## Tâche D1-c — docker-compose.yml

**Fichier** : `CodeBase/docker-compose.yml`

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

---

## Tâche D1-d — Mise à jour CORS backend

Dans `CodeBase/backend/main.py`, ajouter `http://localhost` aux origines autorisées :

```python
allow_origins=["http://localhost:5173", "http://localhost"],
```

---

## Validation finale

```bash
# Depuis CodeBase/
docker-compose up --build

# Tester :
# http://localhost            → dashboard React
# http://localhost:8000/api/health → {"status":"ok","model_loaded":true}
```

## Critères de validation

- [ ] `docker-compose up --build` démarre sans erreur
- [ ] `GET http://localhost:8000/api/health` → `model_loaded: true`
- [ ] Dashboard visible sur `http://localhost`
- [ ] Formulaire de prédiction soumettable

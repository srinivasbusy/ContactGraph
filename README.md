# Contact Graph

A full-stack Android application that maps phone contacts into a **Neo4j Aura** graph database and displays connection chains up to 6 degrees of separation — similar to LinkedIn's connection degrees.

---

## Architecture

```
┌─────────────────┐        ┌──────────────────┐        ┌──────────────┐
│  Android App     │──REST──▶  Python Backend   │──Bolt──▶  Neo4j Aura   │
│  (Kotlin +       │◀──────│  (FastAPI)         │◀──────│  (Graph DB)   │
│  Jetpack Compose)│        └──────────────────┘        └──────────────┘
│                  │──WS───▶  WebSocket (Sync)  │
└─────────────────┘        └──────────────────┘
        │
        ▼
   Google Sign-In
   (Firebase Auth)
```

---

## Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.11+ |
| Android Studio | Hedgehog (2023.1.1+) |
| Docker & Docker Compose | Latest |
| Neo4j Aura account | Free tier available at [console.neo4j.io](https://console.neo4j.io) |
| Firebase project | [console.firebase.google.com](https://console.firebase.google.com) |
| Google Cloud Console | [console.cloud.google.com](https://console.cloud.google.com) |

---

## Quick Start (Backend)

### 1. Create a Neo4j Aura instance

1. Go to [console.neo4j.io](https://console.neo4j.io) → **New Instance** → choose **Free**
2. Note down:
   - **Connection URI** (e.g. `neo4j+s://xxxxxxxx.databases.neo4j.io`)
   - **Username** (default: `neo4j`)
   - **Password** (shown only once — save it!)

### 2. Create a Firebase project

1. Go to [console.firebase.google.com](https://console.firebase.google.com) → **Add project**
2. Enable **Authentication → Sign-in method → Google**
3. Note your **Project ID**

### 3. Configure the backend

```bash
cd backend
cp .env.example .env
# Edit .env with your Neo4j and Firebase credentials
```

`.env` fields:

| Variable | Description |
|----------|-------------|
| `NEO4J_URI` | Neo4j Aura connection URI |
| `NEO4J_USERNAME` | Neo4j username (default: `neo4j`) |
| `NEO4J_PASSWORD` | Neo4j password |
| `GOOGLE_CLIENT_ID` | OAuth 2.0 client ID from Google Cloud Console |
| `FIREBASE_PROJECT_ID` | Firebase project ID |
| `SECRET_KEY` | Random secret ≥ 32 chars (use `openssl rand -hex 32`) |
| `ALLOWED_ORIGINS` | CORS origins (`*` for development) |

### 4. Run the backend

**With Docker Compose (recommended):**

```bash
# From repo root
docker-compose up --build
```

**Without Docker:**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

---

## Quick Start (Android)

### 1. Get Firebase config

1. In Firebase Console → **Project Settings → Your apps → Add app → Android**
2. Package name: `com.contactgraph.app`
3. Download `google-services.json`
4. Place it at `android/app/google-services.json`

> A placeholder `android/app/google-services.json.example` is included for reference.

### 2. Configure Google Sign-In

1. In Google Cloud Console → **APIs & Services → Credentials**
2. Create an **OAuth 2.0 Client ID** for Android
3. SHA-1 fingerprint: run `./gradlew signingReport` in the `android/` directory

### 3. Set the backend URL

Edit `android/app/build.gradle.kts` → `defaultConfig` block:

```kotlin
buildConfigField("String", "BASE_URL", "\"https://your-backend-url.com\"")
```

For local development with the Android emulator, the default `http://10.0.2.2:8000` points to your machine's localhost.

### 4. Build and run

```bash
cd android
./gradlew assembleDebug
```

Or open the `android/` folder in **Android Studio** and click **Run**.

---

## API Reference

### Authentication

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/auth/google` | Verify Google ID token, create/get user |

### Contacts

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/contacts/sync` | Bulk sync contacts from device |
| `PUT` | `/api/v1/contacts/update` | Update a single contact |
| `DELETE` | `/api/v1/contacts/{phone}` | Remove contact relationship |

### Search

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/search?phone={phone}&max_depth=6` | Find connection chain |

### Network

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/network/stats` | Get network statistics |
| `GET` | `/api/v1/network/direct` | Get 1st-degree contacts |

### WebSocket

| Protocol | Path | Description |
|----------|------|-------------|
| `WS` | `/ws/sync?token={firebase_id_token}` | Real-time contact sync |

### Health

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/health` | Health check (no auth required) |

All REST endpoints (except `/auth/google` and `/health`) require:

```
Authorization: Bearer <firebase_id_token>
```

---

## Neo4j Graph Model

```
(:User {
    phone: string,       # E.164 format, e.g. +14155551234
    name: string,
    email: string,
    google_id: string,
    is_app_user: boolean,
    created_at: datetime,
    updated_at: datetime
})-[:KNOWS {
    source_user_id: string,
    contact_name: string,
    added_at: datetime
}]->(:User)
```

**Shortest-path Cypher query:**

```cypher
MATCH path = shortestPath(
    (a:User {phone: $from_phone})-[:KNOWS*1..6]-(b:User {phone: $to_phone})
)
RETURN path, length(path) AS degree
```

---

## Running Tests (Backend)

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

---

## Project Structure

```
ContactGraph/
├── android/                    # Android app (Kotlin + Jetpack Compose)
│   ├── app/
│   │   └── src/main/
│   │       ├── java/com/contactgraph/app/
│   │       │   ├── ContactGraphApplication.kt
│   │       │   ├── MainActivity.kt
│   │       │   ├── ui/           # Compose screens, components, theme
│   │       │   ├── data/         # API, models, repositories
│   │       │   ├── domain/       # Use cases
│   │       │   ├── di/           # Hilt dependency injection
│   │       │   ├── sync/         # ContentObserver + WorkManager
│   │       │   └── viewmodel/    # MVVM ViewModels
│   │       └── res/
│   └── build.gradle.kts
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── dependencies.py
│   │   ├── routers/            # auth, contacts, search, network
│   │   ├── services/           # neo4j, auth, contact, search
│   │   ├── models/             # Pydantic models
│   │   ├── websocket/          # Real-time sync handler
│   │   └── utils/              # phone_utils (E.164 normalization)
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── docker-compose.yml          # Runs backend service
├── .gitignore
└── README.md
```

---

## Features

- **Google Sign-In** with Firebase Authentication
- **Contact Sync**: opt-in dialog, bulk sync via REST, real-time updates via WebSocket, periodic background sync with WorkManager
- **Graph Search**: shortest-path query up to 6 degrees of separation
- **Visual Graph**: Canvas-based node/edge visualization, color-coded by degree
- **Breadcrumb Chain**: "You → John (1st) → Sarah (2nd) → Target (3rd)"
- **My Network**: stats (total, app users, non-users), pull-to-refresh
- **Material 3** design with dynamic theming
- **E.164** phone number normalization
- **Rate limiting** on sync and search endpoints
- **Secure token storage** using EncryptedSharedPreferences


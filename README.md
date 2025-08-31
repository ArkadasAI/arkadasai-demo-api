# ArkadasAI Demo API

This repository contains a minimal mock backend for ArkadasAI, built with
[FastAPI](https://fastapi.tiangolo.com/). It is designed for quick
deployment on hosting providers like Render or Railway and supplies
simple endpoints that simulate user authentication, plan retrieval,
chat responses and subscription upgrades. The service stores all data
in memory and resets whenever the application restarts.

## Endpoints

| Method | Path              | Description                                          |
|-------:|------------------|------------------------------------------------------|
| GET    | `/health`        | Returns service status and timestamp.               |
| POST   | `/auth/register` | Registers a new user; returns a token and user info. |
| POST   | `/auth/login`    | Logs in a user (auto‑creates if missing).            |
| GET    | `/me`            | Retrieves the current user's information.            |
| GET    | `/plans`         | Lists available subscription plans.                 |
| POST   | `/chat/send`     | Simulates sending a chat message and returns a reply |
| POST   | `/purchase/confirm` | Updates the user's subscription plan.             |

## Running Locally

```bash
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Then open your browser at [http://localhost:8000/health](http://localhost:8000/health) to confirm the service is running.

## Deploying to Render

This repository includes a `render.yaml` blueprint and `.render-start` script
to simplify deployment. After connecting your GitHub account to
[Render](https://render.com), you can deploy the service in a few clicks:

1. **New +** → **Blueprint** → select this repository.
2. Choose **Web Service**, region (e.g. `frankfurt`) and the free plan.
3. The build and start commands are provided automatically.
4. Once deployed, note the base URL and configure your Flutter app's
   `API_BASE_URL` accordingly.

## Environment Variables

No custom environment variables are required for this demo. A secret is
generated via Render's `generateValue` key in the blueprint as an example.
You can ignore it or use it to add additional secret configuration later.
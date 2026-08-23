# Stellar Objects API

A FastAPI-based REST API for managing stellar object data (stars), backed by MongoDB, with JWT authentication, pagination, Redis caching, and rate limiting built in.

## Features

- **CRUD operations** for stellar objects (create, read, update, delete)
- **JWT-based authentication** — write operations (`POST`, `PUT`, `DELETE`) require a bearer token
- **Paginated results** on `/stars` via `fastapi-pagination`
- **Filterable search** on `/stars` by name, constellation, spectral class, evolutionary stage, category, multi-star status, and whether the object has planets
- **Expanded stellar object schema** covering physical, positional, and orbital properties (mass, temperature, coordinates, companions, planets, and more)
- **Async MongoDB** integration via `pymongo`'s async client
- **Response caching** with Redis (`redis_fastapi`) for read-heavy endpoints
- **Rate limiting** per endpoint via `slowapi`
- **Auto-generated docs** through FastAPI's built-in Swagger UI (`/docs`) and ReDoc (`/redoc`)

## Tech Stack

| Component | Library |
|---|---|
| Web framework | FastAPI |
| Database | MongoDB (via `pymongo` async client) |
| Authentication | OAuth2 password flow + JWT (`pyjwt`), password hashing (`pwdlib`) |
| Pagination | `fastapi-pagination` |
| Caching | Redis (`redis_fastapi`) |
| Rate limiting | `slowapi` |
| Data validation | Pydantic |
| Server | Uvicorn |

## Project Structure

```
.
├── main.py                    # App entrypoint, routes, auth, caching, pagination & rate-limit config
├── database/
│   └── configurations.py      # MongoDB lifespan/connection setup (stars + admin users)
├── models/
│   ├── models.py               # Pydantic Star model
│   └── auth.py                 # Auth models, password hashing, JWT helpers
├── schema/
│   └── schemas.py             # Mongo document serializers (stars + users)
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.11+
- A running MongoDB instance
- A running Redis instance (required by `redis_fastapi`)

### Installation

```bash
git clone https://github.com/wildAstroboy/stellarObjectsAPI.git
cd stellarObjectsAPI
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```env
MONGODB_URI=mongodb://localhost:27017
SECRET_KEY=<your-jwt-secret-key>
ALGORITHM=HS256
```

`SECRET_KEY` should be a long, random string (e.g. generated with `openssl rand -hex 32`). `ALGORITHM` is the JWT signing algorithm passed to `pyjwt` (`HS256` is a common default).

### Running the API

```bash
python main.py
```

Or with Uvicorn directly:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at `http://127.0.0.1:8000`, with interactive docs at `http://127.0.0.1:8000/docs`.

## Authentication

Write operations (`POST`, `PUT`, `DELETE` on `/stars`) are protected with OAuth2 password flow + JWT bearer tokens. Read operations (`GET`) remain public.

1. Obtain a token from `POST /token` using `username`/`password` form fields (standard `OAuth2PasswordRequestForm`).
2. Include the returned token on subsequent requests: `Authorization: Bearer <access_token>`.
3. Tokens expire after 30 minutes.

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| POST | `/token` | Log in and receive a JWT access token | No |
| GET | `/users/me` | Get the currently authenticated user | Yes |

User records live in a separate `admin_users` MongoDB collection and passwords are hashed with `pwdlib`. There is no self-service registration endpoint — admin users are provisioned directly in the database.

## API Reference

| Method | Endpoint | Description | Auth Required | Rate Limit |
|---|---|---|---|---|
| GET | `/` | Welcome message | No | 100/day, 5/minute |
| GET | `/stars` | List stars (paginated), filterable by `name`, `constellation`, `spectral_class`, `evolutionary_stage`, `category`, `is_multi_star`, `has_planets` | No | 200/day, 20/hour |
| GET | `/stars/{star_id}` | Get a single star by ID | No | 200/day, 20/hour |
| POST | `/stars` | Add a new star (form data) | Yes | 5/minute |
| PUT | `/stars/{star_id}` | Update an existing star | Yes | 5/minute |
| DELETE | `/stars/{star_id}` | Delete a star | Yes | 10/day |

`GET` responses are cached for 300 seconds and automatically evicted from the cache on writes to keep results fresh. `GET /stars` results are paginated via `fastapi-pagination`; use the standard `page` and `size` query parameters to page through results.

### Star Object Schema

| Field | Type | Description |
|---|---|---|
| `name` | string | Star name |
| `mass` | float | Mass in solar masses (M☉) |
| `constellation` | string | Parent constellation |
| `distance_light_years` | float | Distance from Earth in light-years |
| `apparent_magnitude` | float | Apparent (observed) magnitude |
| `absolute_magnitude` | float | Absolute magnitude |
| `spectral_class` | string | Spectral classification (e.g. `G2V`) |
| `evolutionary_stage` | string | Stellar evolutionary stage (e.g. Main Sequence, Red Giant) |
| `variable_type` | string | Variable star type, if any |
| `category` | string | General category (e.g. Star) |
| `right_ascension` | string | Right ascension coordinate |
| `declination` | string | Declination coordinate |
| `temperature_kelvin` | int | Surface temperature in Kelvin |
| `surface_gravity_log_g` | float | Surface gravity (log g) |
| `rotation` | string | Rotation characteristics |
| `age_billion_years` | float, optional | Estimated age in billions of years |
| `is_multi_star` | bool | Whether the object is part of a multi-star system |
| `companion_stars` | list[string] | Names of companion stars, if any |
| `has_planets` | bool | Whether the object has a known planetary system |
| `planet_count` | int | Number of known planets |
| `planet_names` | list[string] | Names of known planets |

## License

MIT
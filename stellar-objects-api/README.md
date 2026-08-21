# Stellar Objects API

A FastAPI-based REST API for managing stellar object data (stars), backed by MongoDB, with Redis caching and rate limiting built in.

## Features

- **CRUD operations** for stellar objects (create, read, update, delete)
- **Filterable search** on `/stars` by name, constellation, spectral class, type, and category
- **Async MongoDB** integration via `pymongo`'s async client
- **Response caching** with Redis (`redis_fastapi`) for read-heavy endpoints
- **Rate limiting** per endpoint via `slowapi`
- **Auto-generated docs** through FastAPI's built-in Swagger UI (`/docs`) and ReDoc (`/redoc`)

## Tech Stack

| Component | Library |
|---|---|
| Web framework | FastAPI |
| Database | MongoDB (via `pymongo` async client) |
| Caching | Redis (`redis_fastapi`) |
| Rate limiting | `slowapi` |
| Data validation | Pydantic |
| Server | Uvicorn |

## Project Structure

```
.
├── main.py                    # App entrypoint, routes, caching & rate-limit config
├── database/
│   └── configurations.py      # MongoDB lifespan/connection setup
├── models/
│   └── stars_model.py         # Pydantic Star model
├── schema/
│   └── schemas.py             # Mongo document serializers
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
git clone https://github.com/wildAstroboy/stellar-objects-api.git
cd stellar-objects-api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```env
MONGODB_URI=mongodb://localhost:27017](MONGODB_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/stellar_info?retryWrites=true&w=majority)
```

### Running the API

```bash
python main.py
```

Or with Uvicorn directly:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at `http://127.0.0.1:8000`, with interactive docs at `http://127.0.0.1:8000/docs`.

## API Reference

| Method | Endpoint | Description | Rate Limit |
|---|---|---|---|
| GET | `/` | Welcome message | 100/day, 5/minute |
| GET | `/stars` | List stars, filterable by `name`, `constellation`, `spectral_class`, `type`, `category` | 200/day, 20/hour |
| GET | `/stars/{star_id}` | Get a single star by ID | 200/day, 20/hour |
| POST | `/stars` | Add a new star (form data) | 5/minute |
| PUT | `/stars/{star_id}` | Update an existing star | 5/minute |
| DELETE | `/stars/{star_id}` | Delete a star | 10/day |

`GET` responses are cached for 300 seconds and automatically evicted from the cache on writes to keep results fresh.

### Star Object Schema

| Field | Type | Description |
|---|---|---|
| `name` | string | Star name |
| `constellation` | string | Parent constellation |
| `distance_light_years` | float | Distance from Earth in light-years |
| `apparent_magnitude` | float | Apparent (observed) magnitude |
| `absolute_magnitude` | float | Absolute magnitude |
| `spectral_class` | string | Spectral classification (e.g. `G2V`) |
| `type` | string | Stellar type (e.g. Main Sequence, Red Giant) |
| `category` | string | General category (e.g. Star) |

## Roadmap

- [ ] Add authentication/authorization
- [ ] Pagination for `/stars`
- [ ] Additional stellar object types (planets, nebulae, etc.)
- [ ] Test suite

## License

MIT
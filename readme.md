# Interview Management Backend (FastAPI)

A **production-style backend system** built to demonstrate **real-world REST API design**, authorization, scalability, and backend engineering best practices.

This project focuses on **how professional backends are structured**, not just CRUD endpoints.

---

## Why This Project Matters

Most backend demos stop at “it works.”
This project goes further by implementing:

- Layered authorization (RBAC + resource-level access)
- Business rules (interview lifecycle)
- Pagination, indexing, and caching
- Defensive API design and error discipline

It reflects how **backend systems are built in real teams**.

---

## Tech Stack

- **FastAPI** (Python)
- **MongoDB**
- **JWT Authentication**
- **Pydantic**
- **In-memory caching**
- **MongoDB indexing**

---

## Core Capabilities

### Authentication & Authorization

- JWT-based authentication
- Role-based access control (`admin`, `interviewer`, `candidate`)
- Participant-based authorization for interview-scoped resources

> Any endpoint containing `{interview_id}` enforces resource-level access.

---

### Interview Management

- Admin creates and manages interviews
- Strict interview lifecycle:

scheduled → ongoing → completed
scheduled → cancelled

yaml
Copy code

- Role-aware state transitions enforced at the API level

---

### Participants

- Admin assigns users to interviews
- Duplicate participants are prevented
- Participants can access **only** their own interviews

---

### Messaging

- Interview-scoped messages
- Append-only design
- Participant-only access
- Paginated reads

---

## Scalability & Performance

### Pagination & Filtering

- Implemented on read-heavy endpoints
- Supports:
  - `limit`
  - `offset`
  - filtering
  - sorting

### Indexing

Optimized MongoDB queries using targeted indexes on:
- Interviews
- Participants
- Messages

### Caching

- Read-through caching on:
  - Interview list
  - Interview detail
  - Messages
- Explicit cache invalidation on write operations

Caching is added **after correctness**, following industry best practices.

---

## Error Handling

- Consistent, structured error responses
- Clear separation between:
  - authentication errors
  - authorization errors
  - business rule violations
- Correct HTTP status usage:
  - `400`
  - `401`
  - `403`
  - `404`

---

## Architecture Overview

Client
↓
FastAPI Routers
↓
Authentication & Authorization Layer
↓
Business Rules (Lifecycle, Permissions)
↓
MongoDB (Indexed)
↓
Cache (Read Optimization)

yaml
Copy code

---

## What This Project Demonstrates

- Strong understanding of **RESTful API architecture**
- Proper **authorization modeling**
- Backend **state machines & business rules**
- Awareness of **performance and scalability**
- Clean, maintainable code structure

This is **not a tutorial project** — it is a **backend engineering exercise**.

---

## Status

✅ **Complete**
All intended backend concepts have been implemented.

---

## Next Steps (Outside This Repo)

- System design & scalability discussions
- Deployment / DevOps
- Distributed caching (Redis)
- Larger-scale backend systems

---

### Recruiter Note

This project was built to **demonstrate backend engineering thinking**, architectural trade-offs, and real-world best practices — not just endpoint implementation.

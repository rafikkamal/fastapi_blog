## 🚀 Step 3 — Content Domain (Posts, Comments, Categories)

---

### ✨ Features

* **Posts** (draft/published, author-owned, timestamps)
* **Comments** (threadable replies, moderation)
* **Categories** (many-to-many with posts)

Enforce role-based permissions consistently (subscriber, editor, super_admin)

Provide pragmatic list endpoints with pagination, filters, and sorting

---

### Entities & Relationships (high-level)

## Post

Fields: title, slug, content, status (draft/published), author_id, created_at, updated_at, published_at (nullable), soft_delete flag

Relations: Post ↔ User (author, many-to-one), Post ↔ Category (many-to-many)

## Comment

Fields: post_id, author_id, body, parent_id (nullable for replies), created_at, updated_at, soft_delete flag

Relations: Comment ↔ Post (many-to-one), Comment ↔ User (author), self-relation via parent_id

## Category

Fields: name, slug, description (optional), created_at, updated_at

Relations: Category ↔ Post via a join table (e.g., post_categories)

---

### API Surface (overview)
## Posts

* POST `/api/v1/posts` — create (editor/super_admin)
* GET `/api/v1/posts` — list (public) with query params: page, size, q, status, author_id, category, sort
* GET `/api/v1/posts/{id}` — detail (published visible to all; drafts only to owner or super_admin)
* PATCH `/api/v1/posts/{id}` — update (owner editor or super_admin)
* DELETE `/api/v1/posts/{id}` — soft delete (owner editor or super_admin)
* POST `/api/v1/posts/{id}/publish` — publish (owner editor or super_admin)
* POST `/api/v1/posts/{id}/unpublish` — unpublish (owner editor or super_admin)

## Comments

* POST `/api/v1/posts/{post_id}/comments` — create (subscriber+)
* GET `/api/v1/posts/{post_id}/comments` — list (public), with page, size, optional parent_id
* DELETE `/api/v1/comments/{id}` — soft delete (super_admin OR editor if comment is under their post)

## Categories

* POST `/api/v1/categories` — create (super_admin)
* GET `/api/v1/categories` — list (public)
* PATCH `/api/v1/categories/{id}` — update (super_admin)
* DELETE `/api/v1/categories/{id}` — delete (super_admin)
* POST `/api/v1/posts/{post_id}/categories` — assign categories (super_admin or owner editor)
* DELETE `/api/v1/posts/{post_id}/categories/{category_id}` — unassign (same rule)

---

### Migrations (commands-first workflow)

Generate models & relationships (implementation step; see code later)

Autogenerate migration

```
docker compose exec app alembic revision --autogenerate -m "content: posts, comments, categories"
```


Review migration (ensure FKs, indexes, enums, join table names are correct)

Apply migration

```
docker compose exec app alembic upgrade head
```

---

### Health check

`curl http://localhost:8000/healthz`

---

### Indexes to include (guidance):

Posts: (status), (author_id), (slug unique), (published_at); optional text index fields for search (title).

Comments: (post_id), (parent_id), (created_at).

Categories: (slug unique); join table composite unique (post_id, category_id).

### List/Filter/Pagination (behavior)

Pagination: page (1-based), size (default 10, max 100)

Sorting: sort supports created_at, published_at, title with optional - prefix for desc (e.g., sort=-published_at)

Filters:

Posts: status=[draft|published], author_id, category=slug, q=search text (title contains)

Comments: optional parent_id to fetch only top-level or only replies

Validation & Constraints (business rules)

Post

title required; slug unique, derived from title (immutable once published)

status in {draft, published}

published_at set when publishing; cleared on unpublish

Only owner editor or super_admin can mutate a post

Comment

body required; parent_id must refer to a comment on the same post

Soft delete should hide body from public lists but keep record for audit

Category

name required; slug unique (lowercase, kebab-case)

Deleting a category removes links but not posts

Seeding (optional for demo data)

Add a simple content seeder for:

A couple of categories (e.g., python, fastapi)

Sample posts (draft + published) authored by the existing editor

A few comments (top-level and replies)

Run (after implementation):

```
docker compose exec app python -m app.seeds.seed_content
```

Testing Plan (commands & scope)

Unit tests (permissions, slugify, pagination math)

Integration tests (with a test DB)

Creating posts as editor vs subscriber (expect 403 for subscriber)

Editing another user’s draft as editor (expect 403)

Publishing/unpublishing flows (timestamps)

Comment creation and nested replies

Category assignment and filter by category

Commands:

# (after tests are added)
```
docker compose exec app pytest -q
```

Acceptance Criteria (definition of done)

Migrations apply cleanly on a fresh DB and on an existing Step 2 DB.

All endpoints return expected HTTP codes based on role matrix.

Public listings return only published posts by default.

Draft access is restricted to the owning editor and super_admin.

Soft-deleted `posts/comments` never appear in public listings.

Categories can be `created/updated/deleted` by super_admin and assigned to posts by owner editor or super_admin.

Pagination and sorting behave predictably (consistent totals and ordering).

Operational Notes

Keep echo=False for production-like runs; enable it temporarily when debugging SQL.

Add OpenAPI examples for each endpoint for clearer Swagger docs.

Consider response caching for GET `/posts` once content grows.
# AI-Assisted Box Selection System

A robust, production-grade Python/Django solution for e-commerce fulfillment packaging optimization. The system automates warehouse packaging decisions by determining the **cheapest feasible shipping box** that safely accommodates an order's products, respecting physical 3D dimensions, spatial rotations, and weight limits.

---

## 1. System Architecture

The project strictly follows the **Service Layer Pattern** to decouple business logic from HTTP presentation and database schemas:

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│    Django Templates + Forms / Views (HTTP & Session Handling)│
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                       Service Layer                         │
│  • BoxSelectorService (Orchestrator & Cost Optimization)    │
│  • PackingEngine (Pure Python 3D Geometric Placement)       │
│  • PackingAdvisor (Diagnostics & Warehouse Reasoning)       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     Persistence Layer                       │
│     Django ORM Models (Product, ShippingBox, Order, Items)  │
│     Database Constraints & Validations (db.sqlite3)         │
└─────────────────────────────────────────────────────────────┘
```

* **`fulfillment/models/`**: Defines relational entities with `DecimalField` precision, database-level `CheckConstraint`, and model-level `clean()` methods.
* **`fulfillment/services/packing_engine.py`**: Pure Python 3D bin packing engine implementing First-Fit Decreasing (FFD) with Extreme Point (Anchor) coordinate tracking and 6-axis orthogonal rotation testing.
* **`fulfillment/services/box_selector.py`**: Coordinates pre-filtering, cost-ascending evaluation, and tie-breaking.
* **`fulfillment/services/packing_advisor.py`**: Generates transparent reasons for selection and actionable diagnostics when orders cannot fit in standard cartons.
* **`fulfillment/views/` & `templates/`**: Responsive warehouse packer interface styled with Tailwind CSS.

---

## 2. Core Box Selection Algorithm

### Multi-Stage Filter-and-Verify Heuristic
1. **Stage 1: Fast $O(1)$ Pre-Filters**
   * **Weight Filter:** $\sum W_{items} \le W_{box, max}$.
   * **Volume Filter:** $\sum V_{items} \le V_{box, internal}$.
   * **Max Dimension Filter:** For every item, its sorted dimensions $(l \le w \le h)$ must be $\le$ box sorted dimensions $(L \le W \le H)$.
2. **Stage 2: Cost-Ascending Ranking**
   * Candidate boxes are sorted primarily by `cost ASC`, with a secondary tie-breaker on `internal_volume ASC` (tightest fit / minimal void space).
3. **Stage 3: 3D Coordinate Simulation**
   * Evaluates candidates starting from the cheapest.
   * **The very first candidate that passes 3D coordinate placement is returned immediately**, mathematically guaranteeing the lowest packaging cost.

### Why Volume Alone is Insufficient (Interview Discussion)
Checking total volume assumes solid goods behave like liquids or sand. A $100\text{ cm}$ pole has a volume of only $400\text{ cm}^3$, but will never fit in a $10 \times 10 \times 10\text{ cm}$ cube box ($1,000\text{ cm}^3$). Our `PackingEngine` ensures collision-free 3D coordinate placement with non-overlapping bounding extents.

---

## 3. Quickstart & Installation

### Prerequisites
* Python 3.10+ (tested on Python 3.14)

### Setup Instructions

1. **Activate Virtual Environment:**
   ```bash
   # Windows PowerShell:
   .\.venv\Scripts\Activate.ps1
   # macOS/Linux:
   source .venv/bin/activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install django
   ```

3. **Run Migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Seed Sample Warehouse Catalog (1-Click):**
   ```bash
   python manage.py populate_catalog
   ```

5. **Start Development Server:**
   ```bash
   python manage.py runserver
   ```
   Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## 4. Running Automated Tests

A comprehensive 24-test suite covers:
* Database constraints, negative value validations, and decimal calculations.
* 3D spatial rotation permutations and non-overlapping coordinate checks.
* Cost-ascending selection, weight limit rejection, and tie-breakers.
* HTTP view workflows and redirects.

Execute the test suite:
```bash
python manage.py test fulfillment.tests
```

---

## 5. Default Credentials

* **Django Admin:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
  * Username: `admin`
  * Password: `admin123`


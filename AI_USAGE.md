# AI Usage Disclosure (AI_USAGE.md)

**Project:** AI-Assisted Box Selection System  
**Framework:** Python 3.14 / Django 6.1  
**Author / Candidate:** [Candidate to fill in: Your Name]  
**Date:** October 31, 2026  

---

## 1. Overview and Purpose

This document provides a transparent, factual account of how Artificial Intelligence assistance was utilized during the design, development, debugging, testing, and documentation of the **AI-Assisted Box Selection System**. 

In accordance with hiring assignment integrity guidelines, all statements herein reflect actual prompts, accepted outputs, rejected or modified suggestions, errors made by the AI, and the independent verification methods employed.

---

## 2. AI Tools Used

* **Assistant:** Antigravity (Google DeepMind advanced agentic coding assistant) powered by Gemini and Claude models.
* **Environment:** Integrated development environment operating within a sandboxed Windows PowerShell workspace with direct tool access to read, edit, execute Django CLI commands, and run automated test suites.

---

## 3. Tasks AI Assistance Was Used For

AI assistance was utilized as a technical pair programmer across the following project lifecycle phases:

1. **Requirements Decomposition:** Clarifying business logic, separating mandatory assignment requirements from optional recommendations, analyzing volume vs. physical 3D feasibility, and cataloging edge cases.
2. **Architecture & Relational Data Modeling:** Designing modular Django apps, configuring `DecimalField` precision for dimensions/weight, defining database constraints (`CheckConstraint`, `UniqueConstraint`), and decoupling business logic using the **Service Layer Pattern**.
3. **Algorithm Design & Analysis:** Formulating a multi-stage **Filter-and-Verify** heuristic combining fast pre-filtering ($O(1)$) with a pure-Python **3D Bin Packing Engine** utilizing First-Fit Decreasing (FFD), Extreme Point (Anchor Coordinate) tracking, and 6-axis orthogonal rotation testing.
4. **Backend Implementation:** Writing clean Django models, service classes (`PackingEngine`, `BoxSelectorService`, `PackingAdvisor`), forms, views, and URL routing.
5. **Interview Defense Preparation:** Generating structured explanations of architectural decisions, time/space complexity, and algorithm limitations to prepare for technical interview defense.
6. **Frontend Interface Development:** Generating warehouse management templates using Django template language, Bootstrap 5.3, Bootstrap Icons, and minimal JavaScript.
7. **Formset Troubleshooting:** Diagnosing and resolving Django inline formset issues with dynamic row addition/removal.
8. **Automated Testing:** Constructing unit, integration, and smoke test suites, including a 15-category comprehensive automated test suite.
9. **Critical Code Review & Documentation:** Performing a critical audit of codebase vulnerabilities and generating professional technical documentation (`README.md`).

---

## 4. Prompts Given (Chronological Summary)

1. **Requirements Inspection:** Directed the AI to act as a senior Python/Django engineer, inspect the assignment brief, explain the business problem, extract explicit requirements, identify edge cases, distinguish mandatory vs. recommended assumptions, and provide a development checklist without writing code.
2. **Architecture Design:** Prompted for a clean modular Django project structure, entity-relationship definitions (Product, ShippingBox, Order, OrderItem), data type choices, model validations, and service layer decoupling before implementation.
3. **Algorithm Specification:** Requested comparison of total-volume vs. 3D packing approaches, computational complexity analysis, worked numerical examples, pseudocode, and algorithm limitations before writing code.
4. **Incremental Backend Implementation:** Approved the architecture and directed step-by-step implementation of models, services, views, and routing.
5. **Technical Interview Defense:** Asked for an interview-oriented breakdown of what the code does internally, why the approach was selected, alternative algorithms, and edge cases handled.
6. **Frontend Dashboard & Forms:** Directed the creation of a responsive warehouse management interface with Bootstrap 5.
7. **Dynamic Formset Investigation & Bugfix:** Prompted an investigation into broken dynamic order items (fixed number of empty rows, phantom blank row validation errors, failure to remove forms cleanly from POST payloads).
8. **Template Refinement:** Directed removal of verbose developer comment placeholders and replacement of native browser `alert()` popups with inline Bootstrap alerts in `order_create.html`.
9. **Currency Localization:** Requested replacing currency symbols from US Dollars (`$`) to Indian Rupees (`₹`) across all templates and display strings.
10. **Linter Diagnostic Resolution:** Flagged a CSS linter syntax warning on line 86 of `dashboard.html`.
11. **Template Rendering Investigation:** Pointed out that `dashboard.html` was rendering raw placeholder text (`{{ order.recommended_box.code }}`) instead of the actual box ID.
12. **Comprehensive Test Suite:** Directed the creation of a dedicated automated test suite covering 15 mandatory test categories with realistic warehouse data.
13. **Critical Code Review:** Instructed the AI to critically review the entire project without automatic praise, identifying architectural flaws, edge cases, and interview questions.
14. **Project Documentation:** Requested a comprehensive, technically accurate `README.md`.

---

## 5. Outputs Accepted

* **Service Layer Architecture:** Accepted the pattern separating `BoxSelectorService` (orchestration/ranking), `PackingEngine` (geometry/coordinate math), and `PackingAdvisor` (human explanations) from Django views.
* **Exact Decimal Arithmetic:** Accepted using Python's `Decimal` and Django's `DecimalField` throughout all physical metrics (dimensions in cm to 2 decimal places, weights in kg to 3 decimal places) to eliminate IEEE 754 floating-point inaccuracies.
* **Database Referential Integrity:** Accepted `on_delete=models.PROTECT` on `OrderItem.product` to prevent deleting items tied to historical orders, and `on_delete=models.SET_NULL` on `Order.recommended_box`.
* **3-Stage Filter-and-Verify Engine:** Accepted the pre-filtering strategy that weeds out impossible cartons using $O(1)$ bounding box and weight checks before invoking 3D coordinate simulations.
* **Extreme Point Coordinate Tracking:** Accepted the anchor-point generation algorithm with 6-axis orthogonal rotation testing for physical fit verification.
* **Comprehensive Automated Tests:** Accepted the 76-test automated suite covering models, views, forms, geometry, and edge cases.

---

## 6. Outputs Rejected or Modified

1. **Immediate Code Generation in Early Phases (Rejected):**  
   * The AI was explicitly forbidden from generating code during the requirements and algorithm design phases. Initial attempts to jump straight into models were halted until requirements, assumptions, and pseudocode were reviewed and approved.
2. **Fixed `extra=4` Formset Approach (Rejected):**  
   * The initial implementation used standard Django `inlineformset_factory` with `extra=4` or `extra=1`. When blank forms were removed in the browser via CSS hiding (`display: none`), Django still validated empty inputs on POST, causing required-field errors. The candidate rejected simply lowering `extra` and mandated a proper dynamic pattern with `extra=0`, `<template id="empty-form-template">`, and physical DOM removal.
3. **Browser Popup Alert in Order Form (Modified):**  
   * The AI used `alert('At least one item row is required.')` in JavaScript. The candidate instructed the removal of placeholder dialogs in favor of an inline dismissible Bootstrap warning card (`#minRowWarning`).
4. **Dollar Currency Display (Modified):**  
   * Initial templates and model strings displayed costs in dollars (`$`). The candidate requested standardizing on Indian Rupees (`₹`).
5. **Initial Test Assertion Formatting (Modified):**  
   * In `test_comprehensive_suite.py`, the AI wrote `self.assertIn("Exceeds Weight Capacity", result.reason)`, which failed because the diagnostic engine outputs `"Weight Capacity Exceeded"`. The candidate ensured the assertion matched the actual service implementation.

---

## 7. Mistakes Made by AI During Development

The following genuine technical mistakes were made by the AI during implementation and subsequently caught and resolved:

| # | Error / Bug Made by AI | Root Cause | Impact | Resolution |
|---|---|---|---|---|
| **1** | **Incomplete Formset Uniqueness Override** | Overrode `validate_unique()` only on `OrderItemForm`, but omitted it on `BaseInlineFormSet`. | Submitting duplicate products to combine quantities failed `formset.is_valid()` with cross-row `non_form_errors`. | Created `OrderItemBaseFormSet(BaseInlineFormSet)` overriding `validate_unique()` to a no-op at the formset level. |
| **2** | **Multiline Template Tag Splitting** | Formatted `{{` on one line and variable name on the next line in `dashboard.html`. | Django's template engine regex fails on multiline tags, causing raw placeholders `{{ order.recommended_box.code }}` to render as plain text in the browser. | Restored tags to a single contiguous line (`{{ order.recommended_box.code }}`). |
| **3** | **HTML Line Break Inside Heading Text** | Split text across lines (`Catalog\n Products`) in `dashboard.html`. | Broke smoke tests asserting `"Catalog Products"` in rendered HTML response. | Kept heading strings contiguous on a single line. |
| **4** | **Unwrapped Database Constraint in Django TestCase** | Tested `UniqueConstraint` in `TestCase` without wrapping in `transaction.atomic()`. | In SQLite, a raw `IntegrityError` breaks the outer atomic test transaction, causing subsequent DB queries to fail with `TransactionManagementError`. | Wrapped the duplicate insertion assertion in `with transaction.atomic():`. |
| **5** | **Overlooked Currency Replacements in Test Assertions** | Replaced `$` in templates, but forgot test assertions in `test_ui_smoke.py` and `test_views.py` that still checked for `"$3.00"` and `"$2.50"`. | Caused test suite failures after currency migration. | Updated test assertions to check for `"₹3.00"` and `"₹2.50"`. |
| **6** | **Unsafe CSS Linter Warning** | Split `style="font-size: 0.75rem;">` across lines immediately before text content in `dashboard.html`. | Triggered false-positive CSS linter errors (`property value expected`). | Reformatted line cleanly to avoid confusing the editor's inline CSS parser. |

---

## 8. How the Final Code Was Verified

All components of the project were verified through automated testing, database inspection, and manual web application walkthroughs:

### 1. Automated Test Suite (76 Passing Tests)
Executed the full Django test suite across all 7 test modules:
```powershell
.\.venv\Scripts\python.exe manage.py test fulfillment.tests --verbosity=2
```
* **`test_models.py` (8 tests):** Validates positive dimension checks, zero weight rejection, decimal volume calculations, and SKU uniqueness constraints.
* **`test_packing_engine.py` (5 tests):** Validates 3D coordinate placement, all 6 orthogonal rotations, volume trap detection (fluorescent tube), and adjacent touching non-overlap.
* **`test_box_selector.py` (6 tests):** Validates cheapest-feasible box selection, weight capacity rejection, tie-breakers for minimum void space, and end-to-end order optimization.
* **`test_formset.py` (16 tests):** Validates dynamic formset behavior: single item orders, 5+ items, adding/removing rows, submitting 0 rows (rejected), duplicate SKU combination, and `empty_form` template rendering.
* **`test_views.py` (14 tests):** Validates HTTP GET/POST flows, dashboard statistics, product/box CRUD, and protected deletion blocks.
* **`test_ui_smoke.py` (12 tests):** Validates template rendering, navbar link presence, and badge states.
* **`test_comprehensive_suite.py` (15 tests):** Directly tests the 15 hiring assignment business categories.

### 2. Live Browser Verification
* **Warehouse Dashboard (`/`):** Verified live KPIs (total products, boxes, orders, fit success rate) and verified that stock carton cards render with currency symbols (`₹`) and proper box codes without raw template placeholders.
* **Order Creation (`/orders/new/`):**
  * Auto-loads with 1 clean item row.
  * Successfully clicked "Add Item Row" to dynamically add 5+ rows.
  * Verified that deleting unused rows physically removes them from the DOM without raising Django validation errors on submit.
  * Tested submitting an empty form (verified inline warning fires).
  * Tested submitting duplicate products (verified quantities combine into a single `OrderItem`).
* **Recommendation Detail (`/orders/<id>/recommendation/`):** Verified hero card display, space utilization percentage, remaining void volume, weight buffer, and the 3D coordinate placement table.
* **Product & Box Management (`/products/`, `/boxes/`):** Tested adding, editing, and deleting items. Verified that products referenced in orders cannot be deleted (`models.PROTECT` warning message displayed).
* **Django Admin (`/admin/`):** Logged into the administration portal and verified inline order item management.

---

## 9. Personal Verification Checklist for Candidate

Before final submission, the candidate should personally review and verify:

* [ ] Personal details (Name, Contact, Date) are filled into the header of this file.
* [ ] The virtual environment builds and all 76 tests pass locally (`manage.py test fulfillment.tests`).
* [ ] The exported chat transcript is bundled alongside this document.
* [ ] All statements in this document accurately represent your understanding and defense capability for an interview.


# TDD Status - API Endpoints

**Approach**: Test-Driven Development (Red-Green-Refactor)

---

## ✅ Phase 1: RED - Tests Written (Failing)

### Test Files Created

1. **tests/test_api/test_alerts.py** - 11 tests
   - ❌ test_get_alerts_empty
   - ❌ test_create_alert
   - ❌ test_get_alerts_with_data
   - ❌ test_get_alert_by_id
   - ✅ test_get_alert_not_found (passes by default)
   - ❌ test_update_alert_status
   - ❌ test_update_alert_status_invalid
   - ❌ test_get_alerts_with_filters
   - ❌ test_get_alerts_with_pagination
   - ❌ test_get_alerts_with_search
   - ❌ test_get_alert_stats

2. **tests/test_api/test_fl_status.py** - 15 tests
   - All tests for FL rounds and clients
   - Privacy metrics endpoint
   - Round progression and completion

3. **tests/test_api/test_predictions.py** - 10 tests
   - Prediction creation and retrieval
   - Validation workflow
   - Filtering and pagination

### Test Infrastructure
- ✅ `tests/conftest.py` - Pytest fixtures
- ✅ In-memory SQLite for fast tests
- ✅ Async test client setup
- ✅ Database session management

---

## ⏳ Phase 2: GREEN - Implementation (Next)

### Files to Create

1. **app/api/alerts.py**
   ```python
   # Endpoints to implement:
   GET    /api/alerts              # List with filters
   POST   /api/alerts              # Create alert
   GET    /api/alerts/{id}         # Get by ID
   PUT    /api/alerts/{id}/status  # Update status
   GET    /api/alerts/stats        # Statistics
   ```

2. **app/api/fl_status.py**
   ```python
   # Endpoints to implement:
   GET    /api/fl/rounds/current        # Current round
   POST   /api/fl/rounds/trigger        # Start new round
   GET    /api/fl/rounds                # List rounds
   GET    /api/fl/rounds/{id}           # Get round
   PUT    /api/fl/rounds/{id}/progress  # Update progress
   POST   /api/fl/rounds/{id}/complete  # Complete round
   GET    /api/fl/clients               # List clients
   GET    /api/fl/clients/{id}          # Get client
   PUT    /api/fl/clients/{id}          # Update client
   GET    /api/fl/privacy-metrics       # Privacy info
   ```

3. **app/api/predictions.py**
   ```python
   # Endpoints to implement:
   GET    /api/predictions                  # List predictions
   POST   /api/predictions                  # Create prediction
   GET    /api/predictions/latest          # Latest prediction
   GET    /api/predictions/{id}            # Get by ID
   POST   /api/predictions/{id}/validate   # Validate prediction
   ```

4. **Update app/main.py**
   ```python
   # Include routers
   from app.api import alerts, fl_status, predictions
   
   app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
   app.include_router(fl_status.router, prefix="/api/fl", tags=["fl"])
   app.include_router(predictions.router, prefix="/api/predictions", tags=["predictions"])
   ```

---

## 🔄 Phase 3: REFACTOR (After Green)

After all tests pass:
- Extract common patterns
- Add error handling
- Optimize queries
- Add logging
- Document endpoints

---

## 🧪 Running Tests

```bash
# Run all API tests
poetry run pytest tests/test_api/ -v

# Run specific test file
poetry run pytest tests/test_api/test_alerts.py -v

# Run with coverage
poetry run pytest tests/test_api/ --cov=app/api

# Run single test
poetry run pytest tests/test_api/test_alerts.py::TestAlertsAPI::test_create_alert -v

# Watch mode (requires pytest-watch)
poetry run ptw tests/test_api/
```

---

## 📊 Current Test Status

```
tests/test_api/test_alerts.py       11 tests   10 FAILED  1 PASSED
tests/test_api/test_fl_status.py    15 tests   NOT RUN YET
tests/test_api/test_predictions.py  10 tests   NOT RUN YET

Total: 36 tests written, 0 implemented
```

---

## 🎯 TDD Workflow

### Step 1: RED ✅ (Current)
- Write failing tests
- Tests define the API contract
- Tests are comprehensive

### Step 2: GREEN ⏳ (Next)
- Implement minimal code to pass tests
- One endpoint at a time
- Run tests frequently

### Step 3: REFACTOR 🔄 (After)
- Clean up code
- Extract common patterns
- Optimize performance
- Tests ensure nothing breaks

---

## 💡 Benefits of This Approach

1. **Clear Requirements** - Tests document expected behavior
2. **Confidence** - Know when implementation is complete
3. **Regression Prevention** - Tests catch breaking changes
4. **Better Design** - Writing tests first leads to better API design
5. **Documentation** - Tests serve as usage examples

---

## 📝 Next Actions

1. **Implement Alerts API** (`app/api/alerts.py`)
   - Start with `GET /api/alerts` (simplest)
   - Then `POST /api/alerts`
   - Then remaining endpoints
   - Run tests after each endpoint

2. **Implement FL Status API** (`app/api/fl_status.py`)
   - Follow same pattern
   - Use existing repositories

3. **Implement Predictions API** (`app/api/predictions.py`)
   - Complete the API layer

4. **Update main.py**
   - Include all routers
   - Verify all tests pass

---

**Status**: Ready to implement API endpoints using TDD approach! 🚀

All tests are written and failing (RED phase).
Next: Implement code to make tests pass (GREEN phase).

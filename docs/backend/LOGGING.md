# Logging Guide

This guide explains how to use the logging system in the PriceTracker backend application.

## Overview

The logging system is designed to be production-ready and fully compatible with Docker and container orchestration platforms. It provides structured JSON logging for machine parsing and integration with log aggregation systems like ELK, Splunk, or CloudWatch.

## Features

- ✅ **JSON-structured logging** - Machine-parseable logs for aggregation systems
- ✅ **Docker-compatible** - Logs to stdout/stderr (no file logging)
- ✅ **Request tracking** - Automatic request ID generation and tracking
- ✅ **Configurable** - Control log level and format via environment variables
- ✅ **Exception tracking** - Full stack traces for errors
- ✅ **Performance metrics** - Automatic request duration logging

## Configuration

Configure logging behavior using environment variables in your `.env` file:

```bash
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Use JSON format (true for production/Docker, false for local dev)
USE_JSON_LOGS=true
```

### Log Levels

- **DEBUG** - Detailed information for diagnosing problems
- **INFO** - General informational messages (default)
- **WARNING** - Warning messages for potentially harmful situations
- **ERROR** - Error messages for serious problems
- **CRITICAL** - Critical messages for very serious errors

## Basic Usage

### Import and Create Logger

```python
from app.config.logger import get_logger

logger = get_logger(__name__)
```

### Simple Logging

```python
# Info message
logger.info("User login successful")

# Warning message
logger.warning("API rate limit approaching")

# Error message
logger.error("Database connection failed")

# Debug message (only shown when LOG_LEVEL=DEBUG)
logger.debug("Processing item with ID: 12345")
```

### Structured Logging with Extra Fields

Add custom fields to your logs using the `extra` parameter:

```python
logger.info(
    "Product price updated",
    extra={
        "product_id": 12345,
        "old_price": 29.99,
        "new_price": 24.99,
        "currency": "USD"
    }
)
```

### Exception Logging

Log exceptions with full stack traces:

```python
try:
    result = scrape_product(url)
except Exception as exc:
    logger.error(
        "Scraping failed",
        extra={"url": url, "product_id": product_id},
        exc_info=True  # Include stack trace
    )
    raise
```

## FastAPI Integration

The logger is automatically integrated with your FastAPI application through middleware.

### Automatic Request Logging

All HTTP requests are automatically logged with:
- Unique request ID
- HTTP method and path
- Client IP address
- Status code
- Request duration in milliseconds

Example log output:
```json
{
  "timestamp": "2025-12-14T10:30:45.123456+00:00",
  "level": "INFO",
  "logger": "app.main",
  "message": "Request completed",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "method": "GET",
  "path": "/api/products/123",
  "status_code": 200,
  "duration_ms": 45.32
}
```

### Request ID in Headers

Every response includes an `X-Request-ID` header that matches the request ID in the logs. Use this for tracing requests across services.

### Using Logger in Route Handlers

```python
from fastapi import APIRouter
from app.config.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.get("/products/{product_id}")
async def get_product(product_id: int):
    logger.info("Fetching product", extra={"product_id": product_id})
    
    try:
        product = await fetch_product(product_id)
        logger.info("Product fetched successfully", extra={"product_id": product_id})
        return product
    except ProductNotFound:
        logger.warning("Product not found", extra={"product_id": product_id})
        raise HTTPException(status_code=404, detail="Product not found")
    except Exception as exc:
        logger.error(
            "Failed to fetch product",
            extra={"product_id": product_id},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")
```

## Docker Integration

### JSON Log Format

When `USE_JSON_LOGS=true` (default), logs are formatted as JSON for easy parsing:

```json
{
  "timestamp": "2025-12-14T10:30:45.123456+00:00",
  "level": "INFO",
  "logger": "app.scraper",
  "message": "Scraping completed",
  "module": "scraper",
  "function": "scrape_prices",
  "line": 45,
  "product_count": 150,
  "duration_seconds": 12.5
}
```

### Viewing Logs in Docker

```bash
# View all logs
docker logs pricetracker-backend

# Follow logs in real-time
docker logs -f pricetracker-backend

# View last 100 lines
docker logs --tail 100 pricetracker-backend

# View logs with timestamps
docker logs -t pricetracker-backend
```

### Log Aggregation

The JSON format integrates seamlessly with log aggregation systems:

**Docker Logging Drivers:**
```yaml
# docker-compose.yml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

**ELK Stack:**
```yaml
services:
  backend:
    logging:
      driver: "gelf"
      options:
        gelf-address: "udp://logstash:12201"
```

## Development vs Production

### Development (Human-Readable Logs)

For local development, use colored console output:

```bash
# .env
LOG_LEVEL=DEBUG
USE_JSON_LOGS=false
```

Output:
```
2025-12-14 10:30:45 - app.main - INFO - Request completed
2025-12-14 10:30:46 - app.scraper - WARNING - Rate limit approaching
2025-12-14 10:30:47 - app.db - ERROR - Connection timeout
```

### Production (JSON Logs)

For production/Docker, use structured JSON:

```bash
# .env
LOG_LEVEL=INFO
USE_JSON_LOGS=true
```

## Best Practices

### 1. Use Appropriate Log Levels

```python
# ✅ Good
logger.debug("Starting loop iteration", extra={"index": i})
logger.info("User registered", extra={"user_id": user.id})
logger.warning("Cache miss", extra={"key": cache_key})
logger.error("Payment processing failed", extra={"order_id": order_id}, exc_info=True)

# ❌ Avoid
logger.info("Loop iteration", extra={"index": i})  # Too verbose for INFO
logger.error("User not found")  # Use WARNING instead
```

### 2. Include Context with Extra Fields

```python
# ✅ Good - includes context
logger.info("Scraping started", extra={
    "url": product_url,
    "product_id": product_id,
    "retry_count": retry_count
})

# ❌ Avoid - no context
logger.info("Scraping started")
```

### 3. Log Exceptions Properly

```python
# ✅ Good - includes stack trace
try:
    process_order(order_id)
except Exception as exc:
    logger.error("Order processing failed", extra={"order_id": order_id}, exc_info=True)
    raise

# ❌ Avoid - loses stack trace
except Exception as exc:
    logger.error(f"Order processing failed: {exc}")
```

### 4. Use Structured Data

```python
# ✅ Good - structured
logger.info("Price changed", extra={
    "product_id": 123,
    "old_price": 29.99,
    "new_price": 24.99
})

# ❌ Avoid - string formatting
logger.info(f"Price changed from {old_price} to {new_price} for product {product_id}")
```

### 5. Don't Log Sensitive Data

```python
# ✅ Good
logger.info("User authenticated", extra={"user_id": user.id})

# ❌ Avoid - logs sensitive data
logger.info("User authenticated", extra={
    "user_id": user.id,
    "password": user.password,  # ⚠️ Security risk!
    "credit_card": card_number   # ⚠️ PCI violation!
})
```

### 6. Keep Messages Concise

```python
# ✅ Good
logger.info("Product scraped", extra={"product_id": 123, "price": 29.99})

# ❌ Avoid - too verbose
logger.info("Successfully completed the scraping operation for product with ID 123 and found the price to be $29.99")
```

## Advanced Usage

### Custom Request Context

Add user information to request logs:

```python
from app.config.logger import RequestContextFilter

@router.get("/profile")
async def get_profile(request: Request, current_user: User = Depends(get_current_user)):
    # Add user context to logs
    request_filter = RequestContextFilter(
        request_id=request.state.request_id,
        user_id=current_user.id
    )
    logger.addFilter(request_filter)
    
    logger.info("Fetching user profile")
    # Logs will now include user_id automatically
    
    return current_user.profile
```

### Performance Monitoring

```python
import time

def scrape_products(urls: list[str]):
    start_time = time.time()
    
    logger.info("Starting bulk scrape", extra={"url_count": len(urls)})
    
    results = []
    for url in urls:
        try:
            result = scrape_single_product(url)
            results.append(result)
        except Exception as exc:
            logger.error("Scraping failed", extra={"url": url}, exc_info=True)
    
    duration = time.time() - start_time
    logger.info("Bulk scrape completed", extra={
        "url_count": len(urls),
        "success_count": len(results),
        "duration_seconds": round(duration, 2),
        "avg_time_per_url": round(duration / len(urls), 2)
    })
    
    return results
```

## Troubleshooting

### Logs Not Appearing

1. Check log level: Set `LOG_LEVEL=DEBUG` to see all logs
2. Verify settings are loaded: Add `print(get_settings())` in startup
3. Check Docker logs: `docker logs <container-name>`

### Too Many Logs

1. Increase log level to `WARNING` or `ERROR`
2. Suppress third-party loggers (already configured for urllib3, asyncio)
3. Add custom filters for specific modules

### JSON Parsing Errors

Ensure `USE_JSON_LOGS=true` (not `"true"` with quotes) in your `.env` file. Boolean values should be lowercase true/false.

## Examples

### Complete Route Example

```python
from fastapi import APIRouter, HTTPException, Depends
from app.config.logger import get_logger
from app.models import Product, ProductCreate
from app.database import get_db

router = APIRouter(prefix="/api/products", tags=["products"])
logger = get_logger(__name__)

@router.post("/", response_model=Product)
async def create_product(product: ProductCreate, db = Depends(get_db)):
    logger.info("Creating new product", extra={"name": product.name})
    
    try:
        new_product = Product(**product.dict())
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        
        logger.info("Product created successfully", extra={
            "product_id": new_product.id,
            "name": new_product.name,
            "price": new_product.price
        })
        
        return new_product
        
    except IntegrityError as exc:
        logger.warning("Product already exists", extra={"name": product.name})
        raise HTTPException(status_code=409, detail="Product already exists")
        
    except Exception as exc:
        logger.error("Failed to create product", extra={"name": product.name}, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Background Task Example

```python
from fastapi import BackgroundTasks
from app.config.logger import get_logger

logger = get_logger(__name__)

def scrape_prices_background(product_ids: list[int]):
    logger.info("Background scraping started", extra={"product_count": len(product_ids)})
    
    for product_id in product_ids:
        try:
            scrape_product_price(product_id)
            logger.debug("Product scraped", extra={"product_id": product_id})
        except Exception as exc:
            logger.error(
                "Background scraping failed",
                extra={"product_id": product_id},
                exc_info=True
            )
    
    logger.info("Background scraping completed", extra={"product_count": len(product_ids)})

@router.post("/scrape")
async def trigger_scrape(product_ids: list[int], background_tasks: BackgroundTasks):
    logger.info("Scheduling background scrape", extra={"product_count": len(product_ids)})
    background_tasks.add_task(scrape_prices_background, product_ids)
    return {"message": "Scraping scheduled", "product_count": len(product_ids)}
```

## Reference

### Logger Methods

- `logger.debug(msg, extra=None, exc_info=False)` - Debug information
- `logger.info(msg, extra=None, exc_info=False)` - Informational messages
- `logger.warning(msg, extra=None, exc_info=False)` - Warning messages
- `logger.error(msg, extra=None, exc_info=False)` - Error messages
- `logger.critical(msg, extra=None, exc_info=False)` - Critical messages
- `logger.exception(msg, extra=None)` - Shortcut for `logger.error(..., exc_info=True)`

### Standard Log Fields (JSON)

- `timestamp` - ISO 8601 timestamp with timezone
- `level` - Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `logger` - Logger name (module path)
- `message` - Log message
- `module` - Module name
- `function` - Function name
- `line` - Line number
- `exception` - Stack trace (if exc_info=True)
- `request_id` - Unique request identifier (in request context)
- Any fields from `extra` parameter

## Further Reading

- [FastAPI Logging Documentation](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [Python Logging Best Practices](https://docs.python.org/3/howto/logging.html)
- [Docker Logging Drivers](https://docs.docker.com/config/containers/logging/configure/)
- [Structured Logging](https://www.structlog.org/en/stable/)

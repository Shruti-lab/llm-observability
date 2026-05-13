from typing import AsyncGenerator
from fastapi import FastAPI, Request, Response
from contextlib import asynccontextmanager
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
from metrics import (
    LLM_REQUEST_COUNT, 
    LLM_REQUEST_DURATION, 
    LLM_RESPONSE_QUALITY, 
    LLM_TOKEN_COUNT, 
    LLM_ERROR_COUNT
)
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from config import settings
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from llm_client import llm_client

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

    
async def monitor_llm():
    """Monitors LLM and updates metrics"""
    logger.info("Running LLM health check...")
    try:
        start = time.time()
        result = await llm_client.query(prompt=settings.test_prompt)
        duration = time.time() - start
        
        # Update duration metric
        LLM_REQUEST_DURATION.labels(
            model=settings.llm_model,
            method="POST",
            endpoint="/monitor"
        ).observe(duration)
        
        # Update request count
        status = "success" if result["success"] else "failure"
        LLM_REQUEST_COUNT.labels(
            model=settings.llm_model,
            method="POST",
            status=status
        ).inc()
        
        # Evaluate and update quality
        if result["success"]:
            quality = llm_client.evaluate_quality(
                response=result["response"],
                expected=settings.expected_answer
            )
            LLM_RESPONSE_QUALITY.labels(
                model=settings.llm_model,
                endpoint="/monitor",
                status=status
            ).set(quality)
            
            # Update token count
            LLM_TOKEN_COUNT.labels(
                model=settings.llm_model,
                endpoint="/monitor",
                status=status
            ).set(result["tokens"])
            
            logger.info(f"Health check passed - Quality: {quality}, Tokens: {result['tokens']}, Latency: {duration:.3f}s")
        else:
            # Record error
            LLM_ERROR_COUNT.labels(
                model=settings.llm_model,
                endpoint="/monitor",
                error_type=result["error"]
            ).inc()
            logger.error(f"Health check failed: {result['error']}")
        
    except Exception as e:
        logger.error(f"Unexpected error in monitor_llm: {e}")
        LLM_ERROR_COUNT.labels(
            model=settings.llm_model,
            endpoint="/monitor",
            error_type="unexpected"
        ).inc()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifecycle"""
    logger.info("Starting LLM Health Monitor...")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        monitor_llm,
        'interval',
        seconds=settings.monitor_interval,
        id='llm_monitor'
    )
    scheduler.start()
    logger.info(f"Scheduler started - monitoring every {settings.monitor_interval}s")
    
    yield
    
    logger.info("Shutting down scheduler...")
    scheduler.shutdown()
    logger.info("Scheduler stopped")


app = FastAPI(
    title=settings.app_name,
    description="LLM Health Monitoring System with Prometheus metrics",
    version="1.0.0",
    lifespan=lifespan
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect HTTP request metrics"""

    async def dispatch(self, request: Request, call_next):
        # Skip metrics endpoint to avoid recursion
        if request.url.path == '/metrics':
            return await call_next(request)

        method = request.method
        endpoint = request.url.path
        start_time = time.time()

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            logger.error(f"Request failed: {e}")
            raise
        finally:
            # Record duration
            duration = time.time() - start_time
            LLM_REQUEST_DURATION.labels(
                model=settings.llm_model,
                method=method,
                endpoint=endpoint
            ).observe(duration)

            # Record request count
            LLM_REQUEST_COUNT.labels(
                model=settings.llm_model,
                method=method,
                status=str(status_code)
            ).inc()

        return response


app.add_middleware(MetricsMiddleware)


@app.get('/')
async def root():
    """Root endpoint with service info"""
    return {
        "service": settings.app_name,
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "metrics": "/metrics",
            "health": "/health",
            "query": "/api/query"
        }
    }


@app.get('/metrics')
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.get('/health')
async def health():
    """Health check endpoint for K8s probes"""
    return {
        'status': 'healthy',
        'service': settings.app_name,
        'llm_url': settings.llm_url,
        'model': settings.llm_model
    }


@app.post('/api/query')
async def query_endpoint(prompt: str):
    """Manual LLM query endpoint"""
    try:
        result = await llm_client.query(prompt)
        logger.info(f"Query result - Success: {result['success']}, Tokens: {result['tokens']}")
        return result
    except Exception as e:
        logger.error(f"Error querying LLM: {e}")
        return {
            'response': '',
            'tokens': 0,
            'success': False,
            'error': str(e)
        }


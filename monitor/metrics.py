from typing import Any
from prometheus_client import Counter, Histogram, Gauge, Info


# File define metrics

APP_INFO = Info(
    'fastapi_app',
    'Application information'
)

# Set application info
APP_INFO.info({
    'version': '1.0.0',
    'environment': 'production'
})

LLM_REQUEST_COUNT: Any = Counter(
    'llm_requests_total',
    'Total LLM requests',
    ['model','endpoint','method','status_code']
)

LLM_REQUEST_DURATION = Histogram(
    'llm_request_duration_seconds',
    'LLM request duration in seconds',
    ['model','endpoint','method'],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)
#     ['model','method','endpoint'],


LLM_RESPONSE_QUALITY = Gauge(
    'llm_response_quality',
    'LLM response quality',
    ['model']
)
#     ['model','endpoint','status']


LLM_TOKEN_COUNT = Gauge(
    'llm_tokens_count',
    'LLM token count',
    ['model']
)
# ['model','endpoint','status']


LLM_ERROR_COUNT = Counter(
    'llm_errors_total',
    'Total LLM errors',
    ['model','error_type']
)
#     ['model','endpoint','error_type']

   



# REQUEST_COUNT = Counter(
#     'fastapi_requests_total',
#     'Total requests',
#     ['method', 'endpoint', 'status_code']
# )

# REQUEST_DURATION = Histogram(
#     'fastapi_request_duration_seconds',
#     'Request duration in seconds',
#     ['method', 'endpoint'],
#     buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
# )

# REQUESTS_IN_PROGRESS = Gauge(
#     'fastapi_requests_in_progress',
#     'Requests currently being processed',
#     ['method', 'endpoint']
# )

# ORDERS_TOTAL = Counter(
#     'orders_total',
#     'Total orders processed',
#     ['status', 'payment_method']
# )

# ORDER_VALUE = Histogram(
#     'order_value_dollars',
#     'Order value in dollars',
#     buckets=[10, 25, 50, 100, 250, 500, 1000, 2500, 5000]
# )

# INVENTORY_LEVEL = Gauge(
#     'inventory_level',
#     'Current inventory level',
#     ['product_id', 'warehouse']
# )

# APP_INFO = Info(
#     'fastapi_app',
#     'Application information'
# )

# # Set application info
# APP_INFO.info({
#     'version': '1.0.0',
#     'environment': 'production'
# })

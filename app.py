from flask import Flask, request, jsonify
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CollectorRegistry

app = Flask(__name__)
registry = CollectorRegistry()

# Prometheus metrics
REQ_COUNT   = Counter("http_requests_total", "Total HTTP requests", ["method","endpoint"], registry=registry)
REQ_LATENCY = Histogram("http_request_duration_seconds", "Request latency", ["endpoint"], registry=registry)
ERROR_COUNT = Counter("http_errors_total", "Total errors", ["endpoint"], registry=registry)
ACTIVE_REQ  = Gauge("http_active_requests", "Active in-flight requests", registry=registry)

# In-memory stores
customers = []
orders = []
products = []

def track(endpoint):
    def decorator(f):
        def wrapped(*args, **kwargs):
            ACTIVE_REQ.inc()
            with REQ_LATENCY.labels(endpoint=endpoint).time():
                try:
                    REQ_COUNT.labels(method=request.method, endpoint=endpoint).inc()
                    return f(*args, **kwargs)
                except Exception:
                    ERROR_COUNT.labels(endpoint=endpoint).inc()
                    raise
                finally:
                    ACTIVE_REQ.dec()
        wrapped.__name__ = f.__name__
        return wrapped
    return decorator

@app.route("/customer", methods=["GET","POST"])
@track("customer")
def customer():
    if request.method == "POST":
        customers.append(request.json)
        return jsonify({"status":"customer created"}), 201
    return jsonify(customers), 200

@app.route("/order", methods=["GET","POST"])
@track("order")
def order():
    if request.method == "POST":
        orders.append(request.json)
        return jsonify({"status":"order placed"}), 201
    return jsonify(orders), 200

@app.route("/product", methods=["GET","POST"])
@track("product")
def product_list():
    if request.method == "POST":
        pid = len(products) + 1
        prod = {"id": pid, **request.json}
        products.append(prod)
        return jsonify(prod), 201
    return jsonify(products), 200

@app.route("/product/<int:pid>", methods=["GET"])
@track("product_detail")
def product_detail(pid):
    for p in products:
        if p["id"] == pid:
            return jsonify(p), 200
    return jsonify({"error":"not found"}), 404

@app.route("/health", methods=["GET"])
def health():
    return "OK", 200

@app.route("/metrics", methods=["GET"])
def metrics():
    return generate_latest(registry), 200, {"Content-Type":"text/plain"}

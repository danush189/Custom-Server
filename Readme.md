# Flask Metrics Server

A lightweight Flask application with built-in Prometheus metrics for monitoring using Grafana.

## Overview

This project implements a basic REST API server with customer, order, and product endpoints. It includes Prometheus instrumentation for monitoring request counts, latency, error rates, and active requests.

## Project Structure

```
flask-metrics-server/
├── app.py                    # Main Flask application with API endpoints and metrics
├── test_flask_and_metrics.py # Test script to generate sample traffic
└── README.md                 # This file
```

## Features

- Simple REST API with endpoints for customers, orders, and products
- Prometheus metrics instrumentation
- Health check endpoint
- Metrics endpoint for Prometheus scraping

## Prerequisites

- Python 3.6+
- Flask
- Prometheus Client for Python
- Prometheus server
- Grafana

## Installation

1. Clone the repository
2. Install the required packages:

```bash
pip install flask prometheus_client requests
```

3. Install and configure Prometheus (Windows):
   - Download Prometheus from the [official website](https://prometheus.io/download/)
   - Add the following job to your `prometheus.yml` configuration:

```yaml
- job_name: 'flask-app'
  static_configs:
    - targets: ['localhost:5000']
```

4. Install and configure Grafana:
   - Download and install Grafana from the [official website](https://grafana.com/grafana/download)
   - Add Prometheus as a data source (default port 9090)

## Usage

1. Start the Flask application:

```bash
python app.py
```

2. Start Prometheus (adjust path as needed):

```bash
cd path/to/prometheus
./prometheus.exe
```

3. Start Grafana (it should run as a service on Windows)

4. Run the test script to generate traffic:

```bash
python test_flask_and_metrics.py
```

## API Endpoints

- **GET/POST /customer** - Retrieve all customers or create a new customer
- **GET/POST /order** - Retrieve all orders or create a new order
- **GET/POST /product** - Retrieve all products or create a new product
- **GET /product/<id>** - Retrieve a specific product by ID
- **GET /health** - Health check endpoint
- **GET /metrics** - Prometheus metrics endpoint

## Monitoring

### Available Metrics

- `http_requests_total` - Counter of total HTTP requests by method and endpoint
- `http_request_duration_seconds` - Histogram of request latency by endpoint
- `http_errors_total` - Counter of HTTP errors by endpoint
- `http_active_requests` - Gauge of active in-flight requests

### Recommended Grafana Queries

Create a dashboard in Grafana with the following queries:

1. **Total Requests Over Time**
   - Query: `sum(rate(http_requests_total[1m]))`

2. **Request Rate by Endpoint**
   - Query: `sum by(endpoint)(rate(http_requests_total[1m]))`

3. **95th-Percentile Latency**
   - Query: `histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[1m])) by (le, endpoint))`

4. **Error Rate**
   - Query: `sum(rate(http_errors_total[1m])) / sum(rate(http_requests_total[1m]))`

5. **Active Requests**
   - Query: `http_active_requests`

## Testing

The included `test_flask_and_metrics.py` script will:

1. Create sample data for customers, products, and orders
2. Generate traffic to all endpoints for 2 minutes
3. Introduce random latency to simulate real-world conditions
4. Create some errors (approximately 10%) to test error tracking
5. Print progress information as it runs

This will help you verify that your metrics are being collected and displayed correctly in Grafana.

## License

[MIT](https://choosealicense.com/licenses/mit/)

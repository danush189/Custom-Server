import requests
import json
import time
import random

BASE_URL = "http://localhost:5000"

# Test data
customers_data = [
    {"id": 1, "name": "John Doe", "email": "john@example.com", "tier": "premium"},
    {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "tier": "standard"},
    {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "tier": "premium"},
]

products_data = [
    {"name": "Laptop", "price": 999.99, "category": "electronics", "stock": 50},
    {"name": "Smartphone", "price": 499.99, "category": "electronics", "stock": 100},
    {"name": "Headphones", "price": 79.99, "category": "accessories", "stock": 200},
    {"name": "Monitor", "price": 299.99, "category": "electronics", "stock": 30},
    {"name": "Keyboard", "price": 59.99, "category": "accessories", "stock": 150},
]

orders_data = [
    {"customer_id": 1, "products": [1, 3], "total": 1079.98, "status": "completed"},
    {"customer_id": 2, "products": [2], "total": 499.99, "status": "processing"},
    {"customer_id": 3, "products": [4, 5], "total": 359.98, "status": "completed"},
    {"customer_id": 1, "products": [2, 5], "total": 559.98, "status": "shipped"},
]

def send_request(endpoint, method="GET", data=None):
    """Send a request and return the response"""
    url = f"{BASE_URL}/{endpoint}"
    
    if method == "GET":
        response = requests.get(url)
    elif method == "POST":
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, data=json.dumps(data), headers=headers)
    
    return response

def generate_traffic(duration=60, error_rate=0.1):
    """Generate traffic to all endpoints for a specified duration"""
    start_time = time.time()
    request_count = 0
    error_count = 0
    
    # First, create some initial data
    print("Creating initial data...")
    for customer in customers_data:
        send_request("customer", "POST", customer)
    
    for product in products_data:
        send_request("product", "POST", product)
    
    for order in orders_data:
        send_request("order", "POST", order)
    
    print(f"Initial data created. Generating traffic for {duration} seconds...")
    
    # Now generate random traffic
    while time.time() - start_time < duration:
        # Pick a random endpoint
        endpoint = random.choice(["customer", "order", "product", "product/1", "product/2", "product/3", "health"])
        
        # Occasionally cause an error by requesting a non-existent product
        if random.random() < error_rate and endpoint.startswith("product/"):
            endpoint = f"product/{random.randint(10, 20)}"  # Non-existent product IDs
        
        # Choose method (GET more often than POST)
        method = "GET" if random.random() < 0.8 or endpoint in ["health", "product/1", "product/2", "product/3"] else "POST"
        
        # Prepare data for POST requests
        data = None
        if method == "POST":
            if endpoint == "customer":
                data = {"name": f"Customer {random.randint(100, 999)}", "email": f"user{random.randint(100, 999)}@example.com", "tier": random.choice(["standard", "premium"])}
            elif endpoint == "product":
                data = {"name": f"Product {random.randint(100, 999)}", "price": round(random.uniform(10, 1000), 2), "category": random.choice(["electronics", "accessories", "clothing"]), "stock": random.randint(1, 100)}
            elif endpoint == "order":
                data = {"customer_id": random.randint(1, 3), "products": [random.randint(1, 5) for _ in range(random.randint(1, 3))], "total": round(random.uniform(10, 2000), 2), "status": random.choice(["pending", "processing", "shipped", "completed"])}
        
        # Add some variable latency
        if random.random() < 0.05:  # 5% of requests are slow
            time.sleep(random.uniform(0.5, 2.0))
        else:
            time.sleep(random.uniform(0.01, 0.1))
        
        # Send the request
        try:
            response = send_request(endpoint, method, data)
            request_count += 1
            
            if response.status_code >= 400:
                error_count += 1
                print(f"Error {response.status_code} on {method} /{endpoint}")
            
            # Print progress periodically
            if request_count % 20 == 0:
                elapsed = time.time() - start_time
                print(f"Progress: {elapsed:.1f}s / {duration}s - {request_count} requests, {error_count} errors")
                
        except Exception as e:
            error_count += 1
            print(f"Exception on {method} /{endpoint}: {str(e)}")
        
    print(f"\nTraffic generation completed!")
    print(f"Total requests: {request_count}")
    print(f"Errors: {error_count} ({error_count/request_count*100:.1f}%)")
    print(f"Average rate: {request_count/duration:.1f} requests/second")

if __name__ == "__main__":
    # Check if the server is running
    try:
        health_check = requests.get(f"{BASE_URL}/health")
        if health_check.status_code == 200:
            print("Server is up and running!")
        else:
            print(f"Server returned unexpected status: {health_check.status_code}")
            exit(1)
    except requests.exceptions.ConnectionError:
        print("Cannot connect to the server. Please make sure it's running at", BASE_URL)
        exit(1)
    
    # Check if metrics endpoint is working
    try:
        metrics = requests.get(f"{BASE_URL}/metrics")
        if metrics.status_code == 200:
            print("Metrics endpoint is working!")
        else:
            print(f"Metrics endpoint returned unexpected status: {metrics.status_code}")
    except requests.exceptions.ConnectionError:
        print("Cannot connect to metrics endpoint")
    
    # Generate traffic
    generate_traffic(duration=300, error_rate=0.1)  # Run for 2 minutes with 10% error rate
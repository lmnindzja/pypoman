import random

def generate_mock_services():
    """Генерирует моковые данные для сервисов."""
    services = []
    statuses = ["Running", "Stopped", "Paused", "Starting", "Stopping"]
    for i in range(10):
        services.append({
            "PSComputerName": f"Host-{i+1}",
            "Port": random.randint(1024, 65535),
            "Type": "Service",
            "Name": f"Service_{i+1}",
            "Version": f"{random.randint(1, 10)}.{random.randint(0, 9)}",
            "State": random.choice(statuses),
            "PID": random.randint(1000, 9999),
            "User": f"User_{i+1}",
            "StartTime": "2025-01-01 10:00:00",
            "LastBootTime": "2025-01-01 08:00:00",
            "RMQConnCount": random.randint(0, 50)
        })
    return services

def generate_mock_web_services():
    """Генерирует моковые данные для веб-сервисов."""
    web_services = []
    statuses = ["Online", "Offline", "Degraded"]
    for i in range(5):
        web_services.append({
            "PSComputerName": f"WebServer-{i+1}",
            "Port": random.randint(80, 443),
            "Type": "Web Service",
            "Name": f"WebApp_{i+1}",
            "Version": f"{random.randint(1, 10)}.{random.randint(0, 9)}",
            "State": random.choice(statuses),
            "PID": random.randint(1000, 9999),
            "User": f"WebUser_{i+1}",
            "StartTime": "2025-01-01 11:00:00",
            "LastBootTime": "2025-01-01 09:00:00",
            "RMQConnCount": random.randint(0, 30)
        })
    return web_services

def generate_mock_network_connections():
    """Генерирует моковые данные для сетевых подключений."""
    connections = []
    statuses = ["Established", "Listening", "Closed"]
    for i in range(10):
        connections.append({
            "State": random.choice(statuses),
            "LocalAddress": f"192.168.0.{random.randint(1, 255)}",
            "LocalHostName": f"LocalHost_{i+1}",
            "LocalPort": random.randint(1024, 65535),
            "RemoteAddress": f"203.0.113.{random.randint(1, 255)}",
            "RemoteHostName": f"RemoteHost_{i+1}",
            "RemotePort": random.randint(1024, 65535),
        })
    return connections

from datetime import datetime

def success_response(data, message="Operation completed successfully"):
    return {
        "success": True,
        "data": data,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }

def error_response(code, message, details=None):
    return {
        "success": False,
        "error_code": code,
        "message": message,
        "details": details or {},
        "timestamp": datetime.utcnow().isoformat()
    }

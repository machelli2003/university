"""
OpenAPI/Swagger Documentation Configuration
Comprehensive API documentation for all endpoints
Section 66: API Documentation
"""
from fastapi.openapi.utils import get_openapi
from app.main import app


def custom_openapi():
    """Generate custom OpenAPI schema with detailed documentation"""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Enterprise University Management Platform API",
        version="1.0.0",
        description="""
## Overview

The Enterprise University Management Platform (EUMP) is a comprehensive multi-tenant SaaS system 
for managing all aspects of university operations including admissions, academics, finance, 
accommodation, and more.

### Key Features
- **Multi-Tenant Architecture**: Complete data isolation per university
- **Role-Based Access Control**: 15 distinct roles with hierarchy
- **Resource-Level Authorization**: Fine-grained permission control
- **20-State Application Lifecycle**: Comprehensive applicant workflow
- **Real-Time Dashboards**: Role-specific analytics and reporting
- **Audit Logging**: Complete operation tracking

### Architecture Layers

#### 1. Authentication Layer
- JWT token-based authentication
- Access token + Refresh token pattern
- User claims: user_id, tenant_id, role, email

#### 2. Tenant Isolation Layer (Early Pipeline)
- TenantIsolationMiddleware enforces tenant_id from JWT
- Blocks cross-tenant access before endpoint execution
- All queries include tenant_id filter

#### 3. Role-Based Authorization Layer
- 15 role levels from student (1) to super_admin (15)
- Role hierarchy enforcement
- Resource access matrix per role

#### 4. Resource-Level Authorization Layer (NEW - Sections 57-62)
- StaffAssignment model links staff to resources
- Fine-grained permissions per assignment
- Support for DEPARTMENT, FACULTY, PROGRAMME, COURSE, HOSTEL, etc.

#### 5. Endpoint-Level Authorization
- get_current_user dependency injection
- PrivateRoute frontend component (5-level checks)
- Audit logging on all operations

### API Response Format

All endpoints return standardized responses:

**Success Response (200)**:
```json
{
  "data": {...},
  "meta": {
    "timestamp": "2026-08-13T10:30:00Z",
    "request_id": "uuid"
  }
}
```

**Error Response**:
```json
{
  "detail": "Error message",
  "status_code": 400,
  "request_id": "uuid"
}
```

### Authentication

All endpoints (except public paths) require JWT Bearer token in Authorization header:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

Public paths (no auth required):
- POST /api/v1/auth/login
- POST /api/v1/auth/register
- GET /api/v1/health
- POST /apply/{school_code}/register (applicant portal)

### Rate Limiting

- 1000 requests per hour per API key
- 5000 requests per hour per IP
- Burst limit: 100 requests per second

### Versioning

Current API version: **1.0.0**

Version format: `/api/v{major}/...`

### Pagination

List endpoints support pagination:
- `skip`: Number of items to skip (default: 0)
- `limit`: Number of items to return (default: 50, max: 100)

### Filtering

Endpoints support field-based filtering:
- Query string format: `?filter_field=value`
- Multiple filters: `?role=lecturer&department=cs`
- Complex filters via POST body

### Sorting

- `sort_by`: Field to sort by
- `sort_order`: 'asc' or 'desc'

### Common Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized (invalid/missing token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

### Rate Limit Headers

Response includes rate limit information:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1629043200
```

### Request Tracking

All requests include X-Request-ID for tracking:
```
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
```

### Audit Logging

All operations are logged with:
- Timestamp
- User ID
- Tenant ID
- Action performed
- Affected resources
- IP address
- Success/failure status

### Examples

#### Login
```bash
curl -X POST https://api.eump.edu/api/v1/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"email": "user@university.edu", "password": "SecurePass123!"}'
```

#### Create Staff Assignment
```bash
curl -X POST https://api.eump.edu/api/v1/staff-assignments \\
  -H "Authorization: Bearer <TOKEN>" \\
  -H "Content-Type: application/json" \\
  -d '{
    "staff_id": "staff_123",
    "assignment_type": "DEPARTMENT",
    "resource_id": "dept_456",
    "resource_name": "Computer Science",
    "staff_role": "head_of_department",
    "permissions": ["view_staff", "edit_course"],
    "start_date": "2026-08-13T00:00:00Z"
  }'
```

#### List Assignments
```bash
curl -X GET "https://api.eump.edu/api/v1/staff-assignments?skip=0&limit=50" \\
  -H "Authorization: Bearer <TOKEN>"
```

### Response Time SLA

- Dashboard endpoints: < 500ms
- CRUD operations: < 200ms
- Aggregation queries: < 2s
- Report generation: < 10s

### Backup & Recovery

- Full backup every 6 hours
- Transaction log backup every 15 minutes
- RPO (Recovery Point Objective): 15 minutes
- RTO (Recovery Time Objective): 1 hour

### Support

- Email: api-support@eump.edu
- Response Time: 4 business hours
- Documentation: https://docs.eump.edu
- Status Page: https://status.eump.edu

""",
        routes=app.routes,
        tags=[
            {
                "name": "auth",
                "description": "Authentication and authorization endpoints"
            },
            {
                "name": "staff-assignments",
                "description": "Staff assignment management (Sections 57-62)"
            },
            {
                "name": "dashboards",
                "description": "Role-specific dashboard endpoints (Sections 40-52)"
            },
            {
                "name": "admissions",
                "description": "Admissions and applicant management (Sections 33-39)"
            },
            {
                "name": "academic",
                "description": "Academic operations (courses, grades, transcripts)"
            },
            {
                "name": "finance",
                "description": "Financial management (invoices, payments, fees)"
            },
            {
                "name": "accommodation",
                "description": "Hostel and accommodation management"
            },
            {
                "name": "library",
                "description": "Library management (books, checkouts, members)"
            },
            {
                "name": "exam",
                "description": "Examination management"
            },
            {
                "name": "attendance",
                "description": "Attendance tracking"
            },
            {
                "name": "admin",
                "description": "Administrative operations"
            },
            {
                "name": "health",
                "description": "Health services management"
            },
            {
                "name": "research",
                "description": "Research management"
            },
            {
                "name": "alumni",
                "description": "Alumni management"
            },
            {
                "name": "communication",
                "description": "Internal communication"
            },
            {
                "name": "documents",
                "description": "Document management"
            },
            {
                "name": "workflow",
                "description": "Workflow management"
            },
            {
                "name": "inventory",
                "description": "Inventory management"
            },
            {
                "name": "analytics",
                "description": "Analytics and reporting"
            },
            {
                "name": "students",
                "description": "Student operations"
            },
            {
                "name": "lecturer",
                "description": "Lecturer operations"
            },
            {
                "name": "parents",
                "description": "Parent portal operations"
            },
            {
                "name": "counseling",
                "description": "Counseling services"
            },
            {
                "name": "applicant-portal",
                "description": "Applicant portal operations (Sections 33-34)"
            },
            {
                "name": "wassce-verification",
                "description": "WASSCE result verification (Sections 35-38)"
            }
        ]
    )

    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    # Add custom response models
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    if "schemas" not in openapi_schema["components"]:
        openapi_schema["components"]["schemas"] = {}

    openapi_schema["components"]["schemas"]["Error"] = {
        "type": "object",
        "properties": {
            "detail": {"type": "string"},
            "status_code": {"type": "integer"},
            "request_id": {"type": "string"}
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Override the OpenAPI schema
app.openapi = custom_openapi


# Configure Swagger UI and ReDoc
def get_swagger_ui_html():
    """Custom Swagger UI configuration"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>EUMP API - Swagger UI</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css">
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js"></script>
        <script>
        const ui = SwaggerUIBundle({{
            url: "/openapi.json",
            dom_id: '#swagger-ui',
            presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIBundle.SwaggerUIStandalonePreset
            ],
            layout: "BaseLayout",
            deepLinking: true,
            defaultModelsExpandDepth: 1
        }})
        </script>
    </body>
    </html>
    """


# API Documentation endpoints are automatically generated by FastAPI
# Access at:
# - Swagger UI: /docs
# - ReDoc: /redoc
# - OpenAPI JSON: /openapi.json

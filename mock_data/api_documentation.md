# API Documentation

## Authentication

### API Keys
All API requests must include an authentication header:
```
Authorization: Bearer YOUR_API_KEY
```

### Rate Limiting
- Standard tier: 500 requests per hour
- Premium tier: 1000 requests per hour  
- Enterprise tier: 5000 requests per hour

Rate limit headers are included in all responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1629825600
```

## Core Endpoints

### Users API

#### Get User
```
GET /api/v2/users/{user_id}
```

Returns user information including profile data and preferences.

#### Create User
```
POST /api/v2/users
```

Creates a new user account. Required fields:
- email (string)
- name (string)
- password (string, min 8 characters)

#### Update User  
```
PUT /api/v2/users/{user_id}
```

Updates user profile information. Only provided fields will be updated.

### Orders API

#### List Orders
```
GET /api/v2/orders
```

Query parameters:
- status: filter by order status (pending, shipped, delivered)
- customer_id: filter by customer
- limit: number of results (max 100)
- offset: pagination offset

#### Get Order
```
GET /api/v2/orders/{order_id}
```

Returns detailed order information including line items and shipping details.

#### Create Order
```
POST /api/v2/orders
```

Creates a new order. Required fields:
- customer_id (integer)
- items (array of objects with product_id and quantity)
- shipping_address (object)

### Products API

#### List Products
```
GET /api/v2/products
```

Query parameters:
- category: filter by product category
- in_stock: boolean, show only products in stock
- search: text search in name and description

#### Get Product
```
GET /api/v2/products/{product_id}
```

Returns product details including pricing, inventory, and variants.

## Webhooks

### Configuration
Webhooks can be configured in your dashboard under Settings > Webhooks.

Supported events:
- order.created
- order.updated
- order.shipped
- user.created
- product.updated

### Payload Format
```json
{
  "event": "order.created",
  "timestamp": "2024-08-20T10:30:00Z",
  "data": {
    "order_id": 12345,
    "customer_id": 67890,
    "total": 99.99,
    "status": "pending"
  }
}
```

### Security
All webhook requests include an HMAC-SHA256 signature in the `X-Signature` header for verification.

## Error Handling

### HTTP Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Rate Limited
- 500: Internal Server Error

### Error Response Format
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "The request is missing required parameter 'email'",
    "details": {
      "field": "email",
      "reason": "required"
    }
  }
}
```

## SDKs and Libraries

### Python SDK
```bash
pip install company-api-sdk
```

```python
from company_api import Client

client = Client(api_key="your_api_key")
user = client.users.get(123)
```

### JavaScript SDK
```bash
npm install @company/api-sdk
```

```javascript
import { Client } from '@company/api-sdk';

const client = new Client({ apiKey: 'your_api_key' });
const user = await client.users.get(123);
```

## Best Practices

### Connection Pooling
For high-traffic applications, configure connection pooling:
- Max connections: 100-200
- Connection timeout: 30 seconds
- Implement retry logic with exponential backoff

### Caching
- Cache frequently accessed data
- Use ETags for conditional requests
- Set appropriate cache headers

### Pagination
For large datasets, use cursor-based pagination:
```
GET /api/v2/orders?cursor=eyJpZCI6MTIzNDV9&limit=50
```

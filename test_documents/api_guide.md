# API Rate Limits Guide

## Overview

This guide explains the rate limiting policies for our API services.

## Rate Limit Tiers

### Free Tier
- **Requests per minute**: 100
- **Requests per hour**: 1,000
- **Requests per day**: 10,000

### Premium Tier
- **Requests per minute**: 1,000
- **Requests per hour**: 50,000
- **Requests per day**: 500,000

### Enterprise Tier
- **Requests per minute**: 10,000
- **Requests per hour**: 500,000
- **Requests per day**: 10,000,000

## Rate Limit Headers

When you make API requests, the following headers are returned:

- `X-RateLimit-Limit`: The rate limit ceiling for that request
- `X-RateLimit-Remaining`: The number of requests left for the time window
- `X-RateLimit-Reset`: The time at which the rate limit resets

## Handling Rate Limits

When you exceed your rate limit, you'll receive a `429 Too Many Requests` response.

### Best Practices

1. **Implement exponential backoff**: When you receive a 429 response, wait before retrying
2. **Monitor your usage**: Keep track of the rate limit headers
3. **Cache responses**: Reduce unnecessary API calls by caching data
4. **Use webhooks**: Instead of polling, use webhooks for real-time updates

## Error Responses

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "API rate limit exceeded",
    "retry_after": 60
  }
}
```

## Contact Support

If you need higher rate limits, please contact our support team at support@example.com.

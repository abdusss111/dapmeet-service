Admin api dap meet  # Admin Panel API Endpoints

## Authentication & Authorization

```typescript
// Admin Authentication
POST   /admin/login
POST   /admin/logout

## Dashboard & Analytics


// Dashboard Overview
GET    /admin/dashboard/metrics
GET    /admin/dashboard/activity-feed
GET    /admin/dashboard/system-health

// Real-time metrics
GET    /admin/metrics/users/active
GET    /admin/metrics/meetings/today
GET    /admin/metrics/ai/usage
GET    /admin/metrics/system/performance
```

## User Management

```typescript
// User CRUD
GET    /admin/users                    // List with pagination, search, filters
GET    /admin/users/:userId           // User details
PUT    /admin/users/:userId           // Update user

// User Analytics

GET    /admin/users/:userId/activity  // User activity log
GET    /admin/users/:userId/ai-usage  // AI usage stats
GET    /admin/users/stats             // User statistics


## Meeting Management


// Meeting Analytics
GET    /admin/meetings/stats

## AI & Processing Management


// AI Configuration
GET    /admin/ai/config
PUT    /admin/ai/config
GET    /admin/ai/models
GET    /admin/ai/prompts

Overall prompt management

// AI Analytics
GET    /admin/ai/usage-stats
GET    /admin/ai/performance
GET    /admin/ai/token-usage
GET    /admin/ai/cost-analysis
```


// Health Monitoring
GET    /admin/system/health
GET    /admin/system/health/database
GET    /admin/system/health/ai-services
GET    /admin/system/health/external-apis
GET    /admin/system/performance-metrics

## Security & Audit

```typescript
// Audit Logs
GET    /admin/audit/logs
GET    /admin/audit/logs/admin-actions
GET    /admin/audit/logs/errors
 
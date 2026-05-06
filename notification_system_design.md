# Notification System Design

## Stage 1: REST API Endpoints

### Core Actions & Endpoints

#### 1. Fetch All Notifications
**Endpoint:** `GET /api/v1/notifications`

**Headers:**
```json
{
  "Authorization": "Bearer <JWT_TOKEN>",
  "Content-Type": "application/json"
}
```

**Query Parameters:**
```
?page=1&limit=20&unread_only=false
```

**Response (Status: 200):**
```json
{
  "success": true,
  "data": {
    "notifications": [
      {
        "notificationId": "uuid",
        "userId": "uuid",
        "type": "email_event|system_alert|remainder",
        "title": "string",
        "message": "string",
        "isRead": false,
        "createdAt": "ISO8601",
        "updatedAt": "ISO8601"
      }
    ],
    "pagination": {
      "currentPage": 1,
      "totalPages": 5,
      "totalNotifications": 100,
      "hasNext": true
    }
  }
}
```

#### 2. Mark Notification as Read
**Endpoint:** `PUT /api/v1/notifications/{notificationId}`

**Headers:**
```json
{
  "Authorization": "Bearer <JWT_TOKEN>",
  "Content-Type": "application/json"
}
```

**Request Body:**
```json
{
  "isRead": true
}
```

**Response (Status: 200):**
```json
{
  "success": true,
  "message": "Notification marked as read",
  "data": {
    "notificationId": "uuid",
    "isRead": true,
    "updatedAt": "ISO8601"
  }
}
```

#### 3. Delete Notification
**Endpoint:** `DELETE /api/v1/notifications/{notificationId}`

**Headers:**
```json
{
  "Authorization": "Bearer <JWT_TOKEN>"
}
```

**Response (Status: 200):**
```json
{
  "success": true,
  "message": "Notification deleted successfully"
}
```

#### 4. Create Notification
**Endpoint:** `POST /api/v1/notifications`

**Headers:**
```json
{
  "Authorization": "Bearer <JWT_TOKEN>",
  "Content-Type": "application/json"
}
```

**Request Body:**
```json
{
  "userId": "uuid",
  "type": "email_event|system_alert|reminder",
  "title": "string",
  "message": "string",
  "metadata": {
    "actionUrl": "string",
    "priority": "high|medium|low"
  }
}
```

**Response (Status: 201):**
```json
{
  "success": true,
  "message": "Notification created",
  "data": {
    "notificationId": "uuid",
    "userId": "uuid",
    "type": "string",
    "title": "string",
    "message": "string",
    "isRead": false,
    "createdAt": "ISO8601"
  }
}
```

### Real-Time Notifications Mechanism

**WebSocket Endpoint:** `ws://api.server.com/ws/notifications/{userId}`

**Connection Message:**
```json
{
  "event": "connected",
  "userId": "uuid",
  "timestamp": "ISO8601"
}
```

**Notification Event:**
```json
{
  "event": "notification_received",
  "notification": {
    "notificationId": "uuid",
    "type": "string",
    "title": "string",
    "message": "string",
    "timestamp": "ISO8601"
  }
}
```



## Stage 2: Database Design & Persistence


### Database Choice: PostgreSQL (Relational DB)

**Reason:**
- ACID properties helps in data consistency
- Complex queries are possible using JOINs
- Built-in JSON support for metadata
- Scalable with proper indexing
- Cost-effective for structured notification data

### Database Schema

```sql
-- Notifications table
CREATE TABLE notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  type VARCHAR(50) NOT NULL CHECK (type IN ('email_event', 'system_alert', 'reminder')),
  title VARCHAR(255) NOT NULL,
  message TEXT,
  is_read BOOLEAN DEFAULT FALSE,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP NULL
);

-- Notification preferences table
CREATE TABLE notification_preferences (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  email_enabled BOOLEAN DEFAULT TRUE,
  sms_enabled BOOLEAN DEFAULT FALSE,
  push_enabled BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indices for performance
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);
CREATE INDEX idx_notifications_user_is_read ON notifications(user_id, is_read);
CREATE INDEX idx_notifications_deleted_at ON notifications(deleted_at);
```

### Scalability Challenges & Solutions

**Challenge 1: Query Performance with Volume Growth**
- *Problem:* Fetching notifications for users with millions of records becomes slow
- *Solution:* Partition notifications based on time or archive the old notifications

**Challenge 2: Storage Growth**
- *Problem:* Database size explodes with notification history
- *Solution:* Archive the notifications which are older than 90 days to separate storage

**Challenge 3: Concurrent Read/Write**
- *Problem:* High update rate when marking notifications as read
- *Solution:* Caching layer (Redis) can be used for recent notification status

### SQL Queries

#### Query 1: Fetch Unread Notifications
```sql
SELECT * FROM notifications
WHERE user_id = $1
  AND is_read = FALSE
  AND deleted_at IS NULL
ORDER BY created_at DESC
LIMIT $2 OFFSET $3;
```

#### Query 2: Mark Notification as Read
```sql
UPDATE notifications
SET is_read = TRUE,
    updated_at = CURRENT_TIMESTAMP
WHERE id = $1
  AND user_id = $2
RETURNING *;
```

#### Query 3: Delete Notification (Soft Delete)
```sql
UPDATE notifications
SET deleted_at = CURRENT_TIMESTAMP
WHERE id = $1
  AND user_id = $2
RETURNING *;
```

#### Query 4: Get Unread Count for User
```sql
SELECT COUNT(*) as unread_count
FROM notifications
WHERE user_id = $1
  AND is_read = FALSE
  AND deleted_at IS NULL;
```


## Stage 3: Query Optimization & Performance

### Query Analysis

**Is this query accurate?** Yes, functionally correct but inefficient.

**Why is it slow?**
1. No indexes on `studentId` and `isRead` columns
2. Full table scan required to check all 5 million notifications
3. Sorting on unindexed `createdAt` column is expensive
4. Multiple database server round-trips for large result sets

### Proposed Solution: Strategic Indexing

**Create Composite Index:**
```sql
CREATE INDEX idx_notifications_user_status_time 
ON notifications(studentId, isRead, createdAt DESC);
```

**Optimized Query:**
```sql
SELECT id, studentId, message, createdAt, notificationType
FROM notifications
WHERE studentId = 1862 
  AND isRead = false
LIMIT 100
ORDER BY createdAt DESC;
```

**Benefits:**
- Index covers all query columns (Index-only scan possible)
- Query execution time: ~50-100ms (vs 5-10 seconds previously)
- Server-side sorting becomes efficient

### Query to Find Placement Notifications

```sql
SELECT DISTINCT s.studentId, s.studentName, n.message, n.createdAt
FROM notifications n
INNER JOIN students s ON n.studentId = s.studentId
WHERE n.notificationType = 'Placement'
  AND n.createdAt >= CURRENT_TIMESTAMP - INTERVAL '7 days'
  AND n.isRead = false
ORDER BY n.createdAt DESC;
```


## Stage 4: Database Indexing Strategy

### Performance Optimization Strategy

**Problem:** DB overwhelmed with read requests on every page load

**Multi-Layer Solution:**

#### 1. Caching Layer (Redis)
```
Frontend Request → API Server → Redis Cache → PostgreSQL DB
```

**Cache Strategy:**
- Store recent notifications in Redis with 5-minute TTL
- Cache unread count separately with 1-minute TTL
- Invalidate on new notification creation

**Implementation:**
```python
# Pseudocode
cache_key = f"notifications:{user_id}:recent"
cached_data = redis.get(cache_key)

if cached_data:
    return cached_data
else:
    notifications = db.query(user_id)
    redis.setex(cache_key, 300, notifications)  # 5 min TTL
    return notifications
```

#### 2. Database Indexing
- Composite index on `(studentId, isRead, createdAt DESC)`
- Separate index on `createdAt` for archival queries
- Index on `notificationType` for filtering

#### 3. Pagination
- Limit fetched records: `LIMIT 20 OFFSET 0`
- Client-side: Load more functionality
- Reduces payload size significantly

#### 4. Database Partitioning
- Partition by month: `notifications_2024_01`, `notifications_2024_02`
- Query only recent partitions for active users
- Archive old data separately

#### 5. Read Replicas
- Setup PostgreSQL read replicas
- Route read traffic to replicas
- Write operations to primary only

### Expected Performance Improvement

| Metric | Before | After |
|--------|--------|-------|
| Response Time | 8-15s | 200-500ms |
| DB CPU Usage | 85-95% | 15-25% |
| Concurrent Users | 50-100 | >500 |
| Data Transferred | 2-5MB | 100-200KB |

---

**How is this effective:**
- Redis caching eliminates repeated DB queries
- Proper indexing reduces query execution time
- Pagination limits data transfer
- Read replicas distribute load
- Partitioning speeds up queries on large datasets

**Tradeoffs:**
- Cache invalidation is complex
- Stale data if TTL too long
- Infrastructure complexity increases
- Requires careful monitoring


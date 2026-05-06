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



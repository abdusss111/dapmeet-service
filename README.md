# Dapmeet API - Prompt Management System

## 🎯 **Overview**
Dapmeet is a meeting transcription service with a comprehensive prompt management system that allows both administrators and regular users to create, manage, and use custom prompts for AI interactions.

## 🏗️ **System Architecture**

### **Database Models**
- **User**: Core user accounts with authentication
- **Prompt**: Custom prompts with type classification (admin/user)
- **Meeting**: Meeting sessions with transcription data
- **TranscriptSegment**: Individual transcription segments

### **Authentication**
- JWT-based authentication using Google OAuth
- Role-based access control (admin vs user)
- Secure token validation for all protected endpoints

---

## 👑 **Admin Interface & Endpoints**

### **Admin Dashboard Overview**
The admin interface provides comprehensive control over all prompts in the system, including both admin-created prompts and user-created prompts.

### **Admin Prompt Management**

#### **1. Create Admin Prompt**
```typescript
// UI: Admin Prompt Creation Form
interface AdminPromptForm {
  name: string;        // Required, unique
  content: string;     // Required, prompt text
  is_active: boolean;  // Default: true
}

// API Call
POST /admin/prompts
Authorization: Bearer <admin_jwt_token>
Content-Type: application/json

{
  "name": "meeting_summary_prompt",
  "content": "Summarize the key points from this meeting transcript...",
  "is_active": true
}
```

#### **2. List All Admin Prompts**
```typescript
// UI: Admin Prompts Table with Filters
interface AdminPromptsTable {
  filters: {
    name?: string;        // Search by name
    is_active?: boolean;  // Filter by status
  };
  pagination: {
    page: number;
    limit: number;
  };
}

// API Call
GET /admin/prompts?name=summary&is_active=true&page=1&limit=20
Authorization: Bearer <admin_jwt_token>
```

#### **3. Get Admin Prompt by ID**
```typescript
// UI: Prompt Detail View/Edit Form
// Used when clicking on a prompt row or edit button

// API Call
GET /admin/prompts/{prompt_id}
Authorization: Bearer <admin_jwt_token>
```

#### **4. Get Admin Prompt by Name**
```typescript
// UI: Quick Search/Quick Access
// Used for direct prompt lookup without browsing

// API Call
GET /admin/prompts/by-name/{prompt_name}
Authorization: Bearer <admin_jwt_token>
```

#### **5. Update Admin Prompt**
```typescript
// UI: Prompt Edit Form (pre-populated with current data)
interface AdminPromptUpdate {
  name?: string;
  content?: string;
  is_active?: boolean;
}

// API Call
PUT /admin/prompts/{prompt_id}
Authorization: Bearer <admin_jwt_token>
Content-Type: application/json

{
  "content": "Updated prompt content...",
  "is_active": false
}
```

#### **6. Delete Admin Prompt**
```typescript
// UI: Delete Confirmation Modal
// Shows warning about prompt deletion

// API Call
DELETE /admin/prompts/{prompt_id}
Authorization: Bearer <admin_jwt_token>
```

#### **7. Admin Prompt Statistics**
```typescript
// UI: Dashboard Metrics Card
// Shows total count of admin prompts

// API Call
GET /admin/prompts/stats/count
Authorization: Bearer <admin_jwt_token>
```

### **Admin UI Components**

#### **Main Dashboard**
```
┌─────────────────────────────────────────────────────────────┐
│                    ADMIN DASHBOARD                          │
├─────────────────────────────────────────────────────────────┤
│  📊 System Overview                                        │
│  ├─ Total Users: 150                                       │
│  ├─ Total Meetings: 89                                     │
│  ├─ Admin Prompts: 12                                      │
│  └─ User Prompts: 45                                       │
├─────────────────────────────────────────────────────────────┤
│  🎯 Quick Actions                                          │
│  ├─ [Create New Admin Prompt]                              │
│  ├─ [View All Prompts]                                     │
│  └─ [System Health Check]                                  │
└─────────────────────────────────────────────────────────────┘
```

#### **Admin Prompts Management Page**
```
┌─────────────────────────────────────────────────────────────┐
│                ADMIN PROMPTS MANAGEMENT                     │
├─────────────────────────────────────────────────────────────┤
│  🔍 Filters                                                │
│  Name: [________________] Active: [✓] [Apply Filters]      │
├─────────────────────────────────────────────────────────────┤
│  ➕ [Create New Admin Prompt]                              │
├─────────────────────────────────────────────────────────────┤
│  📋 Prompts Table                                          │
│  ┌─────┬──────────────┬──────────────┬─────────┬─────────┐ │
│  │ ID  │ Name         │ Content      │ Status  │ Actions │ │
│  ├─────┼──────────────┼──────────────┼─────────┼─────────┤ │
│  │ 1   │ meeting_sum  │ Summarize... │ Active  │ [Edit]  │ │
│  │ 2   │ action_items │ Extract...   │ Active  │ [Edit]  │ │
│  └─────┴──────────────┴──────────────┴─────────┴─────────┘ │
├─────────────────────────────────────────────────────────────┤
│  📄 Pagination: [1] [2] [3] ... [Next]                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 👤 **User Interface & Endpoints**

### **User Dashboard Overview**
The user interface allows individual users to create and manage their own prompts, with access limited to their personal prompt collection.

### **User Prompt Management**

#### **1. Create User Prompt**
```typescript
// UI: User Prompt Creation Form
interface UserPromptForm {
  name: string;        // Required, unique per user
  content: string;     // Required, prompt text
  is_active: boolean;  // Default: true
}

// API Call
POST /api/prompts
Authorization: Bearer <user_jwt_token>
Content-Type: application/json

{
  "name": "my_custom_prompt",
  "content": "Analyze this transcript and identify action items...",
  "is_active": true
}
```

#### **2. List User's Prompts**
```typescript
// UI: User's Personal Prompts Table
interface UserPromptsTable {
  pagination: {
    page: number;
    limit: number;
  };
}

// API Call
GET /api/prompts?page=1&limit=20
Authorization: Bearer <user_jwt_token>
```

#### **2a. List Admin Prompts (Read-Only)**
```typescript
// UI: Admin Prompts Table (Read-Only View)
interface AdminPromptsReadonlyTable {
  pagination: {
    page: number;
    limit: number;
  };
}

// API Call
GET /api/prompts/admin-prompts?page=1&limit=20
Authorization: Bearer <user_jwt_token>
```

#### **3. Get User Prompt Names (Quick Access)**
```typescript
// UI: Prompt Names Dropdown/Selector
// Used for quick prompt selection in other features

// API Call
GET /api/prompts/names
Authorization: Bearer <user_jwt_token>

// Response includes prompt names in user response
{
  "id": "user123",
  "email": "user@example.com",
  "name": "John Doe",
  "prompt_names": ["meeting_analyzer", "action_extractor", "summary_generator"]
}
```

#### **4. Get User Prompt by ID**
```typescript
// UI: Prompt Detail View/Edit Form
// Used when editing existing prompts

// API Call
GET /api/prompts/{prompt_id}
Authorization: Bearer <user_jwt_token>
```

#### **4a. Get Admin Prompt by ID (Read-Only)**
```typescript
// UI: Admin Prompt Detail View (Read-Only)
// Used when viewing admin prompts for reference

// API Call
GET /api/prompts/admin-prompts/{prompt_id}
Authorization: Bearer <user_jwt_token>
```

#### **5. Get User Prompt by Name**
```typescript
// UI: Quick Search within User's Prompts
// Used for direct access to user's own prompts

// API Call
GET /api/prompts/by-name/{prompt_name}
Authorization: Bearer <user_jwt_token>
```

#### **5a. Get Admin Prompt by Name (Read-Only)**
```typescript
// UI: Quick Search within Admin Prompts
// Used for direct access to admin prompts for reference

// API Call
GET /api/prompts/admin-prompts/by-name/{prompt_name}
Authorization: Bearer <user_jwt_token>
```

#### **6. Update User Prompt**
```typescript
// UI: Prompt Edit Form (pre-populated)
interface UserPromptUpdate {
  name?: string;
  content?: string;
  is_active?: boolean;
}

// API Call
PUT /api/prompts/{prompt_id}
Authorization: Bearer <user_jwt_token>
Content-Type: application/json

{
  "content": "Updated user prompt content...",
  "is_active": false
}
```

#### **7. Delete User Prompt**
```typescript
// UI: Delete Confirmation Modal
// Shows warning about prompt deletion

// API Call
DELETE /api/prompts/{prompt_id}
Authorization: Bearer <user_jwt_token>
```

#### **8. User Prompt Statistics**
```typescript
// UI: Personal Dashboard Metrics
// Shows user's prompt count

// API Call
GET /api/prompts/stats/count
Authorization: Bearer <user_jwt_token>
```

#### **8a. Admin Prompt Statistics (Read-Only)**
```typescript
// UI: Admin Prompts Overview
// Shows total count of admin prompts

// API Call
GET /api/prompts/admin-prompts/stats/count
Authorization: Bearer <user_jwt_token>
```

### **User UI Components**

#### **User Dashboard**
```
┌─────────────────────────────────────────────────────────────┐
│                    USER DASHBOARD                           │
├─────────────────────────────────────────────────────────────┤
│  👤 Personal Overview                                      │
│  ├─ My Prompts: 8                                          │
│  ├─ Active Prompts: 6                                      │
│  └─ Recent Activity: 3 meetings                            │
├─────────────────────────────────────────────────────────────┤
│  🎯 Quick Actions                                          │
│  ├─ [Create New Prompt]                                    │
│  ├─ [View My Prompts]                                      │
│  └─ [Join Meeting]                                         │
└─────────────────────────────────────────────────────────────┘
```

#### **User Prompts Management Page**
```
┌─────────────────────────────────────────────────────────────┐
│                MY PROMPTS MANAGEMENT                        │
├─────────────────────────────────────────────────────────────┤
│  ➕ [Create New Prompt]                                    │
├─────────────────────────────────────────────────────────────┤
│  📋 My Prompts Table                                       │
│  ┌─────┬──────────────┬──────────────┬─────────┬─────────┐ │
│  │ ID  │ Name         │ Content      │ Status  │ Actions │ │
│  ├─────┼──────────────┼──────────────┼─────────┼─────────┤ │
│  │ 1   │ meeting_ana  │ Analyze...   │ Active  │ [Edit]  │ │
│  │ 2   │ action_ext   │ Extract...   │ Active  │ [Edit]  │ │
│  │ 3   │ summary_gen  │ Generate...  │ Inactive│ [Edit]  │ │
│  └─────┴──────────────┴──────────────┴─────────┴─────────┘ │
├─────────────────────────────────────────────────────────────┤
│  📄 Pagination: [1] [2] [Next]                            │
├─────────────────────────────────────────────────────────────┤
│  🔍 [View Admin Prompts] (Read-Only)                      │
└─────────────────────────────────────────────────────────────┘
```

#### **Admin Prompts Read-Only View**
```
┌─────────────────────────────────────────────────────────────┐
│                ADMIN PROMPTS (READ-ONLY)                    │
├─────────────────────────────────────────────────────────────┤
│  📋 Admin Prompts Table                                    │
│  ┌─────┬──────────────┬──────────────┬─────────┬─────────┐ │
│  │ ID  │ Name         │ Content      │ Status  │ Actions │ │
│  ├─────┼──────────────┼──────────────┼─────────┼─────────┤ │
│  │ 1   │ system_sum   │ System...    │ Active  │ [View]  │ │
│  │ 2   │ global_ana   │ Global...    │ Active  │ [View]  │ │
│  │ 3   │ default_gen  │ Default...   │ Active  │ [View]  │ │
│  └─────┴──────────────┴──────────────┴─────────┴─────────┘ │
├─────────────────────────────────────────────────────────────┤
│  📄 Pagination: [1] [2] [Next]                            │
├─────────────────────────────────────────────────────────────┤
│  🔙 [Back to My Prompts]                                   │
└─────────────────────────────────────────────────────────────┘
```

#### **Prompt Creation/Edit Form**
```
┌─────────────────────────────────────────────────────────────┐
│                CREATE/EDIT PROMPT                           │
├─────────────────────────────────────────────────────────────┤
│  📝 Prompt Details                                         │
│  Name: [________________________]                          │
│  (Must be unique)                                          │
│                                                             │
│  Content:                                                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ [Enter your prompt content here...]                    │ │
│  │                                                         │
│  │ Example: "Analyze this transcript and identify         │ │
│  │ key action items, decisions made, and follow-up        │ │
│  │ tasks for the team."                                    │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  Status: [✓] Active                                        │
│                                                             │
│  [Save Prompt] [Cancel]                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔗 **Integration Examples**

### **Frontend Integration (React/TypeScript)**

#### **Admin Prompt Service**
```typescript
class AdminPromptService {
  private baseUrl = '/admin/prompts';
  private token: string;

  constructor(token: string) {
    this.token = token;
  }

  async createPrompt(data: AdminPromptCreate): Promise<PromptResponse> {
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    return response.json();
  }

  async getPrompts(filters: PromptFilters): Promise<PromptListResponse> {
    const params = new URLSearchParams();
    if (filters.name) params.append('name', filters.name);
    if (filters.is_active !== undefined) params.append('is_active', filters.is_active.toString());
    
    const response = await fetch(`${this.baseUrl}?${params}`);
    return response.json();
  }
}
```

#### **User Prompt Service**
```typescript
class UserPromptService {
  private baseUrl = '/api/prompts';
  private token: string;

  constructor(token: string) {
    this.token = token;
  }

  async getPromptNames(): Promise<string[]> {
    const response = await fetch(`${this.baseUrl}/names`, {
      headers: {
        'Authorization': `Bearer ${this.token}`
      }
    });
    const data = await response.json();
    return data.prompt_names;
  }

  async createPrompt(data: UserPromptCreate): Promise<PromptResponse> {
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    return response.json();
  }

  // Read-only access to admin prompts
  async getAdminPrompts(page: number = 1, limit: number = 20): Promise<PromptListResponse> {
    const response = await fetch(`${this.baseUrl}/admin-prompts?page=${page}&limit=${limit}`, {
      headers: {
        'Authorization': `Bearer ${this.token}`
      }
    });
    return response.json();
  }

  async getAdminPromptById(promptId: number): Promise<PromptResponse> {
    const response = await fetch(`${this.baseUrl}/admin-prompts/${promptId}`, {
      headers: {
        'Authorization': `Bearer ${this.token}`
      }
    });
    return response.json();
  }

  async getAdminPromptByName(promptName: string): Promise<PromptResponse> {
    const response = await fetch(`${this.baseUrl}/admin-prompts/by-name/${promptName}`, {
      headers: {
        'Authorization': `Bearer ${this.token}`
      }
    });
    return response.json();
  }
}
```

### **Meeting Integration**
```typescript
// When starting a meeting, user can select from their prompts
interface MeetingSetup {
  meetingId: string;
  selectedPrompt: string;  // Prompt name from user's collection
  participants: string[];
}

// The selected prompt is used for AI processing during the meeting
const startMeeting = async (setup: MeetingSetup) => {
  // Get the actual prompt content
  const prompt = await userPromptService.getPromptByName(setup.selectedPrompt);
  
  // Use prompt.content for AI processing
  const aiResponse = await processMeetingWithPrompt(
    setup.meetingId, 
    prompt.content
  );
};
```

---

## 🚀 **Getting Started**

### **1. Environment Setup**
```bash
# Required environment variables
DATABASE_URL=postgresql://user:pass@host/db
DATABASE_URL_ASYNC=postgresql+asyncpg://user:pass@host/db
NEXTAUTH_SECRET=your_jwt_secret
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

### **2. Database Migration**
```bash
# Run migrations to create prompts table
alembic upgrade head
```

### **3. Start the Service**
```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python -m src.dapmeet.cmd.main
```

### **4. Test Endpoints**
```bash
# Health check
curl http://localhost:8000/health

# Create admin prompt (requires admin token)
curl -X POST http://localhost:8000/admin/prompts \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"test_prompt","content":"Test content"}'
```

---

## 🔒 **Security & Access Control**

### **Admin Access**
- Full CRUD operations on admin prompts
- View and manage all prompts in the system
- System-wide prompt management capabilities

### **User Access**
- **Full CRUD operations** on their own prompts
- **Read-only access** to admin prompts (can view, cannot modify)
- Cannot modify other users' prompts
- Prompt names included in user profile response
- Can browse and reference admin prompts for inspiration

### **Authentication Flow**
1. User authenticates via Google OAuth
2. JWT token issued with user ID and role
3. All prompt endpoints require valid JWT
4. Ownership checks prevent unauthorized access

---

## 📊 **API Response Examples**

### **Prompt Response**
```json
{
  "id": 1,
  "name": "meeting_summarizer",
  "content": "Summarize the key points from this meeting...",
  "prompt_type": "user",
  "user_id": "user123",
  "is_active": true,
  "created_at": "2025-01-27T10:00:00Z",
  "updated_at": "2025-01-27T10:00:00Z"
}
```

### **User with Prompt Names**
```json
{
  "id": "user123",
  "email": "user@example.com",
  "name": "John Doe",
  "prompt_names": ["meeting_analyzer", "action_extractor"]
}
```

### **Prompt List Response**
```json
{
  "prompts": [...],
  "total": 25,
  "page": 1,
  "limit": 20,
  "total_pages": 2,
  "has_next": true,
  "has_prev": false
}
```

---

## 🎨 **UI Design Principles**

### **Admin Interface**
- **Professional & Comprehensive**: Full system overview
- **Efficient Management**: Bulk operations and filtering
- **System Monitoring**: Health checks and statistics
- **Access Control**: Role-based permissions

### **User Interface**
- **Personal & Intuitive**: Focus on individual needs
- **Quick Access**: Easy prompt selection and creation
- **Visual Feedback**: Clear status indicators
- **Responsive Design**: Works on all devices

### **Common Elements**
- **Consistent Navigation**: Unified header and sidebar
- **Responsive Tables**: Sortable columns with pagination
- **Form Validation**: Real-time error checking
- **Loading States**: Progress indicators for async operations
- **Error Handling**: User-friendly error messages

This comprehensive prompt management system provides both administrators and users with powerful tools to create, manage, and utilize custom prompts while maintaining proper security boundaries and user experience.

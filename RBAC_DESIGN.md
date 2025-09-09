# RBAC vs ABAC Design & Tenant Isolation

## Architecture Overview

This implementation provides a hybrid RBAC/ABAC system with strict tenant isolation for multi-organizational deployments.

## Roles & Permissions

### Role Hierarchy
- **ADMIN**: Full access to organization resources (CRUD operations)
- **ANALYST**: Read/write access to documents and analytics
- **VIEWER**: Read-only access to resources, limited to own data

### RBAC Implementation
```python
# Role-based gates using FastAPI dependencies
@router.post("/documents")
async def create_document(
    context: UserContext = Depends(require_roles([Role.ADMIN, Role.ANALYST]))
):
    # Only admins and analysts can create documents
```

### ABAC Implementation
```python
# Attribute-based ownership checks
if context.role == Role.VIEWER:
    query = query.filter(ChatHistory.user_id == context.user.id)
```

## Tenant Isolation

### Data Layer Enforcement
Every resource table includes `org_id` for strict tenant isolation:

```sql
-- All queries automatically filtered by organization
SELECT * FROM documents WHERE org_id = ? AND ...
SELECT * FROM chat_history WHERE org_id = ? AND user_id = ?
```

### Service Layer Pattern
```python
# Automatic tenant filtering in service layer
documents = RBACService.filter_by_org(db.query(Document), context.org_id).all()
```

## Database Schema

### Organizations
```sql
CREATE TABLE organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    slug VARCHAR UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### User-Organization Memberships
```sql
CREATE TABLE user_org_memberships (
    id SERIAL PRIMARY KEY,
    org_id INTEGER REFERENCES organizations(id),
    user_id INTEGER REFERENCES users(id),
    role role_enum NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(org_id, user_id)
);
```

### Tenant-Isolated Resources
```sql
-- Every resource table has org_id
ALTER TABLE documents ADD COLUMN org_id INTEGER NOT NULL;
ALTER TABLE chat_history ADD COLUMN org_id INTEGER NOT NULL;
CREATE INDEX idx_documents_org_id ON documents(org_id);
CREATE INDEX idx_chat_history_org_id ON chat_history(org_id);
```

## Security Dependencies

### Organization Membership Check
```python
def require_org_member(org_id: int):
    # Ensures user belongs to organization
    # Returns UserContext with org_id and role
```

### Role-Based Access Control
```python
def require_roles(allowed_roles: List[Role]):
    # Enforces minimum role requirements
    # Raises 403 if insufficient permissions
```

### Resource Ownership (ABAC)
```python
def require_resource_access(resource_org_id: int):
    # Validates resource belongs to user's organization
    # Prevents cross-tenant data access
```

## RBAC vs ABAC Trade-offs

### RBAC Advantages
- **Simple to implement**: Clear role hierarchy
- **Predictable permissions**: Easy to audit and understand
- **Performance**: Fast role-based queries
- **Scalable**: Works well with organizational structures

### RBAC Limitations
- **Rigid**: Hard to handle complex permission scenarios
- **Over-privileged**: Users may get more access than needed
- **Context-blind**: Doesn't consider resource ownership or attributes

### ABAC Advantages
- **Fine-grained control**: Permissions based on attributes (ownership, location, time)
- **Dynamic**: Permissions can change based on context
- **Principle of least privilege**: More precise access control

### ABAC Limitations
- **Complex**: Harder to implement and debug
- **Performance overhead**: More complex queries and evaluations
- **Policy management**: Difficult to maintain complex attribute rules

## Implementation Strategy

### Hybrid Approach
1. **RBAC for organizational permissions**: Admin/Analyst/Viewer roles
2. **ABAC for resource ownership**: Users can only access their own data (where applicable)
3. **Tenant isolation**: Strict org_id filtering at data layer

### Performance Considerations
- **Database indexes**: All tenant-filtered columns are indexed
- **Query optimization**: Tenant filters applied early in query execution
- **Caching**: Role and membership information cached per request

### Security Guarantees
- **No cross-tenant access**: org_id enforced on every query
- **Role enforcement**: FastAPI dependencies validate permissions
- **Ownership validation**: ABAC checks prevent unauthorized resource access
- **Audit trail**: All access attempts logged with user and organization context

## Migration Strategy

1. **Add RBAC tables**: Organizations and memberships
2. **Add tenant columns**: org_id to all resource tables
3. **Update application code**: Use new dependencies and filters
4. **Data migration**: Assign existing data to default organization
5. **Gradual rollout**: Enable multi-tenancy per organization

This design ensures secure, scalable multi-tenant operations while maintaining performance and simplicity where possible.
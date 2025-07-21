# Messaging API Postman Collection

## Setup Instructions

1. Import the `messaging_api.postman_collection.json` into Postman
2. Set up environment variables:
   - `base_url`: Your API base URL (default: http://localhost:8000)
3. Create test users first if needed

## Test Scenarios Covered

### Authentication
- JWT Token obtainment
- Token refresh

### Conversations
- Create new conversation
- List conversations (paginated)

### Messages
- Send new message
- List messages (with pagination)

### Negative Tests
- Unauthorized access attempts
- Non-participant access attempts

## Running Tests

1. Start your Django development server
2. Run the collection in Postman
3. Verify all endpoints return expected status codes:
   - 200 for successful operations
   - 401 for unauthorized access
   - 403 for forbidden operations
   - 404 for not found resources

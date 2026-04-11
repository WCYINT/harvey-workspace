---
name: baas
description: Use aipexbase-cli to operate AiPexBase BaaS service, supporting database operations, application management, user authentication, etc.
allowed-tools: Bash, Read, Write, Grep, Glob
---

# AiPexBase CLI Skill

## About AiPexBase

**AiPexBase** is a BaaS (Backend as a Service) platform that provides database, authentication, file storage, and other backend capabilities.

**GitHub**: https://github.com/kuafuai/aipexbase

**Prerequisites**:
- Deployed AiPexBase service (to get baseUrl)
- API Key (obtained from service admin dashboard)
- Installed aipexbase-cli: `npm install -g aipexbase-cli`

**Core command format:**
```bash
baas -c <config-file> <command> [options]
```

**Important**: All commands must use the `-c` parameter to specify the configuration file!

### Configuration File

**Must create configuration file first** (even an empty file is fine):
```bash
echo '{}' > config.json
```

- Configuration can be filled or updated through the `config` command.

---

## Command Reference

### 1. Configuration Management

```bash
# Set configuration
baas -c config.json config --base-url "http://localhost:8080" --api-key "your-api-key"

# View configuration
baas -c config.json config --show
```

### 2. Database Operations

**Query:**
```bash
# Query all
baas -c config.json db list <table>

# Equal query
baas -c config.json db list <table> --where '{"status": "active"}'

# Comparison query
baas -c config.json db list <table> --where '{"price": {"gt": 100}}'

# Multiple conditions
baas -c config.json db list <table> --where '{"price": {"gte": 100, "lte": 1000}, "status": "active"}'

# Pagination
baas -c config.json db page <table> --page-num 1 --page-size 20

# Sorting
baas -c config.json db list <table> --order "created_at:desc"

# Single record
baas -c config.json db get <table> --where '{"id": "rec_xxx"}'
```

**Modify:**
```bash
# Insert
baas -c config.json db insert <table> --data '{"field1": "value1", "field2": "value2"}'

# Update
baas -c config.json db update <table> --where '{"id": "rec_xxx"}' --data '{"field1": "new-value"}'

# Delete
baas -c config.json db delete <table> --where '{"id": "rec_xxx"}'
```

**where operators:**

| Operator | Description | Example |
|----------|-------------|---------|
| Direct value | Equal | `{"status": "active"}` |
| `gt` | Greater than | `{"price": {"gt": 100}}` |
| `gte` | Greater than or equal | `{"age": {"gte": 18}}` |
| `lt` | Less than | `{"stock": {"lt": 10}}` |
| `lte` | Less than or equal | `{"score": {"lte": 60}}` |
| `neq` | Not equal | `{"status": {"neq": "deleted"}}` |
| `like` | Fuzzy match | `{"name": {"like": "Zhang"}}` |
| `in` | In array | `{"status": {"in": ["active", "pending"]}}` |
| `between` | Range | `{"price": {"between": [100, 1000]}}` |

### 3. Application and Table Management

```bash
# Create application
baas -c config.json manage create-app --name "App Name" --user-id "User ID"

# Create table
baas -c config.json manage create-table \
  --app-id "App ID" \
  --table-name "Table Name" \
  --columns '[
    {"columnName": "name", "columnType": "string", "columnComment": "Name"},
    {"columnName": "age", "columnType": "number", "columnComment": "Age"}
  ]'
```

**Field types:**

| Type | Description | Type | Description |
|------|-------------|------|-------------|
| `string` | Short text | `password` | Password (encrypted) |
| `text` | Long text | `phone` | Phone (validated) |
| `number` | Integer | `email` | Email (validated) |
| `decimal` | Decimal | `images` | Images |
| `boolean` | Boolean | `files` | Files |
| `date` | Date | `videos` | Videos |
| `datetime` | Datetime | `quote` | Reference |

### 4. User Authentication

```bash
# Login
baas -c config.json login --phone "13800138000" --code "123456"

# Logout
baas -c config.json logout

# Generate login link
baas -c config.json login-link --channel "web" --user-id "user123"
```

### 5. File Upload

```bash
baas -c config.json upload --file "/path/to/file.jpg" --table "Table Name"
```

---

## Parameter Specifications

### JSON Format Requirements

**Rules:**
1. Use single quotes `'...'` for outer layer
2. Use double quotes `"..."` for inner layer
3. JSON must be valid

**Correct examples:**
```bash
✓ --data '{"name": "Zhang San", "age": 25}'
✓ --where '{"status": "active"}'
```

**Incorrect examples:**
```bash
✗ --data "{"name": "Zhang San"}"      # Outer layer cannot use double quotes
✗ --data "{'name': 'Zhang San'}"      # Inner layer cannot use single quotes
```

### columns Format

```json
[
  {
    "columnName": "Field Name",
    "columnType": "Field Type",
    "columnComment": "Field Description"
  }
]
```

---

## Quick Example

```bash
# 1. Create configuration file
echo '{}' > config.json

# 2. Set configuration
baas -c config.json config --base-url "http://localhost:8080" --api-key "your-key"

# 3. Create application
baas -c config.json manage create-app --name "My App" --user-id "admin"

# 4. Create table
baas -c config.json manage create-table \
  --app-id "baas_xxx" \
  --table-name "users" \
  --columns '[{"columnName": "username", "columnType": "string", "columnComment": "Username"}]'

# 5. Insert data
baas -c config.json db insert users --data '{"username": "zhangsan"}'

# 6. Query data
baas -c config.json db list users --where '{"username": "zhangsan"}'
```

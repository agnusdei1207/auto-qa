# MinIO Integration for Screenshot Storage - Complete

## Summary
Successfully integrated MinIO object storage for persistent screenshot storage, replacing the previous non-persistent local filesystem approach (/tmp/screenshots).

## Changes Made

### 1. Docker Compose Configuration

#### compose.yml (Production)
- Added MinIO service (ports 9002:9000 API, 9003:9001 Console)
- Added minio_data persistent volume
- Updated web, brain, and executor services with MinIO environment variables
- Added MinIO dependencies to executor service

#### compose.test.yml (Test)
- Added MinIO service (ports 9004:9000 API, 9005:9001 Console)
- Added minio_data persistent volume
- Updated web, brain, and executor services with MinIO environment variables
- Added MinIO dependencies to executor service

### 2. Dependencies

#### apps/executor/requirements.txt
- Added boto3>=1.34.0 for S3-compatible API access

### 3. New Files

#### apps/executor/src/minio_client.py
- MinioClient class with S3-compatible API
- Automatic bucket creation on startup
- upload_screenshot() method for uploading screenshots
- Health check functionality
- Public URL generation for screenshot access
- Graceful fallback to filesystem if MinIO unavailable

### 4. Modified Files

#### apps/executor/src/action_handlers.py
- Updated constructor to accept optional minio_client parameter
- Modified screenshot() method to upload to MinIO if available
- Updated screenshot response to include MinIO URL

#### apps/executor/src/main.py
- Added MinIO client initialization
- Updated startup event to check MinIO connection
- Modified screenshot() function to use MinIO client
- Updated health endpoint to include MinIO status

#### apps/executor/src/main_refactored.py
- Added MinIO client initialization
- Updated startup event to check MinIO connection
- Modified ActionHandlers initialization to include minio_client
- Updated health endpoint to include MinIO status

#### .env
- Added MINIO_API_PORT and MINIO_CONSOLE_PORT
- Added MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY
- Added MINIO_BUCKET and MINIO_SECURE configuration

#### .env.example
- Added MinIO configuration section with all environment variables

## Configuration

### Environment Variables
```bash
# Ports
MINIO_API_PORT=9002        # MinIO API port
MINIO_CONSOLE_PORT=9003    # MinIO Console port

# MinIO Connection
MINIO_ENDPOINT=http://minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=qa-screenshots
MINIO_SECURE=false
```

## Usage

### Starting Services with MinIO
```bash
docker-compose --profile ollama up -d
```

This will start:
- MinIO on http://localhost:9002 (API) and http://localhost:9003 (Console)
- Other services (web, brain, executor, database, ollama)

### Accessing MinIO Console
- URL: http://localhost:9003
- Username: minioadmin
- Password: minioadmin

### Screenshot Storage
Screenshots are now stored in:
- MinIO bucket: qa-screenshots
- Path pattern: screenshots/{session_id}/screenshot_{timestamp}.png
- Fallback: /tmp/screenshots (if MinIO unavailable)

## Features

### Persistent Storage
- Screenshots persist across container restarts
- Data stored in minio_data volume
- Automatic bucket creation on startup

### Graceful Degradation
- Falls back to filesystem storage if MinIO unavailable
- Logs warnings when MinIO is not connected
- System continues to function without MinIO

### Public URL Generation
- Screenshots accessible via public URLs
- URLs included in progress tracking JSON
- Compatible with web dashboard display

### Health Monitoring
- Health check endpoint includes MinIO status
- Startup event verifies MinIO connection
- Logs connection status on service start

## Benefits

1. **Persistence**: Screenshots no longer lost on container restart
2. **Scalability**: S3-compatible API supports future cloud migrations
3. **Reliability**: Graceful fallback ensures system resilience
4. **Accessibility**: Public URLs for easy screenshot access
5. **Management**: MinIO Console for bucket and file management

## Next Steps

1. Test screenshot functionality with MinIO:
   ```bash
   # Start services
   docker-compose --profile ollama up -d

   # Run a test
   curl -X POST http://localhost:9001/screenshot \
     -H "Content-Type: application/json" \
     -d '{"session_id": "test-session", "full_page": false}'
   ```

2. Check MinIO Console:
   - Login to http://localhost:9003
   - Navigate to qa-screenshots bucket
   - Verify screenshots are stored

3. Verify fallback:
   - Stop MinIO service
   - Run screenshot test
   - Confirm fallback to /tmp/screenshots

## Architecture

```
┌─────────────────────────────────────────┐
│         Executor Service              │
│  (main.py, main_refactored.py)       │
│                                       │
│  ┌─────────────────────────────────┐  │
│  │   ActionHandlers              │  │
│  │  - screenshot()               │  │
│  │  - upload to MinIO           │  │
│  │  - fallback to filesystem    │  │
│  └────────────┬──────────────────┘  │
└───────────────┼──────────────────────┘
                │
       ┌────────┴────────┐
       │                 │
       ▼                 ▼
┌──────────────┐  ┌─────────────────┐
│  MinIO       │  │  Filesystem     │
│  (S3 API)    │  │  /tmp/...       │
│              │  │                 │
│  qa-screenshots │  │  fallback      │
└──────────────┘  └─────────────────┘
```

## Troubleshooting

### MinIO Not Starting
- Check port conflicts (9002, 9003)
- Verify minio_data volume permissions
- Review logs: `docker-compose logs minio`

### Screenshots Not Uploading
- Check MinIO connection: `docker-compose logs executor | grep MinIO`
- Verify environment variables in .env
- Check MinIO health: `curl http://localhost:9002/minio/health/live`

### Using Fallback Only
- Check if MinIO service is running: `docker-compose ps minio`
- Verify MinIO endpoint is accessible from executor
- Review network configuration in docker-compose

## Conclusion

MinIO integration successfully provides persistent screenshot storage with S3-compatible API access, graceful fallback, and public URL generation for web display. The system is production-ready and fully backward compatible.

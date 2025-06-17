# Docker Network Test

This is a simple Docker-based network connectivity test designed to diagnose networking issues in SecretVM environments.

## What it tests

1. **Basic Connectivity**
   - Ping to Google DNS (8.8.8.8)
   - Ping to Cloudflare DNS (1.1.1.1)

2. **DNS Resolution**
   - Lookup google.com
   - Lookup Secret Network endpoints
   - Check DNS resolver configuration

3. **HTTP/HTTPS Connectivity**
   - HTTP and HTTPS requests to Google
   - HTTPS requests to Secret Network LCD endpoints
   - HTTPS requests to Secret Network RPC endpoints

4. **Secret Network Specific**
   - Node info queries
   - Contract query endpoints
   - Alternative Secret Network endpoints

5. **TLS/SSL**
   - Certificate validation tests
   - TLS handshake tests

## How to use

1. **Download docker-compose.yaml:**
   ```bash
   wget https://raw.githubusercontent.com/MrGarbonzo/docker_test/main/docker-compose.yaml
   ```

2. **Run the container:**
   ```bash
   docker-compose up -d
   ```

3. **View results:**
   - Open browser to http://your-secretvm-ip:8080
   - View live dashboard with test results
   - API endpoints also available at `/api/results` and `/api/latest`

4. **Monitor logs:**
   ```bash
   docker-compose logs -f
   ```

The container image is automatically built and published to GitHub Container Registry when code is pushed to this repository.

## What to look for

- **All tests passing**: Network connectivity is good
- **DNS failures**: DNS resolution issues
- **HTTPS failures**: TLS/certificate or firewall issues
- **Secret Network specific failures**: Endpoint-specific blocking
- **Timeout errors**: General connectivity or firewall issues

## Files

- `Dockerfile`: Container definition with network tools
- `docker-compose.yaml`: Service configuration
- `network_test.py`: Main test script with web dashboard
- `requirements.txt`: Python dependencies

The test runs continuously and updates every 5 minutes, providing a real-time view of network connectivity.
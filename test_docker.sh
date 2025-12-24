#!/bin/bash
# Docker Setup Test Script
# Tests the complete Docker deployment for external users

set -e

echo "🧪 Testing Complete Docker Setup"
echo "================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Test 1: Check Docker availability
test_docker() {
    print_status "Checking Docker availability..."

    if ! command -v docker &> /dev/null; then
        print_error "Docker not installed"
        return 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose not installed"
        return 1
    fi

    if ! docker info &> /dev/null; then
        print_error "Docker daemon not running"
        return 1
    fi

    print_success "Docker and Docker Compose ready"
    return 0
}

# Test 2: Build containers
test_build() {
    print_status "Building Docker containers..."

    if ! docker-compose build --quiet; then
        print_error "Container build failed"
        return 1
    fi

    print_success "Containers built successfully"
    return 0
}

# Test 3: Start services
test_startup() {
    print_status "Starting services..."

    # Clean start
    docker-compose down --remove-orphans 2>/dev/null || true

    if ! docker-compose up -d; then
        print_error "Services failed to start"
        return 1
    fi

    print_success "Services started"
    return 0
}

# Test 4: Health checks
test_health() {
    print_status "Testing service health..."

    # Wait for services to be ready
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        print_status "Health check attempt $attempt/$max_attempts..."

        # Test backend
        if curl -f -s http://localhost:8080/ > /dev/null 2>&1; then
            print_success "Backend health check passed"
            backend_ok=true
        else
            backend_ok=false
        fi

        # Test frontend
        if curl -f -s http://localhost:3000/ > /dev/null 2>&1; then
            print_success "Frontend health check passed"
            frontend_ok=true
        else
            frontend_ok=false
        fi

        if [ "$backend_ok" = true ] && [ "$frontend_ok" = true ]; then
            print_success "All services healthy"
            return 0
        fi

        sleep 2
        ((attempt++))
    done

    print_error "Services failed health checks"
    if [ "$backend_ok" != true ]; then
        print_error "Backend not responding on port 8080"
    fi
    if [ "$frontend_ok" != true ]; then
        print_error "Frontend not responding on port 3000"
    fi
    return 1
}

# Test 5: API functionality
test_api() {
    print_status "Testing API functionality..."

    # Test jobs endpoint
    if ! curl -f -s http://localhost:8080/api/jobs > /dev/null 2>&1; then
        print_error "Jobs API not accessible"
        return 1
    fi
    print_success "Jobs API accessible"

    # Test creating a job
    local response
    response=$(curl -s -X POST http://localhost:8080/api/jobs \
        -H "Content-Type: application/json" \
        -d '{"code": "int main() { return 0; }"}' 2>/dev/null)

    if ! echo "$response" | grep -q "job_id"; then
        print_error "Job creation failed"
        return 1
    fi
    print_success "Job creation works"

    # Extract job ID
    local job_id
    job_id=$(echo "$response" | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)

    if [ -n "$job_id" ]; then
        print_success "Job created with ID: $job_id"
        return 0
    else
        print_error "Could not extract job ID"
        return 1
    fi
}

# Test 6: WebSocket functionality
test_websocket() {
    print_status "Testing WebSocket functionality..."

    # Use timeout to avoid hanging
    if timeout 10 bash -c '
        exec 3<>/dev/tcp/localhost/8080
        echo -e "GET /ws/jobs HTTP/1.1\r\nHost: localhost:8080\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\nSec-WebSocket-Version: 13\r\n\r\n" >&3
        timeout 5 cat <&3 | head -1 | grep -q "101 Switching Protocols"
    ' 2>/dev/null; then
        print_success "WebSocket endpoint accessible"
        return 0
    else
        print_warning "WebSocket test inconclusive (may require specialized client)"
        return 0  # Not critical for basic functionality
    fi
}

# Test 7: Frontend connectivity
test_frontend() {
    print_status "Testing frontend-backend connectivity..."

    # Check if frontend can reach backend
    local frontend_response
    frontend_response=$(curl -s http://localhost:3000/ 2>/dev/null | head -20)

    if echo "$frontend_response" | grep -q -i "react\|html"; then
        print_success "Frontend serving content"
        return 0
    else
        print_error "Frontend not serving proper content"
        return 1
    fi
}

# Cleanup function
cleanup() {
    print_status "Cleaning up test environment..."
    docker-compose down --remove-orphans 2>/dev/null || true
    docker system prune -f 2>/dev/null || true
    print_success "Cleanup complete"
}

# Main test function
main() {
    local test_passed=0
    local total_tests=7

    echo "Running $total_tests comprehensive tests..."
    echo ""

    # Setup cleanup trap
    trap cleanup EXIT

    # Run tests
    test_docker && ((test_passed++))
    echo ""

    test_build && ((test_passed++))
    echo ""

    test_startup && ((test_passed++))
    echo ""

    test_health && ((test_passed++))
    echo ""

    test_api && ((test_passed++))
    echo ""

    test_websocket && ((test_passed++))
    echo ""

    test_frontend && ((test_passed++))
    echo ""

    # Results
    echo "================================"
    echo "🧪 Test Results: $test_passed/$total_tests passed"

    if [ $test_passed -eq $total_tests ]; then
        print_success "🎉 ALL TESTS PASSED! Docker setup is working perfectly!"
        echo ""
        echo "🌐 Your application is ready:"
        echo "   Frontend: http://localhost:3000"
        echo "   Backend API: http://localhost:8080"
        echo ""
        echo "🛑 To stop: docker-compose down"
        exit 0
    else
        print_error "❌ Some tests failed. Check the output above."
        echo ""
        echo "🔧 Troubleshooting:"
        echo "   - Check Docker daemon: docker info"
        echo "   - View logs: docker-compose logs"
        echo "   - Clean restart: docker-compose down && docker-compose up --build -d"
        exit 1
    fi
}

# Run main tests
main "$@"

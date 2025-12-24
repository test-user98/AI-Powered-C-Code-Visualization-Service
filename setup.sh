#!/bin/bash
# C Code Analyzer - Complete Setup Script
# This script sets up the entire application with all dependencies

set -e

echo "🚀 C Code Analyzer - Complete Setup"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is available
check_docker() {
    if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        print_success "Docker and Docker Compose found"
        return 0
    else
        print_warning "Docker or Docker Compose not found. Using local setup instead."
        return 1
    fi
}

# Setup using Docker
setup_docker() {
    print_status "Setting up with Docker..."

    # Build and start containers
    print_status "Building Docker containers..."
    docker-compose build

    print_status "Starting services..."
    docker-compose up -d

    # Wait for services to be ready
    print_status "Waiting for services to start..."
    sleep 10

    # Test services
    print_status "Testing backend..."
    if curl -f http://localhost:8080/ &>/dev/null; then
        print_success "Backend is running at http://localhost:8080"
    else
        print_error "Backend failed to start"
        exit 1
    fi

    print_status "Testing frontend..."
    if curl -f http://localhost:3000/ &>/dev/null; then
        print_success "Frontend is running at http://localhost:3000"
    else
        print_error "Frontend failed to start"
        exit 1
    fi

    print_success "🎉 Docker setup complete!"
    echo ""
    echo "✅ Includes ast-grep for advanced C code analysis"
    echo ""
    echo "🌐 Access your application:"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend API: http://localhost:8080"
    echo ""
    echo "🛑 To stop: docker-compose down"
    echo "📊 To view logs: docker-compose logs -f"
}

# Setup locally
setup_local() {
    print_status "Setting up locally..."

    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not found"
        exit 1
    fi

    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is required but not found"
        exit 1
    fi

    # Setup backend
    print_status "Setting up backend..."
    cd "$(dirname "$0")"

    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Install Python dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt

    # Setup frontend
    print_status "Setting up frontend..."
    cd frontend

    # Install Node.js dependencies
    print_status "Installing Node.js dependencies..."
    npm install

    # Go back to root
    cd ..

    print_success "Local setup complete!"
    echo ""
    echo "🚀 To start the application:"
    echo "   Backend: python app/main.py"
    echo "   Frontend: cd frontend && npm start"
    echo ""
    echo "🌐 Then visit: http://localhost:3000"
}

# Main setup logic
main() {
    print_status "Checking system requirements..."

    if check_docker; then
        echo ""
        echo "Choose setup method:"
        echo "1) Docker (recommended for external users)"
        echo "2) Local development setup"
        read -p "Enter choice (1 or 2): " choice

        case $choice in
            1)
                setup_docker
                ;;
            2)
                setup_local
                ;;
            *)
                print_error "Invalid choice. Using Docker setup."
                setup_docker
                ;;
        esac
    else
        print_warning "Docker not available. Using local setup."
        setup_local
    fi

    echo ""
    print_success "🎉 Setup complete! Happy coding! 🚀"
}

# Run main function
main "$@"

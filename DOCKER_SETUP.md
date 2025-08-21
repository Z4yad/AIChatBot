# Docker Installation Guide for macOS

## Option 1: Docker Desktop (Recommended for Development)

### Install via Homebrew (Easiest)

1. **Install Homebrew** (if not already installed):
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. **Install Docker Desktop**:
```bash
brew install --cask docker
```

3. **Start Docker Desktop**:
   - Open Docker Desktop from Applications
   - Follow the setup wizard
   - Accept the license agreement
   - Docker will start automatically

### Manual Download Alternative

1. **Download Docker Desktop**:
   - Go to: https://www.docker.com/products/docker-desktop/
   - Click "Download for Mac"
   - Choose your chip type:
     - **Apple Silicon (M1/M2/M3)**: Mac with Apple chip
     - **Intel**: Mac with Intel chip

2. **Install**:
   - Open the downloaded `.dmg` file
   - Drag Docker to Applications folder
   - Launch Docker from Applications

### Verify Installation

Once Docker Desktop is running:

```bash
# Check Docker version
docker --version

# Check Docker Compose version
docker-compose --version

# Test Docker with hello-world
docker run hello-world
```

## Option 2: Command Line Only (Advanced Users)

If you prefer command-line only without Docker Desktop GUI:

```bash
# Install Docker CLI and Docker Compose
brew install docker docker-compose

# Install and start Colima (Docker runtime)
brew install colima
colima start
```

## Configuration for AI Support Chatbot

### System Requirements

- **RAM**: 8GB minimum (16GB recommended for local LLM)
- **Storage**: 10GB free space
- **CPU**: Multi-core processor recommended

### Docker Desktop Settings

1. **Open Docker Desktop Preferences**
2. **Resources > Advanced**:
   - **CPUs**: Allocate at least 4 CPUs
   - **Memory**: Allocate at least 6GB RAM (8GB+ for local LLM)
   - **Disk**: Ensure sufficient space

3. **Apply & Restart**

## Troubleshooting

### Common Issues

1. **"Docker daemon not running"**:
   ```bash
   # Start Docker Desktop application
   open -a Docker
   
   # Or if using Colima:
   colima start
   ```

2. **Permission denied**:
   ```bash
   # Add your user to docker group (may require restart)
   sudo dscl . append /Groups/docker GroupMembership $(whoami)
   ```

3. **Out of disk space**:
   ```bash
   # Clean up unused Docker data
   docker system prune -a
   ```

4. **Slow performance**:
   - Increase RAM allocation in Docker Desktop
   - Enable "Use Rosetta for x86/amd64 emulation" (Apple Silicon only)

### Performance Tips

1. **File sharing**: Only share necessary directories
2. **Resource limits**: Set appropriate CPU/memory limits
3. **Background apps**: Close unnecessary applications

## Next Steps

After Docker is installed and running:

1. **Verify Docker works**:
   ```bash
   docker run hello-world
   ```

2. **Run the AI Support Chatbot setup**:
   ```bash
   cd ai-support-chatbot
   ./setup.sh
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/docs

## Alternative: Development Without Docker

If you prefer not to use Docker for development, I can create a native setup script that runs the services directly on your machine using Python virtual environments and Node.js. This would be faster for development but Docker is recommended for production deployment.

Let me know if you'd like the native development setup instead!

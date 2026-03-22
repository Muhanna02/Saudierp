#!/bin/bash
# =============================================================
# Saudi ERP - Full Server Deployment Script
# Run this as root on your server: bash deploy.sh
# =============================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()    { echo -e "${GREEN}[INFO]${NC} $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

echo ""
echo "======================================================"
echo "  Saudi ERP - Automated Deployment"
echo "  نظام إدارة موارد المؤسسات السعودية"
echo "======================================================"
echo ""

# ── 1. Check root ───────────────────────────────────────────
if [ "$EUID" -ne 0 ]; then
  error "Please run as root: sudo bash deploy.sh"
fi

SERVER_IP=$(curl -s --max-time 5 https://api.ipify.org 2>/dev/null || hostname -I | awk '{print $1}')
info "Server IP detected: $SERVER_IP"

# ── 2. Install dependencies ──────────────────────────────────
info "Updating system and installing dependencies..."
apt-get update -qq
apt-get install -y -qq \
  apt-transport-https \
  ca-certificates \
  curl \
  gnupg \
  lsb-release \
  git \
  unzip 2>/dev/null

# ── 3. Install Docker ────────────────────────────────────────
if ! command -v docker &>/dev/null; then
  info "Installing Docker..."
  curl -fsSL https://get.docker.com | bash
  systemctl enable docker
  systemctl start docker
  info "Docker installed: $(docker --version)"
else
  info "Docker already installed: $(docker --version)"
fi

# ── 4. Install Docker Compose ────────────────────────────────
if ! command -v docker-compose &>/dev/null && ! docker compose version &>/dev/null 2>&1; then
  info "Installing Docker Compose..."
  COMPOSE_VER=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep '"tag_name"' | cut -d'"' -f4)
  curl -SL "https://github.com/docker/compose/releases/download/${COMPOSE_VER}/docker-compose-linux-x86_64" \
    -o /usr/local/bin/docker-compose
  chmod +x /usr/local/bin/docker-compose
  info "Docker Compose installed: $(docker-compose --version)"
else
  info "Docker Compose already available"
fi

# ── 5. Set up project directory ──────────────────────────────
PROJECT_DIR="/opt/saudi-erp"
info "Setting up project at $PROJECT_DIR ..."

if [ -d "$PROJECT_DIR" ]; then
  warn "Directory $PROJECT_DIR already exists. Pulling latest changes..."
  cd "$PROJECT_DIR"
  git pull origin main 2>/dev/null || git pull 2>/dev/null || true
else
  # Clone from GitHub if available, otherwise copy from current location
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  if [ "$SCRIPT_DIR" != "$PROJECT_DIR" ]; then
    info "Copying project files to $PROJECT_DIR ..."
    mkdir -p "$PROJECT_DIR"
    cp -r "$SCRIPT_DIR/." "$PROJECT_DIR/"
  fi
  cd "$PROJECT_DIR"
fi

# ── 6. Configure environment ─────────────────────────────────
info "Configuring environment..."
if [ ! -f "$PROJECT_DIR/.env" ]; then
  cat > "$PROJECT_DIR/.env" << EOF
DB_PASSWORD=Saudi@ERP2024
ADMIN_PASSWORD=admin123
EOF
  info "Created .env file"
fi

# ── 7. Fix odoo.conf (replace env var placeholders) ──────────
info "Fixing odoo.conf..."
cat > "$PROJECT_DIR/docker/odoo.conf" << 'ODOOEOF'
[options]
addons_path = /mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons
admin_passwd = admin123
db_host = db
db_port = 5432
db_user = odoo
db_password = Saudi@ERP2024
db_name = False
dbfilter = ^%h$
list_db = True
xmlrpc_port = 8069
longpolling_port = 8072
workers = 2
max_cron_threads = 1
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_request = 8192
limit_time_cpu = 600
limit_time_real = 1200
log_level = info
log_handler = :INFO
proxy_mode = True
without_demo = True
ODOOEOF

# ── 8. Create log directory for odoo ────────────────────────
mkdir -p /var/log/odoo

# ── 9. Update nginx.conf with server IP ──────────────────────
info "Configuring Nginx for IP: $SERVER_IP ..."
cat > "$PROJECT_DIR/docker/nginx.conf" << NGINXEOF
upstream odoo {
    server odoo:8069;
}

upstream odoo_chat {
    server odoo:8072;
}

server {
    listen 80;
    server_name $SERVER_IP _;

    access_log /var/log/nginx/odoo.access.log;
    error_log /var/log/nginx/odoo.error.log;

    proxy_read_timeout 720s;
    proxy_connect_timeout 720s;
    proxy_send_timeout 720s;
    client_max_body_size 200m;

    location /longpolling {
        proxy_pass http://odoo_chat;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header X-Forwarded-Host \$host;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    location / {
        proxy_pass http://odoo;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "keep-alive";
        proxy_set_header X-Forwarded-Host \$host;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
    gzip_min_length 1000;
}
NGINXEOF

# ── 10. Stop any existing containers ─────────────────────────
info "Stopping existing containers (if any)..."
cd "$PROJECT_DIR"
docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true

# ── 11. Pull images and start services ───────────────────────
info "Pulling Docker images (this may take a few minutes)..."
docker-compose pull 2>/dev/null || docker compose pull 2>/dev/null

info "Starting services..."
docker-compose up -d 2>/dev/null || docker compose up -d 2>/dev/null

# ── 12. Wait for database ─────────────────────────────────────
info "Waiting for PostgreSQL to be ready..."
RETRIES=30
until docker exec saudi_erp_db pg_isready -U odoo -q 2>/dev/null; do
  RETRIES=$((RETRIES-1))
  if [ $RETRIES -le 0 ]; then
    error "Database did not start in time. Check: docker logs saudi_erp_db"
  fi
  sleep 3
done
info "PostgreSQL is ready!"

# ── 13. Wait for Odoo ────────────────────────────────────────
info "Waiting for Odoo to start (this may take 2-3 minutes)..."
sleep 20
RETRIES=40
until curl -s --max-time 3 http://localhost:8069/web/health 2>/dev/null | grep -q "ok\|jsonrpc\|result" 2>/dev/null; do
  RETRIES=$((RETRIES-1))
  if [ $RETRIES -le 0 ]; then
    warn "Odoo health check timed out, but it may still be starting..."
    break
  fi
  sleep 5
done

# ── 14. Initialize Saudi ERP database ────────────────────────
info "Initializing Saudi ERP modules (this takes 3-5 minutes)..."
docker exec saudi_erp_app odoo \
  --config /etc/odoo/odoo.conf \
  --database saudi_erp \
  --init saudi_erp_base,saudi_erp_accounting,saudi_erp_hr,saudi_erp_pos,saudi_erp_dashboard,saudi_erp_portal \
  --stop-after-init \
  --without-demo all \
  --log-level warn 2>&1 | tail -20

info "Database initialized!"

# ── 15. Restart Odoo to apply modules ────────────────────────
info "Restarting Odoo service..."
docker-compose restart odoo 2>/dev/null || docker compose restart odoo 2>/dev/null
sleep 10

# ── 16. Open firewall ports ───────────────────────────────────
info "Opening firewall ports..."
if command -v ufw &>/dev/null; then
  ufw allow 80/tcp 2>/dev/null || true
  ufw allow 443/tcp 2>/dev/null || true
  ufw allow 8069/tcp 2>/dev/null || true
  ufw allow 22/tcp 2>/dev/null || true
fi
if command -v firewall-cmd &>/dev/null; then
  firewall-cmd --permanent --add-port=80/tcp 2>/dev/null || true
  firewall-cmd --permanent --add-port=8069/tcp 2>/dev/null || true
  firewall-cmd --reload 2>/dev/null || true
fi

# ── 17. Final status ─────────────────────────────────────────
echo ""
echo "======================================================"
echo -e "${GREEN}✅ Saudi ERP Deployment Complete!${NC}"
echo "======================================================"
echo ""
echo "🌐 Access URLs:"
echo "   Main URL:  http://$SERVER_IP"
echo "   Alt URL:   http://$SERVER_IP:8069"
echo ""
echo "🔐 Login Credentials:"
echo "   Username:  admin"
echo "   Password:  admin"
echo ""
echo "📦 Container Status:"
docker-compose ps 2>/dev/null || docker compose ps 2>/dev/null
echo ""
echo "📋 Modules installed:"
echo "   - saudi_erp_base      (Core + SaaS)"
echo "   - saudi_erp_accounting (ZATCA + VAT)"
echo "   - saudi_erp_hr        (GOSI + EOS + Iqama)"
echo "   - saudi_erp_pos       (Mada + STC Pay)"
echo "   - saudi_erp_dashboard (Admin Dashboard)"
echo "   - saudi_erp_portal    (Registration Portal)"
echo ""
echo "🛠 Management Commands:"
echo "   Logs:     docker logs -f saudi_erp_app"
echo "   Restart:  cd $PROJECT_DIR && docker-compose restart"
echo "   Stop:     cd $PROJECT_DIR && docker-compose down"
echo "   Start:    cd $PROJECT_DIR && docker-compose up -d"
echo "======================================================"

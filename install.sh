#!/bin/bash
# Saudi ERP Quick Install Script

set -e

echo "======================================"
echo "  Saudi ERP - Quick Setup"
echo "  نظام إدارة موارد المؤسسات السعودية"
echo "======================================"

# Copy .env file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file"
fi

# Start services
echo "Starting Docker services..."
docker-compose up -d

echo ""
echo "Waiting for services to start..."
sleep 15

# Init database
echo "Initializing Saudi ERP database..."
docker exec saudi_erp_app odoo \
    --config /etc/odoo/odoo.conf \
    --database saudi_erp \
    --init saudi_erp_base,saudi_erp_accounting,saudi_erp_hr,saudi_erp_pos,saudi_erp_dashboard,saudi_erp_portal \
    --stop-after-init \
    --without-demo all

echo ""
echo "======================================"
echo "✅ Saudi ERP is ready!"
echo ""
echo "🌐 Access: http://localhost:8069"
echo "👤 Admin: admin"
echo "🔑 Password: admin"
echo ""
echo "📋 Modules installed:"
echo "   - Saudi Base (Core + SaaS)"
echo "   - Saudi Accounting (ZATCA + VAT)"
echo "   - Saudi HR (GOSI + EOS + Iqama)"
echo "   - Saudi POS (Mada + STC Pay)"
echo "   - Custom Admin Dashboard"
echo "   - Registration Portal"
echo "======================================"

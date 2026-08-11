#!/usr/bin/env bash
# =============================================================================
# NaijaBay Django Backend Build Script
# Suitable for Render, Railway, Fly.io, and similar platforms
# =============================================================================

set -o errexit
set -o pipefail
set -o nounset

echo "🚀 Starting NaijaBay backend build..."

# -----------------------------------------------------------------------------
# 1. Upgrade packaging tools and install dependencies
# -----------------------------------------------------------------------------
echo "📦 Installing Python dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install gunicorn

# -----------------------------------------------------------------------------
# 2. Run Django checks
# -----------------------------------------------------------------------------
echo "🔍 Running Django system checks..."
python manage.py check

# -----------------------------------------------------------------------------
# 3. Apply database migrations
# -----------------------------------------------------------------------------
echo "🗄️  Applying database migrations..."
python manage.py migrate --noinput

# -----------------------------------------------------------------------------
# 4. Collect static files
# -----------------------------------------------------------------------------
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

# -----------------------------------------------------------------------------
# 5. Optional translations
# -----------------------------------------------------------------------------
if [ -d "locale" ]; then
    echo "🌐 Compiling translation messages..."
    python manage.py compilemessages || true
fi

echo "✅ NaijaBay backend build completed successfully!"
#!/bin/bash
# ---------------------------------------------------------------------------------
#  VIP REACTION & AI CHATBOT - Task Runner & DevOps Manager
#  Copyright (c) 2026 Amrit Raj (@Villanns). All Rights Reserved.
#  Instagram: @ex_amrit | Snapchat: @ex_amrit
# ---------------------------------------------------------------------------------

set -e

ACTION="${1:-help}"

case "$ACTION" in
    test)
        echo "🧪 Running Unit Test Suite (Tests & Core Architecture)..."
        python3 -m unittest discover tests
        ;;
    clean)
        echo "🧹 Cleaning temporary cache files, byte-compiled bytecode and dumps..."
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find . -type f -name "*.py[cod]" -delete 2>/dev/null || true
        find . -type f -name "*.session-journal" -delete 2>/dev/null || true
        rm -rf cache/* .cache/* 2>/dev/null || true
        touch cache/.gitkeep 2>/dev/null || true
        echo "✅ Cleanup complete!"
        ;;
    check)
        echo "🔍 Running Pre-Flight Environment & Diagnostic Validation..."
        python3 -c "import config; from nexichat.core.diagnostics import validate_environment; ok, err = validate_environment(config); print('✅ Environment and credentials are 100% valid!' if ok else f'❌ Error:\n{err}')"
        ;;
    start)
        echo "🚀 Starting VIP Reaction Bot via start script..."
        bash start
        ;;
    status)
        echo "📊 Checking active VIP Reaction processes..."
        pgrep -fl "python3 -m nexichat" || echo "Bot process is currently not running."
        ;;
    help|*)
        echo "╔════════════════════════════════════════════════════════════════╗"
        echo "║         VIP REACTION & AI CHATBOT - MANAGEMENT CLI            ║"
        echo "║        Creator: Amrit Raj (@Villanns | IG: @ex_amrit)          ║"
        echo "╚════════════════════════════════════════════════════════════════╝"
        echo ""
        echo "Usage: bash manage.sh [command]"
        echo ""
        echo "Available Commands:"
        echo "  test    - Run all unit tests and verify 100% passing status"
        echo "  clean   - Flush all temporary media cache and __pycache__ files"
        echo "  check   - Perform diagnostic environment & token pre-flight check"
        echo "  start   - Launch the bot daemon in foreground or background"
        echo "  status  - Check PID of running bot process"
        echo ""
        ;;
esac

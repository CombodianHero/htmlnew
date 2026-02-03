#!/bin/bash

# 🔍 DEPLOYMENT PACKAGE VERIFICATION SCRIPT
# Run this to verify all files are correct before deployment

echo "======================================================================"
echo "  🔍 VERIFYING DEPLOYMENT PACKAGE"
echo "======================================================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

# Function to check file
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅${NC} $1 exists ($(ls -lh $1 | awk '{print $5}'))"
    else
        echo -e "${RED}❌${NC} $1 NOT FOUND!"
        ((ERRORS++))
    fi
}

# Function to check content
check_content() {
    if grep -q "$2" "$1" 2>/dev/null; then
        echo -e "   ${GREEN}✅${NC} Contains: $2"
    else
        echo -e "   ${RED}❌${NC} Missing: $2"
        ((ERRORS++))
    fi
}

echo "📋 Checking REQUIRED files for deployment..."
echo ""

# Check core files
echo "1️⃣ telegram_bot.py"
check_file "telegram_bot.py"
if [ -f "telegram_bot.py" ]; then
    # Check for smart grouping functions
    check_content "telegram_bot.py" "def normalize_title"
    check_content "telegram_bot.py" "def calculate_similarity"
    check_content "telegram_bot.py" "def find_matching_group"
    
    # Check entry point is correct
    if tail -5 telegram_bot.py | grep -q "if __name__ == \"__main__\":"; then
        echo -e "   ${GREEN}✅${NC} Entry point: main() (correct)"
    else
        echo -e "   ${RED}❌${NC} Entry point: incorrect"
        ((ERRORS++))
    fi
    
    # Check NO port binding
    if ! grep -q "app.run" telegram_bot.py; then
        echo -e "   ${GREEN}✅${NC} No port binding (correct)"
    else
        echo -e "   ${RED}❌${NC} WARNING: Contains app.run() - port binding issue!"
        ((ERRORS++))
    fi
    
    # Check file size
    LINES=$(wc -l < telegram_bot.py)
    if [ $LINES -gt 1000 ]; then
        echo -e "   ${GREEN}✅${NC} File size: $LINES lines (includes smart grouping)"
    else
        echo -e "   ${YELLOW}⚠️${NC}  File size: $LINES lines (might be missing smart grouping)"
        ((WARNINGS++))
    fi
fi
echo ""

echo "2️⃣ requirements.txt"
check_file "requirements.txt"
if [ -f "requirements.txt" ]; then
    check_content "requirements.txt" "python-telegram-bot"
fi
echo ""

echo "3️⃣ render.yaml"
check_file "render.yaml"
if [ -f "render.yaml" ]; then
    check_content "render.yaml" "type: worker"
    if grep -q "type: web" render.yaml 2>/dev/null; then
        echo -e "   ${RED}❌${NC} ERROR: Service type is 'web' - should be 'worker'!"
        ((ERRORS++))
    fi
fi
echo ""

echo "======================================================================"
echo "📚 Checking DOCUMENTATION files (optional but recommended)..."
echo "======================================================================"
echo ""

check_file "README.md"
check_file "DEPLOYMENT_GUIDE.md"
check_file "SMART_GROUPING_GUIDE.md"
check_file "SMART_GROUPING_SUMMARY.md"
check_file "demo_smart_grouping.py"
check_file "FILE_CHECKLIST.md"
echo ""

echo "======================================================================"
echo "  📊 VERIFICATION SUMMARY"
echo "======================================================================"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ PERFECT! All checks passed!${NC}"
    echo ""
    echo "🚀 Your package is ready to deploy!"
    echo ""
    echo "Next steps:"
    echo "  1. Push these files to GitHub"
    echo "  2. Create Worker service on Render.com"
    echo "  3. Set BOT_TOKEN environment variable"
    echo "  4. Deploy!"
    echo ""
    echo "📖 Read DEPLOYMENT_GUIDE.md for detailed instructions"
elif [ $ERRORS -eq 0 ] && [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  $WARNINGS warning(s) found${NC}"
    echo ""
    echo "You can still deploy, but review the warnings above."
else
    echo -e "${RED}❌ $ERRORS error(s) found${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠️  $WARNINGS warning(s) found${NC}"
    fi
    echo ""
    echo "Please fix the errors above before deploying!"
fi

echo ""
echo "======================================================================"

# Exit code
if [ $ERRORS -eq 0 ]; then
    exit 0
else
    exit 1
fi

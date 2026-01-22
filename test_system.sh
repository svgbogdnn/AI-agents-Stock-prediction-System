#!/bin/bash
# Quick system test before Git submission

echo "🧪 Testing Stock Prediction System..."
echo "======================================"
echo

# Test 1: Check Python version
echo "1️⃣  Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+' | head -1)
if (( $(echo "$python_version >= 3.11" | bc -l) )); then
    echo "   ✅ Python $python_version (OK)"
else
    echo "   ❌ Python $python_version (Need 3.11+)"
    exit 1
fi
echo

# Test 2: Check .env file
echo "2️⃣  Checking .env configuration..."
if [ -f .env ]; then
    echo "   ✅ .env file exists"
    if grep -q "GOOGLE_API_KEY" .env && grep -q "POLYGON_API_KEY" .env; then
        echo "   ✅ Required API keys present"
    else
        echo "   ⚠️  Some API keys missing"
    fi
else
    echo "   ⚠️  .env file not found (copy from .env.example)"
fi
echo

# Test 3: Check dependencies
echo "3️⃣  Checking Python dependencies..."
source venv/bin/activate 2>/dev/null
if python -c "import google.genai, pandas, numpy" 2>/dev/null; then
    echo "   ✅ Core dependencies installed"
else
    echo "   ❌ Dependencies missing (run: pip install -r requirements.txt)"
    exit 1
fi
echo

# Test 4: Check agents
echo "4️⃣  Checking agent files..."
agent_count=$(ls -1 agents/*_server.py 2>/dev/null | wc -l | tr -d ' ')
if [ "$agent_count" -ge 5 ]; then
    echo "   ✅ Found $agent_count agent servers"
else
    echo "   ❌ Missing agent files"
    exit 1
fi
echo

# Test 5: Check frontend
echo "5️⃣  Checking frontend..."
if [ -d "frontend/node_modules" ]; then
    echo "   ✅ Frontend dependencies installed"
elif [ -f "frontend/package.json" ]; then
    echo "   ⚠️  Frontend dependencies not installed (run: cd frontend && npm install)"
else
    echo "   ❌ Frontend not found"
fi
echo

# Test 6: Check notebooks
echo "6️⃣  Checking Jupyter notebooks..."
if [ -f "notebooks/kaggle_submission_complete.ipynb" ]; then
    echo "   ✅ Kaggle submission notebook present"
else
    echo "   ❌ Submission notebook missing"
    exit 1
fi
echo

# Test 7: Check documentation
echo "7️⃣  Checking documentation..."
if [ -f "README.md" ] && [ -s "README.md" ]; then
    echo "   ✅ README.md exists and has content"
else
    echo "   ❌ README.md missing or empty"
    exit 1
fi
echo

# Summary
echo "======================================"
echo "✅ System test completed successfully!"
echo
echo "Next steps:"
echo "  1. Test full system: bash scripts/start_full_system.sh"
echo "  2. Initialize git: git init"
echo "  3. Commit: git add . && git commit -m 'Initial commit'"
echo "  4. Push to GitHub"
echo "  5. Submit to Kaggle"
echo


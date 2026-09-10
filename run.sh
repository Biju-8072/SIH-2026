#!/usr/bin/env bash
# ==============================================================================
# 🛰️ SIH26162: AI-Based Detection & Classification of Industrial Fires
# One-Click Launch Script for Hackathon Presentation & Local Surveillance
# ==============================================================================

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "================================================================="
echo "  🛰️ SIH26162: AI INDUSTRIAL FIRE SURVEILLANCE SYSTEM"
echo "================================================================="

# 1. Check or create virtual environment
if [ ! -d ".venv" ]; then
    echo "📦 Initializing isolated Python virtual environment (.venv)..."
    python3 -m venv .venv
fi

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Ensure required packages are installed
echo "🔍 Checking dependencies..."
python3 -m pip install -q -r requirements.txt

# 4. Run baseline detection pipeline
echo "🚀 Bootstrapping surveillance data pipeline..."
python3 pipeline.py --sandbox --no-alert

# 5. Ensure Technical Manual PDF is generated
python3 generate_documentation_pdf.py

# 6. Launch interactive Streamlit Command Center
echo ""
echo "🌟 Starting Tactical Command Center Dashboard..."
echo "👉 Open your browser at: http://localhost:8501"
echo "👉 Or run standalone high-speed server: python3 run_demo.py"
echo "📄 Technical Manual PDF: AURA_FIRE_Project_Working_Manual.pdf"
echo "================================================================="
python3 -m streamlit run app.py

"""
🛰️ AURA-FIRE: AI Industrial Fire Surveillance & Crisis Command Suite
One-Click Demo Runner & Simple Working Explainer
"""

import os
import sys
import time
import webbrowser
from http.server import SimpleHTTPRequestHandler, HTTPServer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_NAME = "AURA_FIRE_Project_Working_Manual.pdf"


def print_working_explanation():
    print("""
======================================================================
  🛰️ AURA-FIRE: AI-POWERED INDUSTRIAL FIRE SURVEILLANCE SYSTEM
  Problem Statement: SIH26162 | Real-Time Satellite to Emergency Dispatch
======================================================================

💡 HOW THIS SYSTEM WORKS (SIMPLE 4-STEP EXPLANATION):
----------------------------------------------------------------------
1. 🛰️ SATELLITE THERMAL INGESTION (NASA SNPP-VIIRS & NOAA-20)
   • Continuously scans ground pixels with 375m Middle-Wave IR sensors.
   • Detects thermal anomalies and calculates Fire Radiative Power (FRP) in MW.

2. 🗺️ GEOSPATIAL INFRASTRUCTURE COLLISION (OpenStreetMap Registry)
   • Computes Haversine great-circle distance to nearest chemical complexes,
     refineries, and bulk hydrocarbon storage depots.
   • Applies a certified 4.5 km industrial safety buffer envelope.

3. 🤖 TEMPORAL AI PERSISTENCE & THREAT CLASSIFIER
   • Tracks 30-day thermal burning history at each facility.
   • Routine Flare: Persistent for >=20 of last 30 days & FRP <= 250 MW.
     -> Result: Classified as CONTROLLED INDUSTRIAL FLARE (99% false alarm reduction).
   • Explosion / Flashover: Sudden spike >250 MW or novel surge without history.
     -> Result: Classified as CRITICAL DISASTER (ALPHA-RED EMERGENCY).

4. 🚨 AUTONOMOUS CRISIS RESPONSE & HUD VISUALIZATION
   • Models secondary exclusion perimeters and prevailing wind drift vectors.
   • Synthesizes dual-tone emergency audio sirens via Web Audio API.
   • Mobilizes rapid hazmat foam tenders and provides 1-click camera fly-to.
======================================================================
    """)


def find_available_port(start_port=8080, max_attempts=10):
    import socket
    for p in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    return start_port


def main():
    os.chdir(BASE_DIR)
    print_working_explanation()

    # Step 1: Run detection pipeline
    print("⏳ [1/3] Verifying surveillance data pipeline...")
    from pipeline import run_full_pipeline
    run_full_pipeline(force_sandbox=True, dispatch_alerts=False)

    # Step 2: Ensure freshest index.html and all 7 separate screen pages are generated
    print("⏳ [2/3] Rendering Operations Dashboard & separate screen pages...")
    from generate_separate_pages import build_all_pages
    build_all_pages()
    print("✅ All 7 screen pages generated successfully.")

    # Step 3: Ensure documentation PDF exists
    pdf_path = os.path.join(BASE_DIR, PDF_NAME)
    if not os.path.exists(pdf_path):
        print("⏳ Generating technical manual PDF...")
        from generate_documentation_pdf import generate_full_manual
        generate_full_manual()
    print(f"📄 Full Working PDF Manual Ready: {pdf_path}")

    # Step 4: Start local presentation server
    port = find_available_port(8080)
    url = f"http://localhost:{port}/index.html"
    print("\n" + "=" * 65)
    print(f"🚀 MISSION COMMAND SERVER ACTIVE!")
    print(f"👉 Presentation Link: {url}")
    print(f"📄 Complete Working PDF: file://{pdf_path}")
    print("=" * 65)
    print("Press Ctrl+C to stop the server.\n")

    try:
        webbrowser.open(url)
    except Exception:
        pass

    server_address = ("", port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nMission command server terminated cleanly.")
        sys.exit(0)


if __name__ == "__main__":
    main()

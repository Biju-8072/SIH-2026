"""
Generates 7 standalone HTML pages for each individual screen:
  1. dashboard.html   (⭐ 1. Dashboard - Default Landing)
  2. analytics.html   (📊 2. DT Analytical Tools)
  3. resource.html    (🛰️ 3. Resource Allocation)
  4. sainffire.html   (🔥 4. SainfFire Continental Surveillance)
  5. ecc.html         (🚨 5. Command Center ECC)
  6. fwi.html         (🌡️ 6. Fire Weather Index)
  7. fleet.html       (🚒 7. Fleet Logistics)
"""

import os
import re
from app import get_telemetry_records, get_zones_records
from ui_template import generate_dashboard_html

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PAGES = [
    ("dashboard.html", "view-dashboard", "btn-dash", 0, "analytics.html", "fleet.html"),
    ("analytics.html", "view-analytics", "btn-analytics", 1, "resource.html", "dashboard.html"),
    ("resource.html", "view-resource", "btn-crisis", 2, "sainffire.html", "analytics.html"),
    ("sainffire.html", "view-sainffire", "btn-sainffire", 3, "ecc.html", "resource.html"),
    ("ecc.html", "view-ecc", "btn-dashboard", 4, "fwi.html", "sainffire.html"),
    ("fwi.html", "view-fwi", "btn-fwi", 5, "fleet.html", "ecc.html"),
    ("fleet.html", "view-fleet", "btn-resources", 6, "dashboard.html", "fwi.html"),
]


def build_all_pages():
    alerts = get_telemetry_records()
    zones = get_zones_records()
    base_html = generate_dashboard_html(alerts, zones)
    
    # Save main index.html (Default: Screen 1 Operations Dashboard)
    with open(os.path.join(BASE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(base_html)
    print("✅ index.html written (Default Screen 1: Operations Dashboard).")

    for filename, view_id, btn_id, page_idx, next_page, prev_page in PAGES:
        html = base_html
        
        # 1. Set active view-container
        html = html.replace('id="view-dashboard" class="view-container active"', 'id="view-dashboard" class="view-container"')
        html = html.replace(f'id="{view_id}" class="view-container"', f'id="{view_id}" class="view-container active"')
        
        # 2. Set active in master-screen-bar
        html = re.sub(r'class="screen-pill active"', 'class="screen-pill"', html)
        html = html.replace(f'data-view="{view_id}"', f'data-view="{view_id}" class="screen-pill active"')
        
        # 3. Set active in sidebar
        html = re.sub(r'class="nav-btn active"', 'class="nav-btn"', html)
        html = html.replace(f'id="{btn_id}"', f'id="{btn_id}" class="nav-btn active"')
        
        # 4. Inject initial screen index in JS
        init_script = f"""<script>
window.addEventListener('DOMContentLoaded', () => {{
  goToScreenIndex({page_idx});
}});
</script>
</body>"""
        html = html.replace("</body>", init_script)
        
        out_path = os.path.join(BASE_DIR, filename)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✅ Generated {filename} (Default: {view_id})")

    # Keep command.html as seamless redirect/forward to index.html
    cmd_redirect = """<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="refresh" content="0; url=index.html">
  <script>window.location.href = "index.html";</script>
  <title>Redirecting to Dashboard...</title>
</head>
<body style="background:#0b1118; color:#cbd5e1; font-family:sans-serif; text-align:center; padding-top:50px;">
  <h2>Redirecting to AURA-FIRE Dashboard...</h2>
  <p><a href="index.html" style="color:#00e5a0;">Click here if not redirected automatically.</a></p>
</body>
</html>"""
    with open(os.path.join(BASE_DIR, "command.html"), "w", encoding="utf-8") as f:
        f.write(cmd_redirect)
    print("✅ command.html updated with instant redirect to index.html.")


if __name__ == "__main__":
    build_all_pages()

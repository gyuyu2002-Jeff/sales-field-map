# -*- coding: utf-8 -*-
"""
全台外勤巡訪地圖總中樞 - 靜態 HTML 生成器
依使用者要求：
1. 完整 RWD 響應式網頁設計（支援手機、平板、桌機極致適配）
   - 手機版底部專屬懸浮視圖切換器（📋 廠商名單 / ⚖️ 上下分割 / 🗺️ 地圖視野）
   - 手機版底部抽屜式訪談紀錄表單 (Bottom-sheet Modal)
   - 頂部導航列手機按鈕自動圖標化適配與防擠壓
   - iOS / Android 觸控安全區支援 (env(safe-area-inset-bottom))
2. 搜尋引擎專注於當前園區與縣市，無跨區干擾
3. 全台 18 縣市 72 大園區順序嚴格依循：西部北到南 -> 東部北到南
"""

import json
import os
import sys

# UTF-8 safety
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DATABASE_FILE = 'taiwan_parks_database.json'
FALLBACK_FILE = 'all_taoyuan_parks.json'

if os.path.exists(DATABASE_FILE):
    with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
        database_bundle = json.load(f)
    print(f"[OK] 成功載入 {DATABASE_FILE}")
elif os.path.exists(FALLBACK_FILE):
    with open(FALLBACK_FILE, 'r', encoding='utf-8') as f:
        taoyuan_parks = json.load(f)
    database_bundle = {
        "counties": {
            "taoyuan": {
                "name": "桃園市", "region": "西部", "icon": "✈️",
                "default_park": "zhongli",
                "parks": list(taoyuan_parks.keys())
            }
        },
        "parks": taoyuan_parks
    }
    print(f"[WARN] 找不到 {DATABASE_FILE}，已回退載入 {FALLBACK_FILE}")
else:
    raise FileNotFoundError("找不到任何工業區資料庫檔案！")

# Compact JSON serialization
database_json = json.dumps(database_bundle, ensure_ascii=False)

html_template = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <title>全台科技＆產業園區地圖</title>
  <meta name="application-name" content="全台科技＆產業園區地圖">
  <meta name="apple-mobile-web-app-title" content="全台科技＆產業園區地圖">
  <meta name="theme-color" content="#16213A">

  <!-- Favicon & Bookmarks Icons (我的最愛與分頁圖示) -->
  <link rel="icon" type="image/svg+xml" href="favicon.svg">
  <link rel="icon" type="image/png" sizes="32x32" href="favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="favicon-16x16.png">
  <link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">
  <link rel="shortcut icon" href="favicon.ico">
  
  <!-- Leaflet CSS -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="" />
  <!-- Google Fonts: Noto Sans TC -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&family=Noto+Serif+TC:wght@700;900&display=swap" rel="stylesheet">

  <style>
    :root {
      --bg-primary: #FCFBF8;
      --navy: #16213A;
      --navy-light: #2A3859;
      --blue: #1A4DA1;
      --blue-subtle: #EEF3FC;
      --accent-orange: #E0622B;
      --accent-green: #2E8540;
      --accent-purple: #7033FF;
      --border: #E6E3DB;
      --text-main: #1F2937;
      --text-muted: #6B7280;
      --card-bg: #FFFFFF;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      -webkit-tap-highlight-color: transparent;
    }

    body {
      font-family: 'Noto Sans TC', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background-color: var(--bg-primary);
      color: var(--text-main);
      height: 100vh;
      height: 100dvh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    /* Top Navigation Header */
    header {
      background: #FFFFFF;
      border-bottom: 1.5px solid var(--border);
      padding: 10px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      z-index: 1000;
      flex-shrink: 0;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 10px;
      min-width: 0;
    }

    .brand-logo {
      width: 36px;
      height: 36px;
      background: var(--navy);
      color: #FFF;
      border-radius: 9px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 19px;
      font-weight: 900;
      box-shadow: 0 2px 6px rgba(22, 33, 58, 0.2);
      flex-shrink: 0;
    }

    .brand-title {
      font-family: 'Noto Serif TC', serif;
      font-size: 18px;
      font-weight: 900;
      color: var(--navy);
      line-height: 1.2;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .brand-subtitle {
      font-size: 11.5px;
      color: var(--text-muted);
      letter-spacing: 0.03em;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-shrink: 0;
    }

    .btn {
      padding: 7px 12px;
      font-size: 12.5px;
      font-weight: 700;
      border-radius: 6px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 5px;
      border: 1px solid var(--border);
      background: #FFFFFF;
      color: var(--navy);
      transition: all 0.15s ease;
      white-space: nowrap;
    }

    .btn:hover {
      background: var(--blue-subtle);
      border-color: var(--blue);
      color: var(--blue);
    }

    .btn-primary {
      background: var(--navy);
      color: #FFFFFF;
      border-color: var(--navy);
    }

    .btn-primary:hover {
      background: var(--blue);
      color: #FFFFFF;
    }

    /* Tier 1: County Navigation Bar (縣市一級切換條 - 西部北到南、東部北到南) */
    .county-nav-bar {
      background: #FFFFFF;
      border-bottom: 1.5px solid var(--border);
      padding: 7px 18px;
      display: flex;
      align-items: center;
      gap: 8px;
      overflow-x: auto;
      white-space: nowrap;
      z-index: 950;
      scrollbar-width: thin;
      flex-shrink: 0;
      -webkit-overflow-scrolling: touch;
    }

    .county-nav-bar::-webkit-scrollbar {
      height: 4px;
    }
    .county-nav-bar::-webkit-scrollbar-thumb {
      background: #D1CDBC;
      border-radius: 2px;
    }

    .region-tag {
      font-size: 11px;
      font-weight: 900;
      padding: 5px 8px;
      border-radius: 6px;
      background: #E5E7EB;
      color: #374151;
      letter-spacing: 0.03em;
      flex-shrink: 0;
    }

    .region-separator {
      width: 1.5px;
      height: 22px;
      background: #E5E3DF;
      margin: 0 4px;
      flex-shrink: 0;
    }

    .county-pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 13px;
      border-radius: 8px;
      font-size: 12.5px;
      font-weight: 800;
      background: #F4F2EC;
      border: 1.5px solid transparent;
      color: var(--navy);
      cursor: pointer;
      transition: all 0.15s ease;
      flex-shrink: 0;
    }

    .county-pill:hover {
      background: #EAE6DC;
      color: var(--blue);
    }

    .county-pill.active {
      background: var(--navy);
      color: #FFFFFF;
      border-color: var(--navy);
      box-shadow: 0 2px 8px rgba(22, 33, 58, 0.25);
    }

    .county-pill-count {
      font-size: 11px;
      padding: 1px 6px;
      border-radius: 999px;
      background: #E0DDD2;
      color: var(--navy);
      font-weight: 800;
    }

    .county-pill.active .county-pill-count {
      background: rgba(255, 255, 255, 0.25);
      color: #FFFFFF;
    }

    /* Tier 2: Park Navigation Bar (園區二級切換條) */
    .park-nav-bar {
      background: #F8F7F3;
      border-bottom: 1.5px solid var(--border);
      padding: 6px 18px;
      overflow-x: auto;
      white-space: nowrap;
      display: flex;
      gap: 8px;
      z-index: 900;
      scrollbar-width: thin;
      flex-shrink: 0;
      -webkit-overflow-scrolling: touch;
    }

    .park-nav-bar::-webkit-scrollbar {
      height: 4px;
    }
    .park-nav-bar::-webkit-scrollbar-thumb {
      background: #CCC8BD;
      border-radius: 2px;
    }

    .park-pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 5px 12px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 700;
      background: #FFFFFF;
      border: 1.5px solid var(--border);
      color: var(--navy);
      cursor: pointer;
      transition: all 0.15s ease;
      flex-shrink: 0;
    }

    .park-pill:hover {
      border-color: var(--blue);
      color: var(--blue);
      background: #FAF8F5;
    }

    .park-pill.active {
      background: var(--blue);
      border-color: var(--blue);
      color: #FFFFFF;
      box-shadow: 0 2px 8px rgba(26, 77, 161, 0.3);
    }

    .park-pill-count {
      font-size: 10.5px;
      padding: 1px 6px;
      border-radius: 999px;
      background: #E8E5DC;
      color: var(--navy);
      font-weight: 800;
    }

    .park-pill.active .park-pill-count {
      background: rgba(255, 255, 255, 0.28);
      color: #FFFFFF;
    }

    /* Main Container (Split Screen on Desktop) */
    .app-container {
      display: flex;
      flex: 1;
      height: calc(100vh - 142px);
      height: calc(100dvh - 142px);
      position: relative;
      overflow: hidden;
    }

    /* Sidebar (Client Cards & Filtering) */
    .sidebar {
      width: 460px;
      background: var(--bg-primary);
      border-right: 1.5px solid var(--border);
      display: flex;
      flex-direction: column;
      z-index: 500;
      flex-shrink: 0;
      box-shadow: 2px 0 12px rgba(22, 33, 58, 0.04);
      height: 100%;
    }

    .sidebar-controls {
      padding: 12px 16px;
      background: #FFFFFF;
      border-bottom: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      gap: 9px;
    }

    .mobile-filter-collapse-btn {
      display: none;
    }

    .collapsible-filters {
      display: flex;
      flex-direction: column;
      gap: 9px;
    }

    /* Search Box */
    .search-row {
      display: flex;
      gap: 6px;
      align-items: center;
    }

    .search-input-wrapper {
      position: relative;
      flex: 1;
      display: flex;
      align-items: center;
    }

    .search-input-wrapper input {
      width: 100%;
      padding: 8px 32px 8px 34px;
      font-size: 13.5px;
      border: 1.5px solid var(--border);
      border-radius: 7px;
      outline: none;
      font-family: inherit;
      background: #FAFAF8;
      transition: all 0.15s;
    }

    .search-input-wrapper input:focus {
      border-color: var(--blue);
      background: #FFF;
      box-shadow: 0 0 0 3px rgba(26, 77, 161, 0.12);
    }

    .search-icon-left {
      position: absolute;
      left: 10px;
      color: var(--text-muted);
      font-size: 13px;
      pointer-events: none;
    }

    .search-clear-btn {
      position: absolute;
      right: 8px;
      background: none;
      border: none;
      color: #9CA3AF;
      cursor: pointer;
      font-size: 13px;
      padding: 3px 6px;
      border-radius: 4px;
      display: none;
      line-height: 1;
    }

    .search-clear-btn:hover {
      color: var(--navy);
      background: #E5E7EB;
    }

    /* Road & Industry Filter Chips */
    .chips-group {
      display: flex;
      flex-direction: column;
      gap: 5px;
    }

    .chips-label {
      font-size: 11px;
      font-weight: 800;
      color: var(--navy);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .chips-scroll {
      display: flex;
      gap: 5px;
      overflow-x: auto;
      padding-bottom: 2px;
      scrollbar-width: thin;
      -webkit-overflow-scrolling: touch;
    }

    .chips-scroll::-webkit-scrollbar {
      height: 3px;
    }
    .chips-scroll::-webkit-scrollbar-thumb {
      background: #D1CDBC;
      border-radius: 2px;
    }

    .chip {
      padding: 4px 9px;
      border-radius: 6px;
      font-size: 11.5px;
      font-weight: 600;
      background: #F4F2EC;
      color: #4B5563;
      border: 1px solid transparent;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.15s;
      flex-shrink: 0;
    }

    .chip:hover {
      background: #EAE6DC;
      color: var(--navy);
    }

    .chip.active {
      background: var(--navy);
      color: #FFFFFF;
      font-weight: 800;
    }

    /* Status Filters */
    .status-chips-scroll {
      display: flex;
      gap: 5px;
      overflow-x: auto;
      scrollbar-width: none;
      -webkit-overflow-scrolling: touch;
    }

    .chip-status {
      padding: 5px 10px;
      font-size: 11.5px;
      font-weight: 700;
      border-radius: 6px;
      border: 1px solid var(--border);
      background: #FFFFFF;
      color: #4B5563;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.15s ease;
    }

    .chip-status:hover {
      border-color: var(--navy);
      color: var(--navy);
    }

    .chip-status.active-all { background: var(--navy); color: #FFF; border-color: var(--navy); }
    .chip-status.active-listed { background: var(--accent-orange); color: #FFF; border-color: var(--accent-orange); }
    .chip-status.active-pending { background: var(--blue); color: #FFF; border-color: var(--blue); }
    .chip-status.active-negotiating { background: var(--accent-purple); color: #FFF; border-color: var(--accent-purple); }
    .chip-status.active-done { background: var(--accent-green); color: #FFF; border-color: var(--accent-green); }

    /* Client List Area */
    .client-list-header {
      padding: 8px 16px;
      background: #FAF8F5;
      border-bottom: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 11.5px;
      font-weight: 700;
      color: var(--text-muted);
    }

    .client-list {
      flex: 1;
      overflow-y: auto;
      padding: 10px;
      display: flex;
      flex-direction: column;
      gap: 9px;
      scrollbar-width: thin;
      -webkit-overflow-scrolling: touch;
    }

    .client-card {
      background: var(--card-bg);
      border: 1.5px solid var(--border);
      border-radius: 8px;
      padding: 11px 13px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      cursor: pointer;
      transition: all 0.15s ease;
      position: relative;
    }

    .client-card:hover {
      border-color: var(--blue);
      box-shadow: 0 4px 12px rgba(22, 33, 58, 0.08);
      transform: translateY(-1px);
    }

    .client-card.active {
      border-color: var(--navy);
      box-shadow: 0 0 0 2px var(--navy);
      background: #FCFBF8;
    }

    .card-top {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 6px;
    }

    .card-title {
      font-size: 14.5px;
      font-weight: 800;
      color: var(--navy);
      line-height: 1.3;
      flex: 1;
    }

    .badge-listed {
      font-size: 10.5px;
      font-weight: 800;
      padding: 1.5px 6px;
      border-radius: 4px;
      background: #FEF3C7;
      color: #92400E;
      border: 1px solid #FDE68A;
      white-space: nowrap;
    }

    .card-address {
      font-size: 12px;
      color: #4B5563;
      display: flex;
      align-items: center;
      gap: 5px;
      line-height: 1.35;
    }

    .card-road {
      font-size: 11px;
      font-weight: 800;
      color: var(--blue);
      background: var(--blue-subtle);
      padding: 1px 6px;
      border-radius: 4px;
      white-space: nowrap;
    }

    .card-meta {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 11.5px;
      color: var(--text-muted);
      flex-wrap: wrap;
    }

    .badge-industry {
      background: #F3F4F6;
      padding: 1px 6px;
      border-radius: 4px;
      font-size: 11px;
      color: #374151;
    }

    .card-notes {
      font-size: 11.5px;
      background: #F8FAFC;
      border: 1px dashed #CBD5E1;
      padding: 5px 8px;
      border-radius: 6px;
      color: #334155;
      line-height: 1.35;
    }

    /* Structured Visit Record Box inside Card */
    .card-visit-box {
      background: #F0FDF4;
      border: 1.5px solid #BBF7D0;
      border-radius: 7px;
      padding: 7px 10px;
      margin-top: 2px;
      display: flex;
      flex-direction: column;
      gap: 3px;
      cursor: pointer;
      transition: all 0.15s ease;
    }

    .card-visit-box:hover {
      background: #DCFCE7;
      border-color: #86EFAC;
    }

    .card-visit-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 11px;
      font-weight: 800;
      color: #166534;
    }

    .badge-outcome {
      font-size: 10px;
      font-weight: 800;
      padding: 1px 6px;
      border-radius: 4px;
      background: #DCFCE7;
      color: #15803D;
      border: 1px solid #BBF7D0;
    }

    .card-visit-summary {
      font-size: 11.5px;
      color: #1F2937;
      line-height: 1.35;
      font-weight: 500;
    }

    .card-visit-next {
      font-size: 10.5px;
      color: #047857;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 3px;
    }

    .card-actions {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 6px;
      margin-top: 2px;
    }

    .status-select {
      font-size: 11.5px;
      font-weight: 700;
      padding: 4px 8px;
      border-radius: 6px;
      border: 1px solid var(--border);
      cursor: pointer;
      outline: none;
    }

    .status-select.status-pending { background: #EEF3FC; color: var(--blue); border-color: #CADCF8; }
    .status-select.status-negotiating { background: #F3EFFE; color: var(--accent-purple); border-color: #D8CCFD; }
    .status-select.status-done { background: #EBF7EE; color: var(--accent-green); border-color: #B9E6C3; }

    .nav-btn {
      padding: 4px 9px;
      font-size: 11px;
      font-weight: 800;
      background: var(--accent-orange);
      color: #FFFFFF;
      border-radius: 6px;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 3px;
      transition: opacity 0.15s;
    }

    .nav-btn:hover {
      opacity: 0.9;
    }

    .btn-log {
      padding: 4px 8px;
      font-size: 11px;
      font-weight: 700;
      background: #FFFFFF;
      border: 1px solid #16213A;
      color: var(--navy);
      border-radius: 6px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 3px;
      transition: all 0.15s;
    }

    .btn-log:hover {
      background: #EEF3FC;
      border-color: var(--blue);
      color: var(--blue);
    }

    .btn-log.has-logs {
      background: #EBF7EE;
      border-color: #2E8540;
      color: #2E8540;
      font-weight: 800;
    }

    /* Map Styling */
    #map {
      flex: 1;
      height: 100%;
      background: #E5E3DF;
    }

    /* Custom Map Markers */
    .custom-marker {
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
      color: #FFFFFF;
      font-weight: 900;
      font-size: 12px;
      border: 2px solid #FFFFFF;
      box-shadow: 0 3px 8px rgba(0,0,0,0.3);
      cursor: pointer;
      transition: transform 0.15s ease;
    }

    .custom-marker:hover {
      transform: scale(1.2);
      z-index: 9999 !important;
    }

    .marker-pending { background: var(--blue); }
    .marker-listed { background: var(--accent-orange); }
    .marker-done { background: var(--accent-green); }
    .marker-negotiating { background: var(--accent-purple); }

    /* 自訂地圖放大自動顯現廠家名稱標籤 (Auto POI Labels on Zoom) */
    .leaflet-tooltip.marker-auto-tooltip {
      display: none !important;
      opacity: 0 !important;
      background: #FFFFFF;
      color: #16213A;
      border: 1.5px solid #CBD5E1;
      border-radius: 6px;
      padding: 3px 8px;
      box-shadow: 0 4px 12px rgba(22, 33, 58, 0.16);
      font-family: 'Noto Sans TC', -apple-system, BlinkMacSystemFont, sans-serif;
      pointer-events: auto;
      cursor: pointer;
      white-space: nowrap;
      transition: opacity 0.15s ease, transform 0.15s ease;
      user-select: none;
      z-index: 600;
    }

    .leaflet-tooltip.marker-auto-tooltip:hover {
      border-color: #1A4DA1;
      box-shadow: 0 6px 16px rgba(26, 77, 161, 0.25);
      z-index: 9999 !important;
    }

    .leaflet-tooltip-top.marker-auto-tooltip:before {
      border-top-color: #CBD5E1;
    }

    /* 當地圖放大到街道級別 (Zoom >= 16) 時自動展現標籤 */
    #map.show-auto-labels .leaflet-tooltip.marker-auto-tooltip {
      display: flex !important;
      flex-direction: column;
      opacity: 1 !important;
    }

    /* 狀態邊框顏色標示 */
    .marker-auto-tooltip.status-done {
      border-color: #2E8540;
      border-left: 4px solid #2E8540;
    }
    .marker-auto-tooltip.status-negotiating {
      border-color: #B45309;
      border-left: 4px solid #B45309;
    }
    .marker-auto-tooltip.status-listed {
      border-color: #D97706;
    }

    /* 標籤內文字排版 */
    .marker-auto-tooltip .lbl-title {
      font-weight: 800;
      font-size: 11.5px;
      color: #16213A;
      display: flex;
      align-items: center;
      gap: 4px;
      line-height: 1.25;
      max-width: 220px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .marker-auto-tooltip .lbl-star {
      font-size: 9.5px;
      background: #FEF3C7;
      color: #92400E;
      padding: 1px 4px;
      border-radius: 3px;
      font-weight: 800;
    }

    .marker-auto-tooltip .lbl-badge-done {
      font-size: 9px;
      background: #EBF7EE;
      color: #2E8540;
      padding: 1px 4px;
      border-radius: 3px;
      font-weight: 800;
    }

    .marker-auto-tooltip .lbl-badge-neg {
      font-size: 9px;
      background: #FEF3C7;
      color: #B45309;
      padding: 1px 4px;
      border-radius: 3px;
      font-weight: 800;
    }

    /* 超近距離 (Zoom >= 17.5) 顯示路段與產業類別 */
    .marker-auto-tooltip .lbl-detail {
      display: none;
      font-size: 10px;
      color: #64748B;
      margin-top: 2px;
      border-top: 1px dashed #E2E8F0;
      padding-top: 2px;
      align-items: center;
      gap: 4px;
    }

    #map.show-detailed-labels .marker-auto-tooltip .lbl-detail {
      display: flex !important;
    }

    /* Map overlay controls */
    .map-controls-panel {
      position: absolute;
      top: 16px;
      right: 16px;
      z-index: 800;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .map-tool-btn {
      background: #FFFFFF;
      border: 1.5px solid var(--border);
      color: var(--navy);
      padding: 9px 12px;
      border-radius: 8px;
      font-weight: 700;
      font-size: 12.5px;
      cursor: pointer;
      box-shadow: 0 4px 14px rgba(22, 33, 58, 0.1);
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s ease;
    }

    .map-tool-btn:hover {
      background: #FAFAF7;
      border-color: var(--navy);
    }

    .map-tool-btn.active-state {
      background: #EEF3FC;
      border-color: var(--blue);
      color: var(--blue);
      font-weight: 800;
      box-shadow: 0 4px 14px rgba(26, 77, 161, 0.18);
    }

    /* Modal Styling */
    .modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(22, 33, 58, 0.6);
      z-index: 2000;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 16px;
    }

    .modal-overlay.open {
      display: flex;
    }

    .modal-card {
      background: #FFFFFF;
      border-radius: 12px;
      max-width: 560px;
      width: 100%;
      padding: 22px;
      box-shadow: 0 20px 40px rgba(0,0,0,0.25);
      max-height: 90vh;
      overflow-y: auto;
    }

    .modal-card h3 {
      font-size: 18px;
      font-weight: 900;
      color: var(--navy);
      margin-bottom: 14px;
    }

    .form-group {
      margin-bottom: 12px;
    }

    .form-group label {
      display: block;
      font-size: 12.5px;
      font-weight: 700;
      margin-bottom: 4px;
      color: var(--navy);
    }

    .form-group input, .form-group textarea, .form-group select {
      width: 100%;
      padding: 8px 10px;
      border: 1px solid var(--border);
      border-radius: 6px;
      font-size: 13.5px;
      font-family: inherit;
    }

    /* Timeline History Item */
    .timeline-card {
      background: #FAFAF8;
      border: 1.5px solid var(--border);
      border-radius: 8px;
      padding: 10px 12px;
      position: relative;
    }

    /* 預設常駐縣市按鈕與標籤 */
    .btn-default-setting {
      background: #FFFFFF;
      border: 1px solid #CADCF8;
      color: #1E40AF;
      font-weight: 700;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 6px 10px;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .btn-default-setting:hover {
      background: #EEF3FC;
      border-color: #2563EB;
      box-shadow: 0 1px 4px rgba(37, 99, 235, 0.15);
    }
    .btn-default-setting b {
      color: #16213A;
      font-weight: 900;
    }
    .default-pill-badge {
      display: inline-block;
      font-size: 9.5px;
      font-weight: 900;
      color: #B45309;
      background: #FEF3C7;
      border: 1px solid #FDE68A;
      border-radius: 4px;
      padding: 1px 4px;
      margin-left: 4px;
      line-height: 1.2;
    }

    /* 預設縣市選擇視窗網格與卡片 */
    .county-select-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
    }
    @media (max-width: 600px) {
      .county-select-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 6px;
      }
    }
    .county-select-card {
      background: #FFFFFF;
      border: 1.5px solid var(--border);
      border-radius: 8px;
      padding: 9px 11px;
      cursor: pointer;
      display: flex;
      flex-direction: column;
      gap: 2px;
      transition: all 0.15s ease;
      user-select: none;
      -webkit-tap-highlight-color: transparent;
      position: relative;
    }
    .county-select-card:hover {
      border-color: var(--blue);
      background: #F4F8FD;
    }
    .county-select-card.selected {
      border-color: var(--blue);
      background: #EEF3FC;
      box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
    }
    .county-select-card .card-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .county-select-card .card-name {
      font-size: 13px;
      font-weight: 800;
      color: var(--navy);
    }
    .county-select-card .card-check {
      font-size: 13px;
      color: var(--blue);
      display: none;
      font-weight: 900;
    }
    .county-select-card.selected .card-check {
      display: inline-block;
    }
    .county-select-card .card-meta {
      font-size: 11px;
      color: var(--text-muted);
      font-weight: 600;
    }

    /* 輕量級 Toast 提示框 */
    .toast-notice {
      position: fixed;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%) translateY(120px);
      background: rgba(22, 33, 58, 0.95);
      color: #FFFFFF;
      padding: 10px 18px;
      border-radius: 999px;
      font-size: 13px;
      font-weight: 700;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
      z-index: 9999;
      display: flex;
      align-items: center;
      gap: 8px;
      opacity: 0;
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      pointer-events: none;
    }
    .toast-notice.show {
      transform: translateX(-50%) translateY(0);
      opacity: 1;
    }

    /* ========================================================
       📱 RWD 響應式網頁設計核心樣式 (Responsive Web Design)
       ======================================================== */
    .mobile-view-toggle {
      display: none;
    }

    /* 平板適配 (iPad / Tablet: 769px ~ 1024px) */
    @media (max-width: 1024px) {
      .sidebar {
        width: 380px;
      }
      .brand-title {
        font-size: 16px;
      }
    }

    /* 手機極致適配 (Mobile Phone: <= 768px) */
    @media (max-width: 768px) {
      header {
        padding: 8px 12px;
        gap: 8px;
      }

      .brand-logo {
        width: 30px;
        height: 30px;
        font-size: 16px;
        border-radius: 7px;
      }

      .brand-title {
        font-size: 15px;
      }

      .brand-subtitle {
        display: none; /* 隱藏過長副標題，避免破版 */
      }

      .header-actions {
        gap: 4px;
      }

      .btn {
        padding: 5px 8px;
        font-size: 11px;
      }

      .county-nav-bar {
        padding: 5px 10px;
        gap: 6px;
      }

      .county-pill {
        padding: 5px 10px;
        font-size: 11.5px;
        border-radius: 6px;
      }

      .region-tag {
        font-size: 10px;
        padding: 4px 6px;
      }

      .park-nav-bar {
        padding: 5px 10px;
        gap: 5px;
      }

      .park-pill {
        padding: 4px 10px;
        font-size: 11px;
      }

      /* Container 適配手機彈性高度，停在底欄上方，絕不溢出或被遮蓋 */
      .app-container {
        flex: 1;
        min-height: 0;
        height: auto;
        position: relative;
        overflow: hidden;
      }

      /* 手機專屬底部常駐模式切換導航列 (Docked Bottom Navigation Bar) - 獨立空間，絕不遮擋卡片 */
      .mobile-view-toggle {
        display: flex;
        flex-shrink: 0;
        position: relative;
        bottom: auto;
        left: auto;
        transform: none;
        width: 100%;
        border-radius: 0;
        background: #16213A;
        background: rgba(22, 33, 58, 0.98);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        padding: 6px 12px;
        padding-bottom: calc(6px + env(safe-area-inset-bottom, 0px));
        border: none;
        border-top: 1.5px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 -4px 16px rgba(0, 0, 0, 0.25);
        gap: 6px;
        z-index: 1000;
        justify-content: center;
        align-items: center;
        box-sizing: border-box;
      }

      .view-btn {
        flex: 1;
        max-width: 160px;
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.14);
        color: #D1D5DB;
        padding: 8px 10px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 800;
        cursor: pointer;
        transition: all 0.15s ease;
        white-space: nowrap;
        text-align: center;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
      }

      .view-btn.active {
        background: #FFFFFF;
        color: #16213A;
        border-color: #FFFFFF;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
      }

      /* 手機視圖模式 1: 分割模式 (地圖 36%，名單 64%，視野更寬廣) */
      .app-container.mobile-split {
        flex-direction: column;
      }
      .app-container.mobile-split #map {
        display: block;
        height: 36%;
        order: 1;
        flex-shrink: 0;
      }
      .app-container.mobile-split .sidebar {
        display: flex;
        flex-direction: column;
        width: 100%;
        height: 64%;
        min-height: 0;
        order: 2;
        border-right: none;
        border-top: 2px solid var(--border);
        overflow: hidden;
      }

      /* 手機視圖模式 2: 名單全螢幕模式 */
      .app-container.mobile-list #map {
        display: none !important;
      }
      .app-container.mobile-list .sidebar {
        display: flex !important;
        flex-direction: column !important;
        width: 100% !important;
        height: 100% !important;
        min-height: 0 !important;
        border-right: none;
        overflow: hidden;
      }

      /* 手機視圖模式 3: 地圖全螢幕模式 */
      .app-container.mobile-map .sidebar {
        display: none !important;
      }
      .app-container.mobile-map #map {
        display: block !important;
        width: 100% !important;
        height: 100% !important;
      }

      /* 側邊篩選列在手機端緊湊化 */
      .sidebar-controls {
        padding: 8px 10px;
        gap: 6px;
      }

      .mobile-filter-collapse-btn {
        display: flex !important;
        align-items: center;
        justify-content: space-between;
        width: 100%;
        background: #F4F2EC;
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 5px 10px;
        font-size: 11.5px;
        font-weight: 700;
        color: var(--navy);
        cursor: pointer;
        margin-top: 1px;
        transition: all 0.15s ease;
      }

      .mobile-filter-collapse-btn:hover {
        background: #EAE6DC;
      }

      .collapsible-filters {
        display: flex;
        flex-direction: column;
        gap: 6px;
      }

      .collapsible-filters.collapsed {
        display: none !important;
      }

      /* 卡片清單底部留有足夠內距，最後一張卡片完整可見 */
      .client-list {
        flex: 1;
        min-height: 0;
        overflow-y: auto;
        padding: 10px;
        padding-bottom: 24px;
        -webkit-overflow-scrolling: touch;
      }

      /* 手機彈窗抽屜化 (Bottom-Sheet Modal) */
      .modal-overlay {
        padding: 0;
        align-items: flex-end;
      }

      .modal-card {
        max-width: 100%;
        border-radius: 16px 16px 0 0;
        padding: 18px 16px calc(24px + env(safe-area-inset-bottom)) 16px;
        max-height: 85vh;
        max-height: 85dvh;
      }

      .map-controls-panel {
        top: 10px;
        right: 10px;
      }

      .map-tool-btn {
        padding: 7px 10px;
        font-size: 11px;
      }
    }

    /* 超小螢幕手機適配 (<= 420px) */
    @media (max-width: 420px) {
      .brand-title {
        font-size: 14px;
      }
      .header-actions .btn-text {
        display: none; /* 超小螢幕隱藏文字僅保留圖標 */
      }
      .header-actions .btn {
        padding: 6px 8px;
        font-size: 13px;
      }
    }
  </style>
</head>
<body>

  <!-- Top Header Navigation -->
  <header>
    <div class="brand">
      <div class="brand-logo">🗺️</div>
      <div>
        <div class="brand-title" id="headerTitle">全台科技＆產業園區地圖</div>
        <div class="brand-subtitle" id="headerSubtitle">18 縣市 72 大工業與科技園區 · 13,424 家廠商動線指南</div>
      </div>
    </div>

    <div class="header-actions">
      <button class="btn btn-default-setting" id="btnDefaultCountySetting" onclick="openDefaultCountyModal(false)" title="點擊設定或更改預設常駐縣市">
        <span>⭐</span><span class="btn-text"> 預設: </span><b id="headerDefaultCountyLabel">桃園市</b>
      </button>
      <button class="btn" id="btnExport" title="匯出當前拜訪狀態為 CSV 檔（含詳細拜訪紀錄與摘要）">
        <span>📤</span><span class="btn-text"> 匯出記錄</span>
      </button>
      <button class="btn" id="btnImport" title="匯入客製化客戶名單 CSV">
        <span>📥</span><span class="btn-text"> 匯入名單</span>
      </button>
      <button class="btn btn-primary" id="btnAddClient" title="新增自訂客戶">
        <span>➕</span><span class="btn-text"> 新增客戶</span>
      </button>
      <input type="file" id="fileInput" accept=".csv" style="display: none;" />
    </div>
  </header>

  <!-- Tier 1: 縣市導航列 (西部北到南 -> 東部北到南) -->
  <nav class="county-nav-bar" id="countyNavBar">
    <!-- Populated by JavaScript in exact geographic order -->
  </nav>

  <!-- Tier 2: 園區導航列 (所選縣市之各大工業區與科學園區) -->
  <nav class="park-nav-bar" id="parkNavBar">
    <!-- Populated dynamically based on selected county -->
  </nav>

  <!-- Main Split Container (Desktop Side-by-Side, Mobile Responsive Split/List/Map) -->
  <div class="app-container mobile-split" id="appContainer">
    
    <!-- Sidebar: Search & Client Cards -->
    <aside class="sidebar">
      
      <div class="sidebar-controls">
        <!-- Search bar with Clear & Search buttons -->
        <div class="search-row">
          <div class="search-input-wrapper">
            <span class="search-icon-left">🔍</span>
            <input type="text" id="searchInput" placeholder="搜尋當前園區公司名稱、路名、地址、聯絡人..." autocomplete="off" />
            <button id="btnClearSearch" class="search-clear-btn" title="清除搜尋字詞">✕</button>
          </div>
          <button id="btnDoSearch" class="btn btn-primary" style="padding: 7px 12px;">搜尋</button>
        </div>

        <!-- Mobile Filter Collapse Toggle Button -->
        <button type="button" class="mobile-filter-collapse-btn" id="btnToggleFilters" onclick="toggleMobileFilters()">
          <span>⚡ 快捷標籤（產業 / 同路 / 狀態）</span>
          <span id="filtersToggleText">▲ 收合篩選</span>
        </button>

        <div id="collapsibleFilterSection" class="collapsible-filters">
          <!-- Filter 1: By Industry (產業別快篩) -->
          <div class="chips-group">
            <div class="chips-label">
              <span>🏭 產業類別快篩</span>
              <span id="indCurrentLabel" style="font-size:10.5px; color:var(--blue);">全部產業</span>
            </div>
            <div class="chips-scroll" id="industryChips">
              <!-- Dynamically populated -->
            </div>
          </div>

          <!-- Filter 2: By Road (同路巡訪快篩) -->
          <div class="chips-group">
            <div class="chips-label">
              <span>📍 同路巡訪快篩（同一條路順路拜訪）</span>
              <span id="roadCurrentLabel" style="font-size:10.5px; color:var(--blue);">全部路段</span>
            </div>
            <div class="chips-scroll" id="roadChips">
              <!-- Dynamically populated -->
            </div>
          </div>

          <!-- Filter 3: By Visit Status & Tier -->
          <div class="chips-group">
            <div class="chips-label">🎯 狀態與等級</div>
            <div class="status-chips-scroll" id="statusChips">
              <button class="chip chip-status active-all" data-status="ALL">全部 (<span id="countAll">0</span>)</button>
              <button class="chip chip-status" data-status="LISTED">⭐ 上市櫃 (<span id="countListed">0</span>)</button>
              <button class="chip chip-status" data-status="尚未拜訪">⏳ 尚未拜訪 (<span id="countPending">0</span>)</button>
              <button class="chip chip-status" data-status="洽談中">💬 洽談中 (<span id="countNegotiating">0</span>)</button>
              <button class="chip chip-status" data-status="已拜訪">✅ 已拜訪 (<span id="countDone">0</span>)</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Result Count Header -->
      <div class="client-list-header">
        <span id="resultCountText">顯示 0 家廠商</span>
        <button id="btnResetFilter" style="background:none; border:none; color:var(--blue); font-size:11.5px; font-weight:700; cursor:pointer;">重設篩選</button>
      </div>

      <!-- List of Clients -->
      <div class="client-list" id="clientList">
        <!-- Rendered by JavaScript -->
      </div>

    </aside>

    <!-- Map Container -->
    <div id="map"></div>

    <!-- Map Floating Tools -->
    <div class="map-controls-panel">
      <button class="map-tool-btn active-state" id="btnToggleLabels" onclick="toggleAutoLabels()" title="切換地圖放大時是否自動顯現廠商名稱標籤">
        🏷️ 廠名: 自動
      </button>
      <button class="map-tool-btn" id="btnLocateMe" title="取得您手機或設備目前的 GPS 位置">
        🎯 我的位置
      </button>
      <button class="map-tool-btn" id="btnFitBounds" title="縮放顯示全部標記點">
        🗺️ 全區視野
      </button>
    </div>

  </div>

  <!-- 📱 手機專屬浮動視圖切換列 (RWD Floating View Switcher) -->
  <div class="mobile-view-toggle" id="mobileViewToggle">
    <button class="view-btn" id="btnViewList" onclick="setMobileView('list')">
      📋 廠商名單 (<span id="mobileCount">0</span>)
    </button>
    <button class="view-btn active" id="btnViewSplit" onclick="setMobileView('split')">
      ⚖️ 分割
    </button>
    <button class="view-btn" id="btnViewMap" onclick="setMobileView('map')">
      🗺️ 地圖視野
    </button>
  </div>

  <!-- Modal 1: 拜訪內容紀錄 (外勤業務核心 CRM 功能) -->
  <div class="modal-overlay" id="modalVisitLog">
    <div class="modal-card">
      <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px; border-bottom:1.5px solid var(--border); padding-bottom:10px;">
        <div>
          <div style="font-size:11px; font-weight:800; color:var(--blue); text-transform:uppercase; letter-spacing:0.05em;">外勤巡訪紀錄</div>
          <h3 id="visitModalTitle" style="margin:2px 0 0 0; font-size:17px; color:var(--navy); font-weight:900;">客戶拜訪紀錄</h3>
          <div id="visitModalSubtitle" style="font-size:11.5px; color:var(--text-muted); margin-top:2px;"></div>
        </div>
        <button type="button" class="btn" id="btnCloseVisitModal" style="padding:4px 8px; font-size:14px;">✕</button>
      </div>

      <!-- Form to Add New Visit Record -->
      <div style="background:#F9F8F5; border:1px solid #E6E3DB; border-radius:8px; padding:12px; margin-bottom:14px;">
        <div style="font-weight:800; font-size:13px; color:var(--navy); margin-bottom:10px; display:flex; align-items:center; gap:5px;">
          <span>📝 填寫本次拜訪內容紀錄</span>
        </div>
        <form id="formAddVisitLog">
          <input type="hidden" id="visitLogClientId" />

          <div style="display:flex; gap:8px; margin-bottom:8px;">
            <div style="flex:1;">
              <label style="font-size:11.5px; font-weight:700; color:var(--navy); display:block; margin-bottom:3px;">📅 拜訪日期時間 *</label>
              <input type="datetime-local" id="logDate" required style="width:100%; padding:6px 8px; border:1px solid var(--border); border-radius:6px; font-size:12px;" />
            </div>
            <div style="flex:1;">
              <label style="font-size:11.5px; font-weight:700; color:var(--navy); display:block; margin-bottom:3px;">👤 接洽對象 / 職稱 *</label>
              <input type="text" id="logContact" required placeholder="例如：陳廠長、採購部林專員" style="width:100%; padding:6px 8px; border:1px solid var(--border); border-radius:6px; font-size:12px;" />
            </div>
          </div>

          <div style="display:flex; gap:8px; margin-bottom:8px;">
            <div style="flex:1;">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px;">
                <label style="font-size:11.5px; font-weight:700; color:var(--navy); margin:0;">🎯 洽談階段 / 進度 *</label>
                <button type="button" onclick="openStageManagerModal()" style="background:none; border:none; color:var(--blue); font-size:11px; font-weight:800; cursor:pointer; padding:0; text-decoration:underline;" title="自訂階段名稱並設為永久常駐">⚙️ 自訂常駐</button>
              </div>
              <select id="logOutcome" onchange="handleOutcomeSelectChange(this)" style="width:100%; padding:6px 8px; border:1px solid var(--border); border-radius:6px; font-size:12px; font-weight:700;">
                <!-- Populated dynamically by populateStageOptions() -->
              </select>
            </div>
            <div style="flex:1;">
              <label style="font-size:11.5px; font-weight:700; color:var(--navy); display:block; margin-bottom:3px;">⏰ 下次預計待辦 / 回訪日</label>
              <input type="text" id="logNextAction" placeholder="例如：下週三送樣、10/25提供報價" style="width:100%; padding:6px 8px; border:1px solid var(--border); border-radius:6px; font-size:12px;" />
            </div>
          </div>

          <div style="margin-bottom:10px;">
            <label style="font-size:11.5px; font-weight:700; color:var(--navy); display:block; margin-bottom:3px;">💬 洽談重點與客戶需求內容 *</label>
            <textarea id="logSummary" rows="3" required placeholder="請詳細記錄：今天拜訪了解到的客戶痛點、目前使用的品牌/耗材、預計採購數量、關鍵決策窗口是誰、何時需提出方案..." style="width:100%; padding:7px 9px; border:1px solid var(--border); border-radius:6px; font-size:12.5px; font-family:inherit;"></textarea>
          </div>

          <div style="display:flex; justify-content:space-between; align-items:center;">
            <label style="font-size:11.5px; color:#4B5563; display:flex; align-items:center; gap:5px; cursor:pointer;">
              <input type="checkbox" id="logAutoSetDone" checked />
              <span>自動更新狀態為「✅ 已拜訪」</span>
            </label>
            <button type="submit" class="btn btn-primary" style="padding:6px 14px; font-size:12.5px;">
              💾 儲存本次紀錄
            </button>
          </div>
        </form>
      </div>

      <!-- History Records Section -->
      <div>
        <div style="font-weight:800; font-size:13px; color:var(--navy); margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
          <span>📜 歷史拜訪歷程時間軸 (<span id="logHistoryCount">0</span> 筆)</span>
        </div>
        <div id="logHistoryList" style="max-height: 220px; overflow-y: auto; display:flex; flex-direction:column; gap:8px;">
          <!-- Dynamically populated -->
        </div>
      </div>
    </div>
  </div>

  <!-- Modal 2: 新增客戶 -->
  <div class="modal-overlay" id="modalAdd">
    <div class="modal-card">
      <h3>➕ 新增拜訪客戶</h3>
      <form id="formAddClient">
        <div class="form-group">
          <label>公司 / 廠房名稱 *</label>
          <input type="text" id="addName" required placeholder="例如：台達電子工業" />
        </div>
        <div class="form-group">
          <label>所在路段 *</label>
          <input type="text" id="addRoad" required placeholder="例如：中園路、科技一路、中華路" />
        </div>
        <div class="form-group">
          <label>完整地址 *</label>
          <input type="text" id="addAddress" required placeholder="例如：新竹市東區力行路..." />
        </div>
        <div style="display:flex; gap:10px;">
          <div class="form-group" style="flex:1;">
            <label>緯度 (Lat) *</label>
            <input type="number" step="0.0001" id="addLat" value="24.7780" required />
          </div>
          <div class="form-group" style="flex:1;">
            <label>經度 (Lng) *</label>
            <input type="number" step="0.0001" id="addLng" value="121.0140" required />
          </div>
        </div>
        <div style="display:flex; gap:10px;">
          <div class="form-group" style="flex:1;">
            <label>聯絡窗口</label>
            <input type="text" id="addContact" placeholder="例如：陳廠長" />
          </div>
          <div class="form-group" style="flex:1;">
            <label>聯絡電話</label>
            <input type="text" id="addPhone" placeholder="例如：03-563-xxxx" />
          </div>
        </div>
        <div class="form-group">
          <label>上市櫃指標企業？</label>
          <select id="addListed">
            <option value="否">否 (一般企業)</option>
            <option value="是">是 (上市櫃大廠)</option>
          </select>
        </div>
        <div class="form-group">
          <label>拜訪備忘錄 / 洽談重點</label>
          <textarea id="addNotes" rows="3" placeholder="記錄該客戶需求、門禁限制或產品詢價重點..."></textarea>
        </div>
        <div style="display:flex; justify-content:flex-end; gap:8px; margin-top:16px;">
          <button type="button" class="btn" id="btnCloseModal">取消</button>
          <button type="submit" class="btn btn-primary">儲存建立</button>
        </div>
      </form>
    </div>
  </div>

  <!-- Modal 3: 選擇預設常駐縣市 (首次進入詢問與隨時切換) -->
  <div class="modal-overlay" id="modalDefaultCounty">
    <div class="modal-card" style="max-width: 660px;">
      <!-- Modal Header -->
      <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px; border-bottom:1.5px solid var(--border); padding-bottom:10px;">
        <div>
          <div style="font-size:11px; font-weight:800; color:var(--blue); text-transform:uppercase; letter-spacing:0.05em; display:flex; align-items:center; gap:5px;">
            <span>📍</span> 常駐巡訪縣市設定
          </div>
          <h3 id="defaultModalTitle" style="margin:2px 0 0 0; font-size:17px; color:var(--navy); font-weight:900;">
            請問您最常巡訪的「預設常駐縣市」是？
          </h3>
          <div id="defaultModalSubtitle" style="font-size:11.5px; color:var(--text-muted); margin-top:2px; line-height:1.4;">
            日後開啟巡訪地圖時，將優先自動為您載入該縣市。（隨時可在上方導航列自由切換全台 18 縣市）
          </div>
        </div>
        <button type="button" class="btn" id="btnCloseDefaultCountyModal" style="padding:4px 8px; font-size:14px;" onclick="closeDefaultCountyModal()">✕</button>
      </div>

      <!-- Quick info / Selection preview -->
      <div id="defaultCountySelectionPreview" style="background:#EEF3FC; border:1px solid #CADCF8; border-radius:8px; padding:9px 12px; margin-bottom:12px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:6px;">
        <div>
          <span style="font-size:11.5px; color:#1E40AF; font-weight:700;">目前已選取：</span>
          <span id="selectedCountyPreviewText" style="font-size:13.5px; font-weight:900; color:var(--navy);">✈️ 桃園市</span>
        </div>
        <span style="font-size:10.5px; background:#DBEAFE; color:#1E40AF; padding:2px 8px; border-radius:12px; font-weight:800;">點選下方卡片切換</span>
      </div>

      <!-- Scrollable County List -->
      <div style="max-height: 50vh; max-height: 50dvh; overflow-y: auto; padding-right: 2px; display:flex; flex-direction:column; gap:10px;">
        <div class="county-select-grid" id="defaultCountyGrid"></div>
        <div style="border-top:1px dashed var(--border); padding-top:8px;">
          <div class="county-select-grid" id="defaultCountyGridAll"></div>
        </div>
      </div>

      <!-- Modal Footer -->
      <div style="margin-top:12px; border-top:1.5px solid var(--border); padding-top:10px; display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:8px;">
        <label style="display:inline-flex; align-items:center; gap:6px; font-size:12px; font-weight:700; color:var(--navy); cursor:pointer;">
          <input type="checkbox" id="chkRememberDefaultCounty" checked style="accent-color:var(--blue); width:15px; height:15px;" />
          <span>記住此設定，下次開啟直接載入</span>
        </label>
        <div style="display:flex; gap:8px;">
          <button type="button" class="btn" onclick="skipDefaultCountyModal()">稍後再選</button>
          <button type="button" class="btn btn-primary" onclick="confirmDefaultCounty()" style="padding:7px 14px; font-weight:800;">
            ✅ 確認並開始巡訪
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Modal 4: 洽談階段自訂管理（常駐選項） -->
  <div class="modal-overlay" id="modalStageManager" style="z-index: 2200;">
    <div class="modal-card" style="max-width: 440px;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; border-bottom:1.5px solid var(--border); padding-bottom:10px;">
        <div>
          <div style="font-size:11px; font-weight:800; color:var(--blue); text-transform:uppercase; letter-spacing:0.05em;">外勤流程設定</div>
          <h3 style="margin:2px 0 0 0; font-size:16px; color:var(--navy); font-weight:900;">🎯 自訂洽談階段（常駐選項）</h3>
        </div>
        <button type="button" class="btn" onclick="closeStageManagerModal()" style="padding:4px 8px; font-size:14px;">✕</button>
      </div>

      <div style="font-size:12px; color:var(--text-muted); margin-bottom:12px; line-height:1.4;">
        自訂符合您公司業務銷售流程的洽談階段，新增後將<strong>永久常駐於拜訪紀錄選單</strong>中，全台 18 縣市 72 大園區皆可即選即用。
      </div>

      <!-- Add New Custom Stage Form -->
      <div style="display:flex; gap:6px; margin-bottom:14px;">
        <input type="text" id="newStageInput" placeholder="輸入自訂階段名稱（例如：送樣測試中）" style="flex:1; padding:7px 10px; border:1px solid var(--border); border-radius:6px; font-size:12.5px;" onkeydown="if(event.key==='Enter'){event.preventDefault();addNewCustomStage();}" />
        <button type="button" class="btn btn-primary" onclick="addNewCustomStage()" style="padding:7px 14px; font-size:12px; white-space:nowrap; font-weight:800;">
          ➕ 加入常駐
        </button>
      </div>

      <!-- List of Currently Active Stages -->
      <div style="font-weight:800; font-size:12px; color:var(--navy); margin-bottom:6px; display:flex; justify-content:space-between; align-items:center;">
        <span>現有常駐階段清單</span>
        <button type="button" onclick="resetDefaultStages()" style="background:none; border:none; color:var(--text-muted); font-size:11px; cursor:pointer; text-decoration:underline;">恢復系統預設</button>
      </div>

      <div id="stageListContainer" style="max-height: 220px; overflow-y: auto; display:flex; flex-direction:column; gap:6px; margin-bottom:16px; border:1px solid var(--border); border-radius:6px; padding:8px; background:#FAFAF8;">
        <!-- Dynamically rendered stages -->
      </div>

      <div style="display:flex; justify-content:flex-end;">
        <button type="button" class="btn btn-primary" onclick="closeStageManagerModal()" style="padding:7px 16px; font-size:12.5px; font-weight:800;">
          ✓ 完成並儲存
        </button>
      </div>
    </div>
  </div>

  <!-- Toast Notification Element -->
  <div class="toast-notice" id="toastNotice"></div>

  <!-- Leaflet JS -->
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
  
  <script>
    // --- 全台 18 縣市完整工業與科技園區資料庫 ---
    const DATABASE_BUNDLE = __DATABASE_BUNDLE_PLACEHOLDER__;
    const COUNTIES = DATABASE_BUNDLE.counties;
    const PARKS = DATABASE_BUNDLE.parks;

    // 嚴格依循：西部 (北到南) -> 東部 (北到南) 的地理順序
    const WEST_COUNTY_KEYS = [
      "keelung", "taipei", "newtaipei", "taoyuan", "hsinchu_city",
      "hsinchu_county", "miaoli", "taichung", "changhua", "nantou",
      "yunlin", "chiayi", "tainan", "kaohsiung", "pingtung"
    ];
    const EAST_COUNTY_KEYS = ["yilan", "hualien", "taitung"];

    // State Variables - 支援個人化常駐預設縣市
    const DEFAULT_COUNTY_KEY = "sales_map_default_county";
    const DEFAULT_PROMPTED_KEY = "sales_map_default_county_prompted";
    let modalSelectedCounty = "taoyuan";
    let currentCounty = "taoyuan";
    let currentPark = "zhongli";
    let clients = [];
    let activeIndustry = "ALL";
    let activeRoad = "ALL";
    let activeStatus = "ALL";
    let searchQuery = "";
    let map = null;
    let markers = {};
    let userLocationMarker = null;
    let currentFiltered = [];
    let displayedCount = 60;
    let searchDebounceTimer = null;
    let markerDebounceTimer = null;
    let currentMobileView = "split"; // "list", "split", "map"

    // --- 洽談階段 / 進度 自訂常駐管理 (Sales Stage Manager CRM) ---
    const DEFAULT_STAGES = [
      "初次接洽 · 建立關係",
      "確認規格需求 · 評估中",
      "樣品測試中 · 送件評估",
      "已提報價單 · 議價審核",
      "成交簽約 · 正式下單 🎉",
      "定期維護 · 售後關懷",
      "暫無需求 · 暫緩後續追蹤"
    ];

    const STAGE_STORAGE_KEY = "sales_custom_stages_v2";
    let customStagesList = [];
    let previousSelectedOutcome = "確認規格需求 · 評估中";

    function loadCustomStages() {
      try {
        const saved = localStorage.getItem(STAGE_STORAGE_KEY);
        if (saved) {
          const parsed = JSON.parse(saved);
          if (Array.isArray(parsed) && parsed.length > 0) {
            customStagesList = parsed;
            return;
          }
        }
      } catch (e) {
        console.error("Failed to load custom stages", e);
      }
      customStagesList = [...DEFAULT_STAGES];
    }

    function saveCustomStages() {
      try {
        localStorage.setItem(STAGE_STORAGE_KEY, JSON.stringify(customStagesList));
      } catch (e) {
        console.error("Failed to save custom stages", e);
      }
      populateStageOptions();
    }

    function populateStageOptions(selectTargetStage) {
      const select = document.getElementById('logOutcome');
      if (!select) return;

      const currentVal = selectTargetStage || select.value || previousSelectedOutcome;
      select.innerHTML = '';

      customStagesList.forEach(st => {
        const opt = document.createElement('option');
        opt.value = st;
        opt.textContent = st;
        if (st === currentVal) opt.selected = true;
        select.appendChild(opt);
      });

      // Add Manage Option at the bottom
      const manageOpt = document.createElement('option');
      manageOpt.value = '__MANAGE_STAGES__';
      manageOpt.textContent = '⚙️ ＋ 自訂/新增常駐階段...';
      manageOpt.style.fontWeight = 'bold';
      manageOpt.style.color = '#1A4DA1';
      select.appendChild(manageOpt);

      if (!select.value && select.options.length > 0) {
        select.selectedIndex = 0;
      }
      previousSelectedOutcome = select.value;
    }

    window.openStageManagerModal = function() {
      renderStageList();
      const modal = document.getElementById('modalStageManager');
      if (modal) modal.classList.add('open');
      const input = document.getElementById('newStageInput');
      if (input) {
        input.value = '';
        setTimeout(() => input.focus(), 150);
      }
    };

    window.closeStageManagerModal = function() {
      const modal = document.getElementById('modalStageManager');
      if (modal) modal.classList.remove('open');
      populateStageOptions();
    };

    function renderStageList() {
      const container = document.getElementById('stageListContainer');
      if (!container) return;
      container.innerHTML = '';

      if (customStagesList.length === 0) {
        container.innerHTML = '<div style="font-size:12px; color:var(--text-muted); text-align:center; padding:12px;">目前無任何自訂階段</div>';
        return;
      }

      customStagesList.forEach((st, idx) => {
        const row = document.createElement('div');
        row.style.cssText = 'display:flex; justify-content:space-between; align-items:center; background:#FFFFFF; border:1px solid #E2E8F0; padding:6px 10px; border-radius:6px; font-size:12px;';
        row.innerHTML = `
          <div style="font-weight:700; color:var(--navy); display:flex; align-items:center; gap:6px;">
            <span style="color:var(--blue); font-size:11px;">#${idx + 1}</span>
            <span>${st}</span>
          </div>
          <button type="button" onclick="deleteCustomStage(${idx})" title="刪除此階段" style="background:none; border:none; color:#EF4444; font-size:13px; cursor:pointer; padding:2px 5px; border-radius:4px;">
            🗑️
          </button>
        `;
        container.appendChild(row);
      });
    }

    window.addNewCustomStage = function() {
      const input = document.getElementById('newStageInput');
      if (!input) return;
      const val = input.value.trim();
      if (!val) {
        alert("請輸入階段名稱！");
        return;
      }
      if (customStagesList.includes(val)) {
        alert("此階段名稱已存在！");
        return;
      }
      customStagesList.push(val);
      saveCustomStages();
      renderStageList();
      input.value = '';
      populateStageOptions(val);
    };

    window.deleteCustomStage = function(idx) {
      if (customStagesList.length <= 1) {
        alert("請至少保留一個洽談階段！");
        return;
      }
      const item = customStagesList[idx];
      if (confirm(`確定要移除「${item}」常駐階段嗎？`)) {
        customStagesList.splice(idx, 1);
        saveCustomStages();
        renderStageList();
      }
    };

    window.resetDefaultStages = function() {
      if (confirm("確定要恢復原廠預設的洽談階段選項嗎？")) {
        customStagesList = [...DEFAULT_STAGES];
        saveCustomStages();
        renderStageList();
      }
    };

    window.handleOutcomeSelectChange = function(selectEl) {
      if (selectEl.value === '__MANAGE_STAGES__') {
        openStageManagerModal();
        selectEl.value = previousSelectedOutcome || (customStagesList[0] || '初次接洽');
      } else {
        previousSelectedOutcome = selectEl.value;
      }
    };

    // --- RWD Mobile Filter Chips Collapsible ---
    window.toggleMobileFilters = function() {
      const section = document.getElementById('collapsibleFilterSection');
      const textSpan = document.getElementById('filtersToggleText');
      if (!section) return;
      const isCollapsed = section.classList.toggle('collapsed');
      if (textSpan) {
        textSpan.innerText = isCollapsed ? '▼ 展開篩選' : '▲ 收合篩選';
      }
    };

    // --- RWD Mobile View Switcher ---
    window.setMobileView = function(mode) {
      currentMobileView = mode;
      const appContainer = document.getElementById('appContainer');
      appContainer.classList.remove('mobile-list', 'mobile-map', 'mobile-split');
      appContainer.classList.add(`mobile-${mode}`);

      document.querySelectorAll('#mobileViewToggle .view-btn').forEach(btn => btn.classList.remove('active'));
      if (mode === 'list') document.getElementById('btnViewList').classList.add('active');
      else if (mode === 'split') document.getElementById('btnViewSplit').classList.add('active');
      else if (mode === 'map') document.getElementById('btnViewMap').classList.add('active');

      if (map) {
        setTimeout(() => { map.invalidateSize(); }, 200);
      }
    };

    // Helper: Get localStorage key for a specific park
    function getParkStorageKey(pid) {
      if (pid === "zhongli") return "sales_visit_clients_v744";
      return `sales_visit_clients_${pid}`;
    }

    // Load persisted park status/notes/visit_logs from localStorage
    function getPersistedParkClients(pid) {
      const parkCfg = PARKS[pid];
      if (!parkCfg || !parkCfg.clients) return [];
      
      const storageKey = getParkStorageKey(pid);
      const stored = localStorage.getItem(storageKey);
      if (!stored) {
        return parkCfg.clients.map(c => ({ ...c, park_id: pid, county_id: parkCfg.county_id, visit_logs: c.visit_logs || [] }));
      }

      try {
        const storedList = JSON.parse(stored);
        const mapById = {};
        storedList.forEach(item => {
          mapById[item.id] = {
            status: item.status,
            notes: item.notes,
            visit_logs: item.visit_logs || []
          };
        });

        return parkCfg.clients.map(c => {
          if (mapById[c.id]) {
            return {
              ...c,
              park_id: pid,
              county_id: parkCfg.county_id,
              status: mapById[c.id].status,
              notes: mapById[c.id].notes,
              visit_logs: mapById[c.id].visit_logs || []
            };
          }
          return { ...c, park_id: pid, county_id: parkCfg.county_id, visit_logs: c.visit_logs || [] };
        });
      } catch (e) {
        return parkCfg.clients.map(c => ({ ...c, park_id: pid, county_id: parkCfg.county_id, visit_logs: c.visit_logs || [] }));
      }
    }

    // Save client changes back to appropriate park's localStorage
    function saveCurrentParkData() {
      if (currentPark.startsWith("all_") || currentPark === "all_taiwan") {
        const grouped = {};
        clients.forEach(c => {
          const pid = c.park_id || currentPark;
          if (!grouped[pid]) grouped[pid] = [];
          grouped[pid].push(c);
        });
        Object.keys(grouped).forEach(pid => {
          localStorage.setItem(getParkStorageKey(pid), JSON.stringify(grouped[pid]));
        });
      } else {
        localStorage.setItem(getParkStorageKey(currentPark), JSON.stringify(clients));
      }
    }

    // 18 縣市依地理動線排列（基隆至屏東，再至宜蘭、花蓮、台東）
    const ALL_COUNTY_KEYS = [
      "keelung", "taipei", "newtaipei", "taoyuan", "hsinchu_city",
      "hsinchu_county", "miaoli", "taichung", "changhua", "nantou",
      "yunlin", "chiayi", "tainan", "kaohsiung", "pingtung",
      "yilan", "hualien", "taitung"
    ];

    // --- 預設常駐縣市設定 (First-Visit & Default County Setting) ---
    function showToast(msg) {
      let toast = document.getElementById('toastNotice');
      if (!toast) {
        toast = document.createElement('div');
        toast.id = 'toastNotice';
        toast.className = 'toast-notice';
        document.body.appendChild(toast);
      }
      toast.innerHTML = msg;
      toast.classList.add('show');
      if (window._toastTimer) clearTimeout(window._toastTimer);
      window._toastTimer = setTimeout(() => {
        toast.classList.remove('show');
      }, 2600);
    }

    function updateDefaultCountyHeaderUI(cid) {
      const label = document.getElementById('headerDefaultCountyLabel');
      if (!label) return;
      if (cid === 'all') {
        label.innerText = '全台';
      } else if (COUNTIES[cid]) {
        label.innerText = COUNTIES[cid].name;
      } else {
        label.innerText = '未設定';
      }
    }

    window.openDefaultCountyModal = function(isFirstVisit = false) {
      const modal = document.getElementById('modalDefaultCounty');
      if (!modal) return;

      const saved = localStorage.getItem(DEFAULT_COUNTY_KEY) || currentCounty || "taoyuan";
      modalSelectedCounty = saved;

      const titleEl = document.getElementById('defaultModalTitle');
      const subtitleEl = document.getElementById('defaultModalSubtitle');
      if (isFirstVisit) {
        if (titleEl) titleEl.innerText = "請問您最常巡訪的「預設常駐縣市」是？";
        if (subtitleEl) subtitleEl.innerText = "日後開啟巡訪地圖時，將優先自動為您載入該縣市與園區。（隨時可在上方隨選切換其他縣市）";
      } else {
        if (titleEl) titleEl.innerText = "變更「預設常駐縣市」";
        if (subtitleEl) subtitleEl.innerText = "請選擇日後開啟網站時優先載入的預設縣市：";
      }

      renderDefaultCountyCards();
      updateSelectedCountyPreview();
      modal.classList.add('open');
    };

    window.closeDefaultCountyModal = function() {
      const modal = document.getElementById('modalDefaultCounty');
      if (modal) modal.classList.remove('open');
    };

    window.selectDefaultCountyInModal = function(cid) {
      modalSelectedCounty = cid;
      renderDefaultCountyCards();
      updateSelectedCountyPreview();
    };

    window.confirmDefaultCounty = function() {
      const remember = document.getElementById('chkRememberDefaultCounty')?.checked ?? true;
      if (remember) {
        localStorage.setItem(DEFAULT_COUNTY_KEY, modalSelectedCounty);
        localStorage.setItem(DEFAULT_PROMPTED_KEY, "true");
      }
      switchCounty(modalSelectedCounty);
      updateDefaultCountyHeaderUI(modalSelectedCounty);
      renderCountyNavBar();
      closeDefaultCountyModal();

      const cname = modalSelectedCounty === 'all' ? '全台 72 大園區' : (COUNTIES[modalSelectedCounty]?.name || '所選縣市');
      showToast(`⭐ 已成功將【${cname}】設為預設開啟縣市！`);
    };

    window.skipDefaultCountyModal = function() {
      localStorage.setItem(DEFAULT_PROMPTED_KEY, "true");
      closeDefaultCountyModal();
      showToast("💡 您可隨時點擊頂部【⭐ 預設】按鈕重新設定常駐縣市！");
    };

    function renderDefaultCountyCards() {
      const grid = document.getElementById('defaultCountyGrid');
      if (grid) {
        grid.innerHTML = "";
        ALL_COUNTY_KEYS.forEach(cid => {
          if (!COUNTIES[cid]) return;
          const c = COUNTIES[cid];
          const count = (c.parks || []).reduce((s, pid) => s + (PARKS[pid] ? PARKS[pid].clients.length : 0), 0);
          const card = document.createElement('div');
          card.className = `county-select-card ${modalSelectedCounty === cid ? 'selected' : ''}`;
          card.onclick = () => selectDefaultCountyInModal(cid);
          card.ondblclick = () => { selectDefaultCountyInModal(cid); confirmDefaultCounty(); };
          card.innerHTML = `
            <div class="card-head">
              <span class="card-name">${c.icon} ${c.name}</span>
              <span class="card-check">✓</span>
            </div>
            <div class="card-meta">${(c.parks || []).length} 園區 · ${count.toLocaleString()} 家廠商</div>
          `;
          grid.appendChild(card);
        });
      }

      const allGrid = document.getElementById('defaultCountyGridAll');
      if (allGrid) {
        allGrid.innerHTML = "";
        const allTaiwanTotal = Object.values(PARKS).reduce((sum, p) => sum + p.clients.length, 0);
        const card = document.createElement('div');
        card.className = `county-select-card ${modalSelectedCounty === 'all' ? 'selected' : ''}`;
        card.onclick = () => selectDefaultCountyInModal('all');
        card.ondblclick = () => { selectDefaultCountyInModal('all'); confirmDefaultCounty(); };
        card.innerHTML = `
          <div class="card-head">
            <span class="card-name">🌐 全台 72 大園區總覽</span>
            <span class="card-check">✓</span>
          </div>
          <div class="card-meta">18 縣市 · ${allTaiwanTotal.toLocaleString()} 家廠商</div>
        `;
        allGrid.appendChild(card);
      }
    }

    function updateSelectedCountyPreview() {
      const textEl = document.getElementById('selectedCountyPreviewText');
      if (!textEl) return;
      if (modalSelectedCounty === 'all') {
        const allTaiwanTotal = Object.values(PARKS).reduce((sum, p) => sum + p.clients.length, 0);
        textEl.innerText = `🌐 全台 72 大園區 (共 18 縣市 · ${allTaiwanTotal.toLocaleString()} 家廠商)`;
      } else if (COUNTIES[modalSelectedCounty]) {
        const c = COUNTIES[modalSelectedCounty];
        const count = (c.parks || []).reduce((s, pid) => s + (PARKS[pid] ? PARKS[pid].clients.length : 0), 0);
        textEl.innerText = `${c.icon} ${c.name} (共 ${(c.parks || []).length} 大園區 · ${count.toLocaleString()} 家廠商)`;
      }
    }

    // --- Render County Navigation (Tier 1: 18 縣市依序排列，無文字標籤干擾) ---
    function renderCountyNavBar() {
      const nav = document.getElementById('countyNavBar');
      nav.innerHTML = "";
      const savedDefault = localStorage.getItem(DEFAULT_COUNTY_KEY) || "";

      ALL_COUNTY_KEYS.forEach(cid => {
        if (!COUNTIES[cid]) return;
        const cinfo = COUNTIES[cid];
        const parkIds = cinfo.parks || [];
        const totalCount = parkIds.reduce((sum, pid) => sum + (PARKS[pid] ? PARKS[pid].clients.length : 0), 0);
        const isDefault = (cid === savedDefault);

        const btn = document.createElement('button');
        btn.className = `county-pill ${cid === currentCounty ? 'active' : ''}`;
        btn.setAttribute('data-county', cid);
        btn.innerHTML = `
          <span>${cinfo.icon} ${cinfo.name}</span>
          <span class="county-pill-count">${totalCount.toLocaleString()}</span>
          ${isDefault ? '<span class="default-pill-badge" title="您的預設常駐縣市">⭐預設</span>' : ''}
        `;
        btn.onclick = () => switchCounty(cid);
        nav.appendChild(btn);
      });

      // 全台總覽前分隔線
      const sep = document.createElement('div');
      sep.className = 'region-separator';
      nav.appendChild(sep);

      const allTaiwanTotal = Object.values(PARKS).reduce((sum, p) => sum + p.clients.length, 0);
      const isAllDefault = (savedDefault === 'all');
      const allBtn = document.createElement('button');
      allBtn.className = `county-pill ${currentCounty === 'all' ? 'active' : ''}`;
      allBtn.setAttribute('data-county', 'all');
      allBtn.innerHTML = `
        <span>🌐 全台 72 大園區</span>
        <span class="county-pill-count">${allTaiwanTotal.toLocaleString()}</span>
        ${isAllDefault ? '<span class="default-pill-badge" title="您的預設常駐縣市">⭐預設</span>' : ''}
      `;
      allBtn.onclick = () => switchCounty('all');
      nav.appendChild(allBtn);
    }

    // --- Render Park Navigation (Tier 2: 當前縣市所屬各大園區) ---
    function renderParkNavBar() {
      const nav = document.getElementById('parkNavBar');
      nav.innerHTML = "";

      let parksToShow = [];
      let overviewPillTitle = "";
      let overviewPillId = "";
      let overviewCount = 0;

      if (currentCounty === 'all') {
        parksToShow = Object.keys(PARKS);
        overviewPillTitle = "🌐 全台 72 大園區總覽";
        overviewPillId = "all_taiwan";
        overviewCount = parksToShow.reduce((s, pid) => s + PARKS[pid].clients.length, 0);
      } else {
        const cinfo = COUNTIES[currentCounty];
        parksToShow = cinfo.parks || [];
        overviewPillTitle = `🌐 全${cinfo.name} ${parksToShow.length} 大園區總覽`;
        overviewPillId = `all_${currentCounty}`;
        overviewCount = parksToShow.reduce((s, pid) => s + (PARKS[pid] ? PARKS[pid].clients.length : 0), 0);
      }

      parksToShow.forEach(pid => {
        const pcfg = PARKS[pid];
        if (!pcfg) return;

        const btn = document.createElement('button');
        btn.className = `park-pill ${pid === currentPark ? 'active' : ''}`;
        btn.setAttribute('data-park', pid);
        btn.innerHTML = `
          <span>📍 ${pcfg.name}</span>
          <span class="park-pill-count">${pcfg.clients.length} 家</span>
        `;
        btn.onclick = () => switchPark(pid);
        nav.appendChild(btn);
      });

      // Add County Overview Pill
      const ovBtn = document.createElement('button');
      ovBtn.className = `park-pill ${currentPark === overviewPillId ? 'active' : ''}`;
      ovBtn.setAttribute('data-park', overviewPillId);
      ovBtn.innerHTML = `
        <span>${overviewPillTitle}</span>
        <span class="park-pill-count">${overviewCount.toLocaleString()} 家</span>
      `;
      ovBtn.onclick = () => switchPark(overviewPillId);
      nav.appendChild(ovBtn);
    }

    // --- Switch County ---
    window.switchCounty = function(cid) {
      currentCounty = cid;
      renderCountyNavBar();

      let targetPark = "";
      if (cid === 'all') {
        targetPark = "all_taiwan";
      } else {
        targetPark = COUNTIES[cid].default_park || COUNTIES[cid].parks[0];
      }

      renderParkNavBar();
      switchPark(targetPark);
    };

    // --- Switch Park ---
    window.switchPark = function(parkId, newSearchTerm) {
      currentPark = parkId;

      document.querySelectorAll('#parkNavBar .park-pill').forEach(pill => {
        if (pill.getAttribute('data-park') === parkId) {
          pill.classList.add('active');
          pill.scrollIntoView({ behavior: 'smooth', inline: 'center' });
        } else {
          pill.classList.remove('active');
        }
      });

      if (newSearchTerm !== undefined) {
        const input = document.getElementById('searchInput');
        input.value = newSearchTerm;
        searchQuery = newSearchTerm;
        const clearBtn = document.getElementById('btnClearSearch');
        if (clearBtn) clearBtn.style.display = newSearchTerm ? 'block' : 'none';
      }

      loadParkData(parkId);
    };

    // Load Data for current park
    function loadParkData(parkId) {
      let baseClients = [];

      if (parkId === "all_taiwan") {
        baseClients = [];
        Object.keys(PARKS).forEach(pid => {
          baseClients = baseClients.concat(getPersistedParkClients(pid));
        });
        document.getElementById('headerTitle').innerText = '全台科技＆產業園區地圖 · 18 縣市 72 大園區總覽';
        document.getElementById('headerSubtitle').innerText = `全台合計 ${baseClients.length.toLocaleString()} 家廠商巡訪指南`;
      } else if (parkId.startsWith("all_")) {
        const cid = parkId.replace("all_", "");
        const cinfo = COUNTIES[cid];
        baseClients = [];
        (cinfo.parks || []).forEach(pid => {
          baseClients = baseClients.concat(getPersistedParkClients(pid));
        });
        document.getElementById('headerTitle').innerText = `全台科技＆產業園區地圖 · ${cinfo.name}總覽`;
        document.getElementById('headerSubtitle').innerText = `${cinfo.name} ${cinfo.parks.length} 大園區合計 ${baseClients.length.toLocaleString()} 家廠商巡訪指南`;
      } else {
        baseClients = getPersistedParkClients(parkId);
        const pcfg = PARKS[parkId];
        const countyName = COUNTIES[pcfg.county_id] ? COUNTIES[pcfg.county_id].name : '';
        document.getElementById('headerTitle').innerText = `全台科技＆產業園區地圖 · ${pcfg.name}`;
        document.getElementById('headerSubtitle').innerText = `${countyName} · ${pcfg.name} · ${pcfg.clients.length} 家廠商全區地圖（支援上市櫃、產業、同路巡訪快篩）`;
      }

      clients = baseClients;

      // Reset filters when switching park
      activeIndustry = "ALL";
      activeRoad = "ALL";
      activeStatus = "ALL";
      
      setupIndustryChips();
      setupRoadChips();
      updateBadgeCounts();

      // Pan/fly map smoothly
      if (map) {
        if (parkId === "all_taiwan") {
          map.flyTo([23.8, 120.9], 8, { duration: 1.2 });
        } else if (parkId.startsWith("all_")) {
          const cid = parkId.replace("all_", "");
          const firstParkId = COUNTIES[cid].parks[0];
          const pcenter = (PARKS[firstParkId] && PARKS[firstParkId].center) || [24.0, 121.0];
          map.flyTo(pcenter, 12, { duration: 1 });
        } else {
          const pcfg = PARKS[parkId];
          if (pcfg && pcfg.center) {
            map.flyTo(pcfg.center, pcfg.zoom || 15, { duration: 1 });
          }
        }
      }

      renderList();
    }

    // --- 地圖放大自動顯現廠家名稱標籤 (Auto POI Labels on Zoom) ---
    let autoLabelsEnabled = true;

    window.updateMapLabelVisibility = function() {
      if (!map) return;
      const currentZoom = map.getZoom();
      const mapEl = document.getElementById('map');
      if (!mapEl) return;
      if (autoLabelsEnabled) {
        mapEl.classList.toggle('show-auto-labels', currentZoom >= 16);
        mapEl.classList.toggle('show-detailed-labels', currentZoom >= 17.5);
      } else {
        mapEl.classList.remove('show-auto-labels', 'show-detailed-labels');
      }
    };

    window.toggleAutoLabels = function() {
      autoLabelsEnabled = !autoLabelsEnabled;
      const btn = document.getElementById('btnToggleLabels');
      if (btn) {
        if (autoLabelsEnabled) {
          btn.innerHTML = '🏷️ 廠名: 自動';
          btn.classList.add('active-state');
        } else {
          btn.innerHTML = '🏷️ 廠名: 關閉';
          btn.classList.remove('active-state');
        }
      }
      updateMapLabelVisibility();
    };

    // --- Initialize Leaflet Map ---
    function initMap() {
      map = L.map('map', {
        zoomControl: true,
        attributionControl: false
      }).setView([25.0880, 121.7010], 15);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19
      }).addTo(map);

      L.control.attribution({ position: 'bottomright' })
        .addAttribution('&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>')
        .addTo(map);

      map.on('zoomend', updateMapLabelVisibility);
      map.on('zoom', updateMapLabelVisibility);
      map.on('moveend', updateMapLabelVisibility);
    }

    // --- Debounced Marker Rendering for 60fps Performance ---
    function updateMarkersDebounced(filteredClients) {
      clearTimeout(markerDebounceTimer);
      markerDebounceTimer = setTimeout(() => {
        updateMarkers(filteredClients);
      }, 90);
    }

    function updateMarkers(filteredClients) {
      // Clear existing markers
      Object.values(markers).forEach(m => map.removeLayer(m));
      markers = {};

      const bounds = L.latLngBounds();

      filteredClients.forEach(c => {
        let markerClass = "marker-pending";
        if (c.status === "已拜訪") markerClass = "marker-done";
        else if (c.status === "洽談中") markerClass = "marker-negotiating";
        else if (c.is_listed === "是") markerClass = "marker-listed";

        const iconHtml = `<div class="custom-marker ${markerClass}" style="width:26px;height:26px;">${c.is_listed === '是' ? '★' : '●'}</div>`;
        const customIcon = L.divIcon({
          html: iconHtml,
          className: '',
          iconSize: [26, 26],
          iconAnchor: [13, 13],
          popupAnchor: [0, -13]
        });

        const marker = L.marker([c.lat, c.lng], { icon: customIcon }).addTo(map);

        const isDone = c.status === '已拜訪';
        const logCount = (c.visit_logs && c.visit_logs.length) || 0;
        const parkName = (c.park_id && PARKS[c.park_id]) ? PARKS[c.park_id].name : '';

        // 廠家自動標籤（地圖放大至街道級別時自動顯現，免點選直接閱讀廠商名稱與重點資訊）
        let statusBadge = '';
        let statusTooltipClass = '';
        if (c.status === '已拜訪') {
          statusBadge = '<span class="lbl-badge-done">✅已訪</span>';
          statusTooltipClass = 'status-done';
        } else if (c.status === '洽談中') {
          statusBadge = '<span class="lbl-badge-neg">💬洽談</span>';
          statusTooltipClass = 'status-negotiating';
        } else if (c.is_listed === '是') {
          statusTooltipClass = 'status-listed';
        }

        const tooltipContent = `
          <div class="lbl-title">
            <span>${c.name}</span>
            ${c.is_listed === '是' ? '<span class="lbl-star">⭐上市</span>' : ''}
            ${statusBadge}
          </div>
          <div class="lbl-detail">
            <span>📍 ${c.road}</span>
            <span>·</span>
            <span>${c.industry}</span>
          </div>
        `;

        marker.bindTooltip(tooltipContent, {
          permanent: true,
          direction: 'top',
          offset: [0, -14],
          className: `marker-auto-tooltip ${statusTooltipClass}`,
          interactive: true
        });

        marker.on('tooltipopen', (e) => {
          if (e.tooltip && e.tooltip._container) {
            e.tooltip._container.onclick = (ev) => {
              ev.stopPropagation();
              marker.openPopup();
              highlightClientCard(c.id);
            };
          }
        });

        const popupContent = `
          <div style="font-family:'Noto Sans TC',sans-serif; min-width:230px; padding:2px;">
            <div style="font-weight:800; font-size:14px; color:#16213A; margin-bottom:3px; line-height:1.3;">
              ${c.name}
            </div>
            <div style="font-size:11px; color:#68717F; margin-bottom:6px;">
              ${c.address}
            </div>
            <div style="display:flex; gap:5px; align-items:center; margin-bottom:8px; flex-wrap:wrap;">
              ${parkName ? `<span style="font-size:10.5px; font-weight:800; color:#16213A; background:#E5E7EB; padding:1px 5px; border-radius:4px;">${parkName}</span>` : ''}
              <span style="font-size:11px; font-weight:700; color:#1A4DA1; background:#EEF3FC; padding:2px 6px; border-radius:4px;">${c.road}</span>
              <span style="font-size:11px; color:#68717F;">${c.industry}</span>
            </div>
            ${c.notes ? `<div style="font-size:11px; background:#F8FAFC; border:1px solid #E2E8F0; padding:4px 6px; border-radius:4px; margin-bottom:8px; color:#334155;">📝 <strong>備忘：</strong>${c.notes}</div>` : ''}
            <div style="display:flex; gap:5px; align-items:center; padding-top:8px; border-top:1px dashed #E6E3DB;">
              <button onclick="quickToggleVisit(${c.id})" 
                      style="flex:1; border:1px solid ${isDone ? '#2E8540' : '#1A4DA1'}; background:${isDone ? '#EBF7EE' : '#1A4DA1'}; color:${isDone ? '#2E8540' : '#FFFFFF'}; padding:6px 6px; border-radius:6px; font-weight:800; font-size:11px; cursor:pointer; display:inline-flex; align-items:center; justify-content:center; gap:2px;">
                ${isDone ? '✅ 已拜訪' : '✓ 標記已訪'}
              </button>
              <button onclick="openVisitLogModal(${c.id})" 
                      style="background:#FFFFFF; border:1px solid #16213A; color:#16213A; padding:6px 8px; border-radius:6px; font-weight:700; font-size:11px; cursor:pointer; white-space:nowrap;">
                📋 紀錄${logCount > 0 ? ` (${logCount})` : ''}
              </button>
              <a href="https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(c.address)}" 
                 target="_blank" 
                 style="font-size:11px; background:#E0622B; color:#fff; text-decoration:none; padding:6px 8px; border-radius:6px; font-weight:800; white-space:nowrap;">
                 🚗 導航
              </a>
            </div>
          </div>
        `;
        marker.bindPopup(popupContent);

        marker.on('click', () => {
          highlightClientCard(c.id);
        });

        markers[c.id] = marker;
        bounds.extend([c.lat, c.lng]);
      });

      // Fit map if moderate number of markers
      if (filteredClients.length > 0 && bounds.isValid() && filteredClients.length <= 150) {
        map.fitBounds(bounds, { padding: [50, 50], maxZoom: 16 });
      }

      // 每次更新標記後同步刷新標籤可視性
      updateMapLabelVisibility();
    }

    // --- Search & Multi-Dimensional Filtering Logic (嚴格局限於當前所選園區/縣市) ---
    function executeFilter() {
      const q = (searchQuery || "").trim().toLowerCase();
      const keywords = q ? q.split(/\\s+/).filter(Boolean) : [];

      currentFiltered = clients.filter(c => {
        // 1. Search Query Match
        if (keywords.length > 0) {
          const logTexts = (c.visit_logs || []).map(l => `${l.contact || ''} ${l.summary || ''} ${l.outcome || ''} ${l.next_action || ''}`).join(' ');
          const targetStr = `${c.name || ''} ${c.address || ''} ${c.road || ''} ${c.industry || ''} ${c.contact || ''} ${c.phone || ''} ${c.notes || ''} ${logTexts}`.toLowerCase();
          const matchAll = keywords.every(kw => targetStr.includes(kw));
          if (!matchAll) return false;
        }

        // 2. Road Filter
        if (activeRoad !== "ALL" && c.road !== activeRoad) return false;

        // 3. Industry Filter
        if (activeIndustry !== "ALL" && c.industry !== activeIndustry) return false;

        // 4. Status Filter
        if (activeStatus === "LISTED" && c.is_listed !== "是") return false;
        if (activeStatus !== "ALL" && activeStatus !== "LISTED" && c.status !== activeStatus) return false;

        return true;
      });

      return currentFiltered;
    }

    function renderList() {
      executeFilter();

      // Update Header Count Text & Mobile Toggle Counter
      document.getElementById('resultCountText').innerText = `顯示 ${currentFiltered.length} / ${clients.length} 家廠商`;
      const mobileCounter = document.getElementById('mobileCount');
      if (mobileCounter) mobileCounter.innerText = currentFiltered.length;
      updateBadgeCounts();

      // Update Map Pins with Debounce
      updateMarkersDebounced(currentFiltered);

      // Reset card display count and render
      displayedCount = 60;
      renderCardsSlice(true);
    }

    function renderCardsSlice(isReset) {
      const container = document.getElementById('clientList');
      if (isReset) {
        container.innerHTML = "";
      }

      const existingHint = document.getElementById('loadMoreHint');
      if (existingHint) existingHint.remove();

      // Visited Summary Banner
      if (isReset && activeStatus === "已拜訪") {
        const totalLogs = currentFiltered.reduce((sum, c) => sum + ((c.visit_logs && c.visit_logs.length) || 0), 0);
        const visitedBanner = document.createElement('div');
        visitedBanner.style.cssText = "background:#ECFDF5; border:1.5px solid #A7F3D0; border-radius:8px; padding:10px 14px; margin-bottom:8px; font-size:12.5px; color:#065F46;";
        visitedBanner.innerHTML = `
          <div style="font-weight:900; font-size:13px; display:flex; justify-content:space-between; align-items:center;">
            <span>✅ 已拜訪廠商清單 (${currentFiltered.length} 家)</span>
            <span style="background:#D1FAE5; padding:2px 8px; border-radius:999px; font-size:11px;">累計拜訪紀錄：${totalLogs} 筆</span>
          </div>
          <div style="font-size:11.5px; color:#047857; margin-top:3px;">
            每家卡片皆可查看「最新洽談進度」與「下次待辦事項」，點擊「📋 拜訪紀錄」可隨時追加或檢閱歷史訪談歷程！
          </div>
        `;
        container.appendChild(visitedBanner);
      }

      // Zero Results Handling (無跨縣市干擾，乾淨聚焦在當前園區)
      if (currentFiltered.length === 0) {
        const q = (searchQuery || "").trim();
        let noticeHtml = '';

        if (q) {
          const keywords = q.toLowerCase().split(/\\s+/).filter(Boolean);
          const relaxedMatches = clients.filter(c => {
            const str = `${c.name || ''} ${c.address || ''} ${c.road || ''} ${c.industry || ''} ${c.contact || ''} ${c.phone || ''} ${c.notes || ''}`.toLowerCase();
            return keywords.every(kw => str.includes(kw));
          });

          if (relaxedMatches.length > 0 && (activeRoad !== 'ALL' || activeIndustry !== 'ALL' || activeStatus !== 'ALL')) {
            noticeHtml = `
              <div style="background:#FFFBEB; border:1px solid #FCD34D; padding:12px; border-radius:8px; margin-bottom:12px; text-align:left; font-size:12.5px; color:#92400E;">
                💡 <strong>提示：</strong>目前已啟用【${activeRoad !== 'ALL' ? activeRoad : ''} ${activeIndustry !== 'ALL' ? activeIndustry : ''} ${activeStatus !== 'ALL' ? activeStatus : ''}】篩選條件。<br>
                在當前園區中共找到 <strong>${relaxedMatches.length}</strong> 家廠商符合「${q}」！<br>
                <button onclick="clearAllFiltersAndSearch()" class="btn btn-primary" style="margin-top:8px; font-size:12px; padding:4px 10px;">
                  🔓 解除標籤限制，顯示這 ${relaxedMatches.length} 家
                </button>
              </div>
            `;
          }
        }

        const emptyTip = activeStatus === "已拜訪" 
          ? "目前尚無標記為「已拜訪」的廠商。<br>在廠商卡片點擊「✓ 標記為已拜訪」或「📋 拜訪紀錄」即可開始填寫訪談進度！"
          : "請檢查關鍵字是否有錯字，或點擊上方「重設篩選」";

        container.innerHTML += `
          <div style="text-align:center; padding:30px 16px; color:#6B7280;">
            ${noticeHtml}
            <div style="font-size:32px; margin-bottom:8px;">${activeStatus === "已拜訪" ? "📋" : "🔍"}</div>
            <div style="font-weight:700; font-size:15px; color:var(--navy);">${activeStatus === "已拜訪" ? "尚無已拜訪紀錄" : "找不到符合條件的廠商"}</div>
            <div style="font-size:12px; margin-top:4px; line-height:1.5;">${emptyTip}</div>
          </div>
        `;
        return;
      }

      const startIndex = isReset ? 0 : container.querySelectorAll('.client-card').length;
      const endIndex = Math.min(displayedCount, currentFiltered.length);

      for (let i = startIndex; i < endIndex; i++) {
        const c = currentFiltered[i];
        const card = document.createElement('div');
        card.className = "client-card";
        card.id = `card-${c.id}`;

        let statusClass = "status-pending";
        if (c.status === "已拜訪") statusClass = "status-done";
        else if (c.status === "洽談中") statusClass = "status-negotiating";

        const logs = c.visit_logs || [];
        const latestLog = logs.length > 0 ? logs[0] : null;

        let visitLogBoxHtml = "";
        if (latestLog) {
          visitLogBoxHtml = `
            <div class="card-visit-box" onclick="openVisitLogModal(${c.id}, event)" title="點擊檢視或新增歷史拜訪紀錄">
              <div class="card-visit-header">
                <span>📅 最近拜訪：${latestLog.date ? latestLog.date.replace('T', ' ') : ''} · ${latestLog.contact || '洽談'}</span>
                <span class="badge-outcome">${latestLog.outcome || '已拜訪'}</span>
              </div>
              <div class="card-visit-summary">
                💬 <strong>內容：</strong>${latestLog.summary}
              </div>
              ${latestLog.next_action ? `<div class="card-visit-next">⏰ <strong>下次待辦：</strong>${latestLog.next_action}</div>` : ''}
            </div>
          `;
        }

        const parkName = (c.park_id && PARKS[c.park_id]) ? PARKS[c.park_id].name : '';

        card.innerHTML = `
          <div class="card-top">
            <div class="card-title">${c.name}</div>
            ${c.is_listed === '是' ? '<span class="badge-listed">★ 上市櫃</span>' : ''}
          </div>

          <div class="card-address">
            ${parkName && (currentPark.startsWith('all_') || currentPark === 'all_taiwan') ? `<span style="font-size:10.5px; font-weight:800; color:#1F2937; background:#E5E7EB; padding:1px 5px; border-radius:4px;">${parkName}</span>` : ''}
            <span class="card-road">${c.road}</span>
            <span>${c.address}</span>
          </div>

          <div class="card-meta">
            <span>👤 ${c.contact || '總機/廠務'}</span>
            ${c.phone ? `<span>📞 <a href="tel:${c.phone}">${c.phone}</a></span>` : ''}
            <span class="badge-industry">${c.industry}</span>
          </div>

          ${c.notes && !latestLog ? `
            <div class="card-notes" title="點擊卡片可查看地圖位置">
              📝 <strong>備忘：</strong><span id="note-text-${c.id}">${c.notes}</span>
            </div>
          ` : ''}

          ${visitLogBoxHtml}

          <div class="card-actions">
            <div>
              <select class="status-select ${statusClass}" onchange="changeClientStatus(${c.id}, this.value, event)">
                <option value="尚未拜訪" ${(c.status === '尚未拜訪' || c.status === '待拜訪') ? 'selected' : ''}>⏳ 尚未拜訪</option>
                <option value="洽談中" ${c.status === '洽談中' ? 'selected' : ''}>💬 洽談中</option>
                <option value="已拜訪" ${c.status === '已拜訪' ? 'selected' : ''}>✅ 已拜訪</option>
              </select>
            </div>

            <div style="display:flex; gap:5px;">
              <button class="btn-log ${logs.length > 0 ? 'has-logs' : ''}" onclick="openVisitLogModal(${c.id}, event)" title="開啟並填寫拜訪紀錄">
                📋 拜訪紀錄${logs.length > 0 ? ` (${logs.length})` : ''}
              </button>
              <a href="https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(c.address)}" 
                 target="_blank" 
                 class="nav-btn" 
                 onclick="event.stopPropagation();" 
                 title="開啓 Google Maps 導航">
                🚗 導航
              </a>
            </div>
          </div>
        `;

        card.addEventListener('click', () => {
          focusOnClient(c);
        });

        container.appendChild(card);
      }

      // Show lazy load indicator if more available
      if (displayedCount < currentFiltered.length) {
        const hint = document.createElement('div');
        hint.id = 'loadMoreHint';
        hint.style.cssText = "text-align:center; padding:12px; font-size:12px; color:#6B7280; font-weight:700;";
        hint.innerText = `已顯示前 ${endIndex} 家 (共 ${currentFiltered.length} 家) · 向下滾動載入更多...`;
        container.appendChild(hint);
      }
    }

    // --- Card & Map Interaction ---
    function focusOnClient(c) {
      highlightClientCard(c.id);

      // 手機版若在名單全螢幕模式，自動切換至分割模式以便看到地圖
      if (window.innerWidth <= 768 && currentMobileView === 'list') {
        setMobileView('split');
      }

      if (markers[c.id]) {
        map.flyTo([c.lat, c.lng], 17, { duration: 1 });
        markers[c.id].openPopup();
      }
    }

    function highlightClientCard(id) {
      document.querySelectorAll('.client-card').forEach(el => el.classList.remove('active'));
      const targetCard = document.getElementById(`card-${id}`);
      if (targetCard) {
        targetCard.classList.add('active');
        targetCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }

    // --- Update Status & Notes ---
    window.quickToggleVisit = function(id) {
      const client = clients.find(c => c.id === id);
      if (client) {
        const wasDone = client.status === '已拜訪';
        client.status = wasDone ? '尚未拜訪' : '已拜訪';
        saveCurrentParkData();
        renderList();
        if (markers[id]) {
          markers[id].openPopup();
        }

        if (!wasDone) {
          openVisitLogModal(id);
        }
      }
    };

    window.changeClientStatus = function(id, newStatus, event) {
      if (event) event.stopPropagation();
      const client = clients.find(c => c.id === id);
      if (client) {
        client.status = newStatus;
        saveCurrentParkData();
        renderList();
        if (newStatus === "已拜訪") {
          openVisitLogModal(id);
        }
      }
    };

    // --- Visit Log Modal Logic ---
    window.openVisitLogModal = function(id, event) {
      if (event) event.stopPropagation();
      const client = clients.find(c => c.id === id);
      if (!client) return;

      document.getElementById('visitLogClientId').value = client.id;
      document.getElementById('visitModalTitle').innerText = client.name;
      document.getElementById('visitModalSubtitle').innerText = `📍 ${client.road} · ${client.address}`;
      
      const now = new Date();
      const localTime = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
      document.getElementById('logDate').value = localTime;
      document.getElementById('logContact').value = client.contact || '';
      document.getElementById('logSummary').value = '';
      document.getElementById('logNextAction').value = '';

      populateStageOptions();
      renderVisitHistoryTimeline(client);

      const modal = document.getElementById('modalVisitLog');
      modal.classList.add('open');
    };

    function renderVisitHistoryTimeline(client) {
      const logs = client.visit_logs || [];
      document.getElementById('logHistoryCount').innerText = logs.length;
      const historyContainer = document.getElementById('logHistoryList');
      historyContainer.innerHTML = "";

      if (logs.length === 0) {
        historyContainer.innerHTML = `
          <div style="text-align:center; padding:16px; color:#9CA3AF; font-size:12px; background:#F9FAFB; border-radius:6px;">
            尚無歷史拜訪紀錄。請在上方填寫本次洽談重點並點擊「儲存本次紀錄」！
          </div>
        `;
        return;
      }

      logs.forEach((item, idx) => {
        const itemCard = document.createElement('div');
        itemCard.className = 'timeline-card';
        itemCard.innerHTML = `
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
            <div style="font-size:12px; font-weight:800; color:var(--navy);">
              📅 ${item.date ? item.date.replace('T', ' ') : ''} · 👤 ${item.contact || '現場窗口'}
            </div>
            <div style="display:flex; gap:6px; align-items:center;">
              <span class="badge-outcome">${item.outcome || '洽談紀錄'}</span>
              <button onclick="deleteVisitLog(${client.id}, '${item.id}')" style="background:none; border:none; color:#EF4444; font-size:11px; cursor:pointer;" title="刪除此筆紀錄">🗑️</button>
            </div>
          </div>
          <div style="font-size:12px; color:#374151; line-height:1.4; white-space:pre-wrap; margin-bottom:4px;">
            ${item.summary}
          </div>
          ${item.next_action ? `
            <div style="font-size:11px; color:#059669; font-weight:700;">
              ⏰ 下次待辦：${item.next_action}
            </div>
          ` : ''}
        `;
        historyContainer.appendChild(itemCard);
      });
    }

    window.deleteVisitLog = function(clientId, logId) {
      const client = clients.find(c => c.id === clientId);
      if (!client || !confirm("確定要刪除這筆拜訪紀錄嗎？")) return;

      client.visit_logs = (client.visit_logs || []).filter(l => String(l.id) !== String(logId));
      if (client.visit_logs.length > 0) {
        client.notes = client.visit_logs[0].summary;
      } else {
        client.notes = "";
      }
      saveCurrentParkData();
      renderVisitHistoryTimeline(client);
      renderList();
    };

    function updateBadgeCounts() {
      document.getElementById('countAll').innerText = clients.length;
      const listedCount = clients.filter(c => c.is_listed === '是').length;
      document.getElementById('countListed').innerText = `${listedCount}`;
      document.getElementById('countPending').innerText = clients.filter(c => c.status === '尚未拜訪' || c.status === '待拜訪').length;
      document.getElementById('countNegotiating').innerText = clients.filter(c => c.status === '洽談中').length;
      document.getElementById('countDone').innerText = clients.filter(c => c.status === '已拜訪').length;
    }

    // --- Dynamic Industry Chips ---
    function setupIndustryChips() {
      const indMap = {};
      clients.forEach(c => {
        const ind = c.industry || "其他製造及服務業";
        indMap[ind] = (indMap[ind] || 0) + 1;
      });

      const sortedInds = Object.keys(indMap).sort((a, b) => indMap[b] - indMap[a]);
      const container = document.getElementById('industryChips');
      container.innerHTML = "";

      const allBtn = document.createElement('button');
      allBtn.className = `chip ${activeIndustry === 'ALL' ? 'active' : ''}`;
      allBtn.innerText = `全部產業 (${clients.length})`;
      allBtn.onclick = () => {
        activeIndustry = 'ALL';
        document.querySelectorAll('#industryChips .chip').forEach(b => b.classList.remove('active'));
        allBtn.classList.add('active');
        document.getElementById('indCurrentLabel').innerText = '全部產業';
        renderList();
      };
      container.appendChild(allBtn);

      sortedInds.forEach(ind => {
        const btn = document.createElement('button');
        btn.className = `chip ${activeIndustry === ind ? 'active' : ''}`;
        btn.innerText = `${ind} (${indMap[ind]})`;
        btn.onclick = () => {
          activeIndustry = ind;
          document.querySelectorAll('#industryChips .chip').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          document.getElementById('indCurrentLabel').innerText = ind;
          renderList();
        };
        container.appendChild(btn);
      });
    }

    // --- Dynamic Road Chips ---
    function setupRoadChips() {
      const roadMap = {};
      clients.forEach(c => {
        if (c.road) {
          roadMap[c.road] = (roadMap[c.road] || 0) + 1;
        }
      });

      const sortedRoads = Object.keys(roadMap).sort((a, b) => roadMap[b] - roadMap[a]);
      const roadContainer = document.getElementById('roadChips');
      roadContainer.innerHTML = "";

      const allBtn = document.createElement('button');
      allBtn.className = `chip ${activeRoad === 'ALL' ? 'active' : ''}`;
      allBtn.innerText = `全部路段 (${clients.length})`;
      allBtn.onclick = () => {
        activeRoad = 'ALL';
        document.querySelectorAll('#roadChips .chip').forEach(c => c.classList.remove('active'));
        allBtn.classList.add('active');
        document.getElementById('roadCurrentLabel').innerText = '全部路段';
        renderList();
      };
      roadContainer.appendChild(allBtn);

      sortedRoads.forEach(r => {
        const btn = document.createElement('button');
        btn.className = `chip ${activeRoad === r ? 'active' : ''}`;
        btn.innerText = `${r} (${roadMap[r]})`;
        btn.onclick = () => {
          activeRoad = r;
          document.querySelectorAll('#roadChips .chip').forEach(c => c.classList.remove('active'));
          btn.classList.add('active');
          document.getElementById('roadCurrentLabel').innerText = r;
          renderList();
        };
        roadContainer.appendChild(btn);
      });
    }

    window.clearAllFiltersAndSearch = function() {
      activeRoad = 'ALL';
      activeIndustry = 'ALL';
      activeStatus = 'ALL';
      setupRoadChips();
      setupIndustryChips();
      document.querySelectorAll('#statusChips .chip-status').forEach(b => b.className = "chip chip-status");
      document.querySelector('[data-status="ALL"]').classList.add('active-all');
      renderList();
    };

    // --- Event Listeners Initialization ---
    document.addEventListener("DOMContentLoaded", () => {
      initMap();
      loadCustomStages();
      populateStageOptions();

      // 檢查是否已設定預設常駐縣市
      const savedDefault = localStorage.getItem(DEFAULT_COUNTY_KEY);
      const hasPrompted = localStorage.getItem(DEFAULT_PROMPTED_KEY);

      if (savedDefault && (COUNTIES[savedDefault] || savedDefault === 'all')) {
        currentCounty = savedDefault;
      } else {
        // 尚未設定：預設以桃園市為啟始背景
        currentCounty = "taoyuan";
      }

      updateDefaultCountyHeaderUI(savedDefault || "taoyuan");
      renderCountyNavBar();
      renderParkNavBar();
      switchCounty(currentCounty);

      // 手機端視圖初始化：若寬度小於 768px 預設為上下分割
      if (window.innerWidth <= 768) {
        setMobileView("split");
      }

      // 若為第一次造訪（未設定預設縣市且尚未詢問過），主動彈出詢問視窗
      if (!savedDefault && !hasPrompted) {
        setTimeout(() => {
          openDefaultCountyModal(true);
        }, 350);
      }

      // 監聽螢幕旋轉與縮放 (Orientation & Resize)
      window.addEventListener('resize', () => {
        if (map) {
          map.invalidateSize();
        }
      });

      // Infinite scroll listener for client list
      const clientListContainer = document.getElementById('clientList');
      clientListContainer.addEventListener('scroll', () => {
        if (clientListContainer.scrollTop + clientListContainer.clientHeight >= clientListContainer.scrollHeight - 160) {
          if (displayedCount < currentFiltered.length) {
            displayedCount += 60;
            renderCardsSlice(false);
          }
        }
      });

      // Search Input Handling
      const searchInput = document.getElementById('searchInput');
      const clearBtn = document.getElementById('btnClearSearch');
      const searchBtn = document.getElementById('btnDoSearch');

      function triggerSearch() {
        searchQuery = searchInput.value.trim();
        clearBtn.style.display = searchQuery ? 'block' : 'none';
        renderList();
      }

      searchInput.addEventListener('input', () => {
        clearTimeout(searchDebounceTimer);
        searchDebounceTimer = setTimeout(triggerSearch, 100);
      });

      searchInput.addEventListener('compositionend', () => {
        clearTimeout(searchDebounceTimer);
        triggerSearch();
      });

      searchInput.addEventListener('change', () => {
        clearTimeout(searchDebounceTimer);
        triggerSearch();
      });

      searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          clearTimeout(searchDebounceTimer);
          triggerSearch();
        }
      });

      if (searchBtn) {
        searchBtn.addEventListener('click', (e) => {
          e.preventDefault();
          clearTimeout(searchDebounceTimer);
          triggerSearch();
        });
      }

      if (clearBtn) {
        clearBtn.addEventListener('click', (e) => {
          e.preventDefault();
          searchInput.value = '';
          searchQuery = '';
          clearBtn.style.display = 'none';
          renderList();
          searchInput.focus();
        });
      }

      // Status Filter Chips
      document.querySelectorAll('#statusChips .chip-status').forEach(btn => {
        btn.addEventListener('click', () => {
          document.querySelectorAll('#statusChips .chip-status').forEach(b => {
            b.className = "chip chip-status";
          });
          const status = btn.getAttribute('data-status');
          activeStatus = status;

          if (status === "ALL") btn.classList.add('active-all');
          else if (status === "LISTED") btn.classList.add('active-listed');
          else if (status === "尚未拜訪" || status === "待拜訪") btn.classList.add('active-pending');
          else if (status === "洽談中") btn.classList.add('active-negotiating');
          else if (status === "已拜訪") btn.classList.add('active-done');

          renderList();
        });
      });

      // Reset Filter Button
      document.getElementById('btnResetFilter').addEventListener('click', () => {
        searchQuery = "";
        searchInput.value = "";
        clearBtn.style.display = 'none';
        activeIndustry = "ALL";
        activeRoad = "ALL";
        activeStatus = "ALL";
        setupIndustryChips();
        setupRoadChips();
        document.querySelectorAll('#statusChips .chip-status').forEach(b => b.className = "chip chip-status");
        document.querySelector('[data-status="ALL"]').classList.add('active-all');
        renderList();
      });

      // Form Add Visit Log Submission
      document.getElementById('formAddVisitLog').addEventListener('submit', (e) => {
        e.preventDefault();
        const clientId = parseInt(document.getElementById('visitLogClientId').value, 10);
        const client = clients.find(c => c.id === clientId);
        if (!client) return;

        const newLog = {
          id: 'v_' + Date.now(),
          date: document.getElementById('logDate').value,
          contact: document.getElementById('logContact').value.trim(),
          outcome: document.getElementById('logOutcome').value,
          next_action: document.getElementById('logNextAction').value.trim(),
          summary: document.getElementById('logSummary').value.trim(),
          created_at: Date.now()
        };

        if (!client.visit_logs) client.visit_logs = [];
        client.visit_logs.unshift(newLog);

        client.notes = newLog.summary;

        if (document.getElementById('logAutoSetDone').checked) {
          client.status = "已拜訪";
        }

        saveCurrentParkData();
        renderVisitHistoryTimeline(client);
        renderList();

        document.getElementById('logSummary').value = '';
        document.getElementById('logNextAction').value = '';
        alert("✅ 拜訪紀錄已成功儲存！");
      });

      document.getElementById('btnCloseVisitModal').addEventListener('click', () => {
        document.getElementById('modalVisitLog').classList.remove('open');
      });

      // Locate User GPS
      document.getElementById('btnLocateMe').addEventListener('click', () => {
        if (!navigator.geolocation) {
          alert("您的設備或瀏覽器不支援 GPS 定位");
          return;
        }

        const btn = document.getElementById('btnLocateMe');
        btn.innerText = "⏳ 定位中...";

        navigator.geolocation.getCurrentPosition(
          (pos) => {
            btn.innerText = "🎯 我的位置";
            const lat = pos.coords.latitude;
            const lng = pos.coords.longitude;

            if (userLocationMarker) {
              map.removeLayer(userLocationMarker);
            }

            const meIcon = L.divIcon({
              html: `<div style="background:#2563EB; width:20px; height:20px; border-radius:50%; border:3px solid #FFF; box-shadow:0 0 0 8px rgba(37,99,235,0.25);"></div>`,
              className: '',
              iconSize: [20, 20],
              iconAnchor: [10, 10]
            });

            userLocationMarker = L.marker([lat, lng], { icon: meIcon }).addTo(map);
            userLocationMarker.bindPopup("<b>📍 您的目前位置</b>").openPopup();
            
            // 手機版若在地圖全關模式，自動切換至地圖或分割模式
            if (window.innerWidth <= 768 && currentMobileView === 'list') {
              setMobileView('map');
            }

            map.flyTo([lat, lng], 16);
          },
          (err) => {
            btn.innerText = "🎯 我的位置";
            alert("無法取得 GPS 定位，請確認手機已允許瀏覽器定位權限。");
          },
          { enableHighAccuracy: true, timeout: 8000 }
        );
      });

      // Fit bounds
      document.getElementById('btnFitBounds').addEventListener('click', () => {
        const bounds = L.latLngBounds(clients.map(c => [c.lat, c.lng]));
        if (bounds.isValid()) {
          map.fitBounds(bounds, { padding: [50, 50] });
        }
      });

      // Export CSV (含縣市、園區、外勤拜訪紀錄與下次待辦，繁體中文欄位表頭)
      document.getElementById('btnExport').addEventListener('click', () => {
        let csvContent = "\\uFEFF客戶編號,縣市,工業或科技園區,公司名稱,所在路段,完整廠址,緯度(Lat),經度(Lng),產業類別,是否上市櫃,拜訪狀態,聯絡窗口,聯絡電話,拜訪備忘與筆記,累計拜訪次數,最新拜訪日期,最新接洽對象,最新洽談階段,最新洽談重點,下次預計待辦事項與回訪日\\n";
        clients.forEach(c => {
          const logs = c.visit_logs || [];
          const latest = logs.length > 0 ? logs[0] : {};
          const pcfg = (c.park_id && PARKS[c.park_id]) ? PARKS[c.park_id] : {};
          const cinfo = (pcfg.county_id && COUNTIES[pcfg.county_id]) ? COUNTIES[pcfg.county_id] : {};
          const row = [
            c.id,
            `"${(cinfo.name || c.county_id || '').replace(/"/g, '""')}"`,
            `"${(pcfg.name || c.park_id || '').replace(/"/g, '""')}"`,
            `"${(c.name || '').replace(/"/g, '""')}"`,
            `"${(c.road || '').replace(/"/g, '""')}"`,
            `"${(c.address || '').replace(/"/g, '""')}"`,
            c.lat,
            c.lng,
            `"${(c.industry || '').replace(/"/g, '""')}"`,
            c.is_listed || "否",
            `"${(c.status || '尚未拜訪')}"`,
            `"${(c.contact || '').replace(/"/g, '""')}"`,
            `"${(c.phone || '').replace(/"/g, '""')}"`,
            `"${(c.notes || '').replace(/"/g, '""')}"`,
            logs.length,
            `"${(latest.date || '').replace('T', ' ')}"`,
            `"${(latest.contact || '').replace(/"/g, '""')}"`,
            `"${(latest.outcome || '').replace(/"/g, '""')}"`,
            `"${(latest.summary || '').replace(/"/g, '""')}"`,
            `"${(latest.next_action || '').replace(/"/g, '""')}"`
          ].join(",");
          csvContent += row + "\\n";
        });

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        const parkName = PARKS[currentPark] ? PARKS[currentPark].name : currentPark;
        a.download = `全台科技園區_${parkName}_業務拜訪與洽談紀錄_${new Date().toISOString().slice(0,10)}.csv`;
        a.click();
        URL.revokeObjectURL(url);
      });

      // Import CSV
      const fileInput = document.getElementById('fileInput');
      document.getElementById('btnImport').addEventListener('click', () => {
        fileInput.click();
      });

      fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (evt) => {
          const text = evt.target.result;
          parseAndImportCSV(text);
        };
        reader.readAsText(file);
      });

      // Modal Add Client
      const modal = document.getElementById('modalAdd');
      document.getElementById('btnAddClient').addEventListener('click', () => {
        modal.classList.add('open');
      });
      document.getElementById('btnCloseModal').addEventListener('click', () => {
        modal.classList.remove('open');
      });

      // Modal Backdrop Click Closes
      document.getElementById('modalDefaultCounty')?.addEventListener('click', (e) => {
        if (e.target.id === 'modalDefaultCounty') {
          closeDefaultCountyModal();
        }
      });
      document.getElementById('modalStageManager')?.addEventListener('click', (e) => {
        if (e.target.id === 'modalStageManager') {
          closeStageManagerModal();
        }
      });
      document.getElementById('modalVisitLog')?.addEventListener('click', (e) => {
        if (e.target.id === 'modalVisitLog') {
          document.getElementById('modalVisitLog').classList.remove('open');
        }
      });

      document.getElementById('formAddClient').addEventListener('submit', (e) => {
        e.preventDefault();
        const center = (PARKS[currentPark] && PARKS[currentPark].center) || [25.0880, 121.7010];
        const newClient = {
          id: Date.now(),
          park_id: currentPark,
          county_id: currentCounty,
          name: document.getElementById('addName').value.trim(),
          road: document.getElementById('addRoad').value.trim(),
          address: document.getElementById('addAddress').value.trim(),
          lat: parseFloat(document.getElementById('addLat').value) || center[0],
          lng: parseFloat(document.getElementById('addLng').value) || center[1],
          industry: "自建客戶",
          is_listed: document.getElementById('addListed').value,
          status: "尚未拜訪",
          contact: document.getElementById('addContact').value.trim(),
          phone: document.getElementById('addPhone').value.trim(),
          notes: document.getElementById('addNotes').value.trim(),
          visit_logs: []
        };

        clients.unshift(newClient);
        saveCurrentParkData();
        setupRoadChips();
        renderList();
        modal.classList.remove('open');
        document.getElementById('formAddClient').reset();
        focusOnClient(newClient);
      });
    });

    // Helper: Parse CSV (支援中文欄位與英文欄位雙向相容、引號與 BOM 解析)
    function parseAndImportCSV(csvText) {
      const lines = csvText.split(/\\r?\\n/).filter(line => line.trim() !== "");
      if (lines.length <= 1) {
        alert("CSV 內容為空或格式不符");
        return;
      }

      function parseCSVLine(line) {
        const result = [];
        let cur = '';
        let inQuotes = false;
        for (let i = 0; i < line.length; i++) {
          const char = line[i];
          if (char === '"') {
            if (inQuotes && line[i + 1] === '"') {
              cur += '"';
              i++;
            } else {
              inQuotes = !inQuotes;
            }
          } else if (char === ',' && !inQuotes) {
            result.push(cur.trim());
            cur = '';
          } else {
            cur += char;
          }
        }
        result.push(cur.trim());
        return result;
      }

      const headers = parseCSVLine(lines[0].replace(/^\\uFEFF/, '')).map(h => h.trim().replace(/^"|"$/g, ''));
      const colMap = {};
      headers.forEach((h, idx) => {
        colMap[h] = idx;
      });

      const getVal = (row, ...keys) => {
        for (const k of keys) {
          if (colMap[k] !== undefined && row[colMap[k]] !== undefined) {
            return row[colMap[k]];
          }
        }
        return '';
      };

      const imported = [];

      for (let i = 1; i < lines.length; i++) {
        const row = parseCSVLine(lines[i]);
        if (row.length < 3) continue;

        const name = getVal(row, '公司名稱', 'name') || (row.length > 3 ? row[3] : row[1]) || `客戶 ${i}`;
        const road = getVal(row, '所在路段', 'road') || (row.length > 4 ? row[4] : row[2]) || '園區內';
        const address = getVal(row, '完整廠址', 'address') || (row.length > 5 ? row[5] : row[3]) || '';
        const latVal = parseFloat(getVal(row, '緯度(Lat)', 'lat') || (row.length > 6 ? row[6] : row[4]));
        const lngVal = parseFloat(getVal(row, '經度(Lng)', 'lng') || (row.length > 7 ? row[7] : row[5]));
        const industry = getVal(row, '產業類別', 'industry') || (row.length > 8 ? row[8] : row[6]) || '其他';
        const is_listed = getVal(row, '是否上市櫃', 'is_listed') || (row.length > 9 ? row[9] : row[7]) || '否';
        const status = getVal(row, '拜訪狀態', 'status') || (row.length > 10 ? row[10] : row[8]) || '尚未拜訪';
        const contact = getVal(row, '聯絡窗口', 'contact') || (row.length > 11 ? row[11] : row[9]) || '';
        const phone = getVal(row, '聯絡電話', 'phone') || (row.length > 12 ? row[12] : row[10]) || '';
        const notes = getVal(row, '拜訪備忘與筆記', 'notes') || (row.length > 13 ? row[13] : row[11]) || '';

        imported.push({
          id: Date.now() + i,
          park_id: currentPark,
          county_id: currentCounty,
          name: name,
          road: road,
          address: address,
          lat: !isNaN(latVal) && latVal > 0 ? latVal : (PARKS[currentPark] ? PARKS[currentPark].lat : 24.97),
          lng: !isNaN(lngVal) && lngVal > 0 ? lngVal : (PARKS[currentPark] ? PARKS[currentPark].lng : 121.23),
          industry: industry,
          is_listed: is_listed,
          status: status,
          contact: contact,
          phone: phone,
          notes: notes,
          visit_logs: []
        });
      }

      if (imported.length > 0) {
        if (confirm(`成功解析出 ${imported.length} 筆客戶名單！是否要覆蓋目前名單？（選取消則為追加名單）`)) {
          clients = imported;
        } else {
          clients = [...imported, ...clients];
        }
        saveCurrentParkData();
        setupRoadChips();
        renderList();
        alert("名單匯入成功！");
      } else {
        alert("解析 CSV 失敗，請確認欄位格式是否包含公司名稱、地址等欄位。");
      }
    }
  </script>
</body>
</html>
'''

full_html = html_template.replace('__DATABASE_BUNDLE_PLACEHOLDER__', database_json)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(full_html)

print(f"[OK] 成功編譯生成 index.html！檔案大小：{len(full_html.encode('utf-8')):,} bytes")

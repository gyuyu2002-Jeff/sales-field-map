# -*- coding: utf-8 -*-
import json

# 1. Load all parks data
with open('all_taoyuan_parks.json', 'r', encoding='utf-8') as f:
    all_parks = json.load(f)

# Serialize to compact JSON for inlining
all_parks_json = json.dumps(all_parks, ensure_ascii=False)

html_template = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>桃園外勤巡訪地圖總中樞 - 7大工業區 1,874家廠商巡訪指南</title>
  
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
    }

    .brand-title {
      font-family: 'Noto Serif TC', serif;
      font-size: 18px;
      font-weight: 900;
      color: var(--navy);
      line-height: 1.2;
    }

    .brand-subtitle {
      font-size: 11.5px;
      color: var(--text-muted);
      letter-spacing: 0.03em;
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 8px;
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

    /* Park Navigation Bar (橫向捲動切換各大工業區) */
    .park-nav-bar {
      background: #F4F2EC;
      border-bottom: 1.5px solid var(--border);
      padding: 6px 16px;
      overflow-x: auto;
      white-space: nowrap;
      display: flex;
      gap: 8px;
      z-index: 900;
      scrollbar-width: thin;
      flex-shrink: 0;
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
      padding: 6px 12px;
      border-radius: 999px;
      font-size: 12.5px;
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
      background: var(--navy);
      border-color: var(--navy);
      color: #FFFFFF;
      box-shadow: 0 2px 8px rgba(22, 33, 58, 0.25);
    }

    .park-pill-count {
      font-size: 11px;
      padding: 1px 6px;
      border-radius: 999px;
      background: #E8E5DC;
      color: var(--navy);
      font-weight: 800;
    }

    .park-pill.active .park-pill-count {
      background: rgba(255, 255, 255, 0.25);
      color: #FFFFFF;
    }

    /* Main Container (Split Screen) */
    .app-container {
      display: flex;
      flex: 1;
      height: calc(100vh - 105px);
      position: relative;
      overflow: hidden;
    }

    /* Sidebar (Client Cards & Filtering) */
    .sidebar {
      width: 450px;
      background: var(--bg-primary);
      border-right: 1.5px solid var(--border);
      display: flex;
      flex-direction: column;
      z-index: 500;
      flex-shrink: 0;
      box-shadow: 2px 0 12px rgba(22, 33, 58, 0.04);
    }

    .sidebar-controls {
      padding: 12px 16px;
      background: #FFFFFF;
      border-bottom: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      gap: 9px;
    }

    /* Search Box with Clear Button & Explicit Search Button */
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
      gap: 4px;
    }

    .chips-label {
      font-size: 11px;
      font-weight: 700;
      color: var(--text-muted);
      letter-spacing: 0.04em;
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
    }

    .chips-scroll::-webkit-scrollbar {
      height: 3px;
    }
    .chips-scroll::-webkit-scrollbar-thumb {
      background: #DDD;
      border-radius: 2px;
    }

    .chip {
      padding: 3.5px 9px;
      font-size: 11.5px;
      font-weight: 700;
      background: #F1EFE7;
      color: var(--navy);
      border-radius: 999px;
      border: 1px solid transparent;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.15s;
    }

    .chip:hover {
      background: #E6E3D8;
    }

    .chip.active {
      background: var(--navy);
      color: #FFFFFF;
      border-color: var(--navy);
    }

    .status-chips-scroll {
      display: flex;
      gap: 5px;
      overflow-x: auto;
      padding-bottom: 2px;
    }

    .chip-status.active-all { background: var(--navy); color: #fff; }
    .chip-status.active-listed { background: var(--accent-orange); color: #fff; }
    .chip-status.active-pending { background: var(--blue); color: #fff; }
    .chip-status.active-negotiating { background: var(--accent-purple); color: #fff; }
    .chip-status.active-done { background: var(--accent-green); color: #fff; }

    /* Result Count Header */
    .client-list-header {
      padding: 8px 16px;
      background: #F9F8F5;
      border-bottom: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 12px;
      font-weight: 700;
      color: var(--text-muted);
      flex-shrink: 0;
    }

    /* Client Cards List (Scrollable) */
    .client-list {
      flex: 1;
      overflow-y: auto;
      padding: 10px 14px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .client-card {
      background: var(--card-bg);
      border: 1.5px solid var(--border);
      border-radius: 10px;
      padding: 12px 14px;
      cursor: pointer;
      transition: all 0.15s ease;
      position: relative;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .client-card:hover {
      border-color: var(--blue);
      box-shadow: 0 4px 12px rgba(26, 77, 161, 0.08);
      transform: translateY(-1px);
    }

    .client-card.active {
      border-color: var(--blue);
      background: var(--blue-subtle);
      box-shadow: 0 0 0 2px var(--blue);
    }

    .card-top {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 8px;
    }

    .card-title {
      font-size: 14.5px;
      font-weight: 800;
      color: var(--navy);
      line-height: 1.3;
    }

    .badge-listed {
      background: #FEF3C7;
      color: #92400E;
      font-size: 10.5px;
      font-weight: 900;
      padding: 2px 6px;
      border-radius: 4px;
      border: 1px solid #FCD34D;
      white-space: nowrap;
      flex-shrink: 0;
    }

    .badge-industry {
      font-size: 10.5px;
      color: var(--navy-light);
      background: #EDEAE1;
      padding: 2px 7px;
      border-radius: 4px;
      display: inline-block;
      white-space: nowrap;
    }

    .card-address {
      font-size: 12px;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 5px;
    }

    .card-road {
      font-weight: 700;
      color: var(--blue);
      background: #EEF3FC;
      padding: 1px 5px;
      border-radius: 3px;
    }

    .card-meta {
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 11.5px;
      color: #4B5563;
      padding-top: 4px;
      border-top: 1px dashed var(--border);
    }

    .card-meta a {
      color: var(--blue);
      text-decoration: none;
      font-weight: 700;
    }

    .card-notes {
      font-size: 11px;
      background: #FAF9F5;
      padding: 5px 8px;
      border-radius: 5px;
      color: #4B5563;
      border: 1px solid #EFECE6;
      line-height: 1.4;
    }

    .card-actions {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
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
    }

    .map-tool-btn:hover {
      background: #FAFAF7;
      border-color: var(--navy);
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
      max-width: 520px;
      width: 100%;
      padding: 24px;
      box-shadow: 0 20px 40px rgba(0,0,0,0.2);
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

    @media (max-width: 860px) {
      .app-container {
        flex-direction: column;
        height: calc(100vh - 100px);
      }

      .sidebar {
        width: 100%;
        height: 54%;
        order: 2;
        border-right: none;
        border-top: 2px solid var(--border);
      }

      #map {
        height: 46%;
        order: 1;
      }

      header {
        padding: 8px 12px;
      }

      .brand-title {
        font-size: 16px;
      }

      .btn {
        padding: 5px 8px;
        font-size: 11.5px;
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
        <div class="brand-title" id="headerTitle">桃園外勤巡訪地圖總中樞</div>
        <div class="brand-subtitle" id="headerSubtitle">全桃 7 大工業區 · 1,874 家全區廠商巡訪指南</div>
      </div>
    </div>

    <div class="header-actions">
      <button class="btn" id="btnExport" title="匯出當前拜訪狀態為 CSV 檔">
        📤 匯出記錄
      </button>
      <button class="btn" id="btnImport" title="匯入客製化客戶名單 CSV">
        📥 匯入名單
      </button>
      <button class="btn btn-primary" id="btnAddClient">
        ➕ 新增客戶
      </button>
      <input type="file" id="fileInput" accept=".csv" style="display: none;" />
    </div>
  </header>

  <!-- Top Park Navigation Bar (各大工業區一鍵切換) -->
  <nav class="park-nav-bar" id="parkNavBar">
    <button class="park-pill active" data-park="zhongli">
      <span>📍 中壢產業園區</span>
      <span class="park-pill-count">744 家</span>
    </button>
    <button class="park-pill" data-park="guishan">
      <span>📍 龜山產業園區</span>
      <span class="park-pill-count">220 家</span>
    </button>
    <button class="park-pill" data-park="huaya">
      <span>📍 華亞科技園區</span>
      <span class="park-pill-count">100 家</span>
    </button>
    <button class="park-pill" data-park="pingzhen">
      <span>📍 平鎮產業園區</span>
      <span class="park-pill-count">120 家</span>
    </button>
    <button class="park-pill" data-park="guanyin">
      <span>📍 觀音產業園區</span>
      <span class="park-pill-count">350 家</span>
    </button>
    <button class="park-pill" data-park="dayuan">
      <span>📍 大園產業園區</span>
      <span class="park-pill-count">230 家</span>
    </button>
    <button class="park-pill" data-park="youshi">
      <span>📍 幼獅產業園區</span>
      <span class="park-pill-count">110 家</span>
    </button>
    <button class="park-pill" data-park="all">
      <span>🌐 全桃 7 大園區總覽</span>
      <span class="park-pill-count">1,874 家</span>
    </button>
  </nav>

  <!-- Main Split Container -->
  <div class="app-container">
    
    <!-- Sidebar: Search & Client Cards -->
    <aside class="sidebar">
      
      <div class="sidebar-controls">
        <!-- Search bar with Clear & Search buttons -->
        <div class="search-row">
          <div class="search-input-wrapper">
            <span class="search-icon-left">🔍</span>
            <input type="text" id="searchInput" placeholder="搜尋公司名稱、地址、聯絡人、路名..." autocomplete="off" />
            <button id="btnClearSearch" class="search-clear-btn" title="清除搜尋字詞">✕</button>
          </div>
          <button id="btnDoSearch" class="btn btn-primary" style="padding: 7px 12px;">搜尋</button>
        </div>

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
      <button class="map-tool-btn" id="btnLocateMe" title="取得您手機或設備目前的 GPS 位置">
        🎯 我的位置
      </button>
      <button class="map-tool-btn" id="btnFitBounds" title="縮放顯示全部標記點">
        🗺️ 全區視野
      </button>
    </div>

  </div>

  <!-- Modal: 新增客戶 -->
  <div class="modal-overlay" id="modalAdd">
    <div class="modal-card">
      <h3>➕ 新增拜訪客戶</h3>
      <form id="formAddClient">
        <div class="form-group">
          <label>公司 / 廠房名稱 *</label>
          <input type="text" id="addName" required placeholder="例如：台達電子工業 (中壢二廠)" />
        </div>
        <div class="form-group">
          <label>所在路段 *</label>
          <input type="text" id="addRoad" required placeholder="例如：中園路、吉林路" />
        </div>
        <div class="form-group">
          <label>完整地址 *</label>
          <input type="text" id="addAddress" required placeholder="桃園市中壢區..." />
        </div>
        <div style="display:flex; gap:10px;">
          <div class="form-group" style="flex:1;">
            <label>緯度 (Lat) *</label>
            <input type="number" step="0.0001" id="addLat" value="24.9818" required />
          </div>
          <div class="form-group" style="flex:1;">
            <label>經度 (Lng) *</label>
            <input type="number" step="0.0001" id="addLng" value="121.2385" required />
          </div>
        </div>
        <div style="display:flex; gap:10px;">
          <div class="form-group" style="flex:1;">
            <label>聯絡窗口</label>
            <input type="text" id="addContact" placeholder="例如：陳廠長" />
          </div>
          <div class="form-group" style="flex:1;">
            <label>聯絡電話</label>
            <input type="text" id="addPhone" placeholder="例如：03-452-xxxx" />
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

  <!-- Leaflet JS -->
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
  
  <script>
    // --- 桃園 7 大園區真實廠商資料庫 ---
    const ALL_PARKS_DATA = __PARKS_DATA_PLACEHOLDER__;

    // State Variables
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

    // Load Data for current park
    function loadParkData(parkId) {
      currentPark = parkId;
      
      let baseClients = [];
      if (parkId === "all") {
        baseClients = [];
        Object.keys(ALL_PARKS_DATA).forEach(pid => {
          baseClients = baseClients.concat(ALL_PARKS_DATA[pid].clients);
        });
      } else {
        baseClients = ALL_PARKS_DATA[parkId] ? ALL_PARKS_DATA[parkId].clients : [];
      }

      // Check localStorage for saved visit statuses/notes
      const storageKey = parkId === "zhongli" ? "sales_visit_clients_v744" : `sales_visit_clients_${parkId}`;
      const stored = localStorage.getItem(storageKey);
      if (stored) {
        try {
          const storedList = JSON.parse(stored);
          const statusMap = {};
          storedList.forEach(item => {
            statusMap[item.id] = { status: item.status, notes: item.notes };
          });
          clients = baseClients.map(c => {
            if (statusMap[c.id]) {
              return { ...c, status: statusMap[c.id].status, notes: statusMap[c.id].notes };
            }
            return { ...c };
          });
        } catch (e) {
          clients = JSON.parse(JSON.stringify(baseClients));
        }
      } else {
        clients = JSON.parse(JSON.stringify(baseClients));
      }

      // Update titles
      if (parkId === "all") {
        document.getElementById('headerTitle').innerText = '桃園外勤巡訪地圖總中樞 · 全桃 7 大園區總覽';
        document.getElementById('headerSubtitle').innerText = `合計 1,874 家全區廠商（中壢、龜山、華亞、平鎮、觀音、大園、幼獅）`;
      } else {
        const pcfg = ALL_PARKS_DATA[parkId];
        document.getElementById('headerTitle').innerText = `業務外勤拜訪地圖 - ${pcfg.name}`;
        document.getElementById('headerSubtitle').innerText = `${pcfg.name} · ${pcfg.badge} 廠商全區地圖（支援上市櫃、產業、同路巡訪快篩）`;
      }

      // Reset filters when switching park
      activeIndustry = "ALL";
      activeRoad = "ALL";
      activeStatus = "ALL";
      // keep searchQuery if user was searching
      
      setupIndustryChips();
      setupRoadChips();
      updateBadgeCounts();

      // Pan/fly map
      if (map) {
        if (parkId === "all") {
          map.flyTo([25.01, 121.26], 12, { duration: 1 });
        } else {
          const pcfg = ALL_PARKS_DATA[parkId];
          map.flyTo(pcfg.center, pcfg.zoom, { duration: 1 });
        }
      }

      renderList();
    }

    function saveCurrentParkData() {
      const storageKey = currentPark === "zhongli" ? "sales_visit_clients_v744" : `sales_visit_clients_${currentPark}`;
      localStorage.setItem(storageKey, JSON.stringify(clients));
    }

    // --- Initialize Leaflet Map ---
    function initMap() {
      map = L.map('map', {
        zoomControl: true,
        attributionControl: false
      }).setView([24.9818, 121.2385], 15);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19
      }).addTo(map);

      L.control.attribution({ position: 'bottomright' })
        .addAttribution('&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>')
        .addTo(map);
    }

    // --- Debounced Marker Rendering for 60fps Performance ---
    function updateMarkersDebounced(filteredClients) {
      clearTimeout(markerDebounceTimer);
      markerDebounceTimer = setTimeout(() => {
        updateMarkers(filteredClients);
      }, 100);
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
        const popupContent = `
          <div style="font-family:'Noto Sans TC',sans-serif; min-width:210px; padding:2px;">
            <div style="font-weight:800; font-size:14px; color:#16213A; margin-bottom:3px; line-height:1.3;">
              ${c.name}
            </div>
            <div style="font-size:11px; color:#68717F; margin-bottom:6px;">
              ${c.address}
            </div>
            <div style="display:flex; gap:6px; align-items:center; margin-bottom:8px;">
              <span style="font-size:11px; font-weight:700; color:#1A4DA1; background:#EEF3FC; padding:2px 6px; border-radius:4px;">${c.road}</span>
              <span style="font-size:11px; color:#68717F;">${c.industry}</span>
            </div>
            <div style="display:flex; gap:6px; align-items:center; padding-top:8px; border-top:1px dashed #E6E3DB;">
              <button onclick="quickToggleVisit(${c.id})" 
                      style="flex:1; border:1px solid ${isDone ? '#2E8540' : '#1A4DA1'}; background:${isDone ? '#EBF7EE' : '#1A4DA1'}; color:${isDone ? '#2E8540' : '#FFFFFF'}; padding:6px 8px; border-radius:6px; font-weight:800; font-size:11.5px; cursor:pointer; display:inline-flex; align-items:center; justify-content:center; gap:4px;">
                ${isDone ? '✅ 已拜訪 (點擊還原)' : '✓ 標記為已拜訪'}
              </button>
              <a href="https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(c.address)}" 
                 target="_blank" 
                 style="font-size:11.5px; background:#E0622B; color:#fff; text-decoration:none; padding:6px 10px; border-radius:6px; font-weight:800; white-space:nowrap;">
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

      // Fit map if we have markers
      if (filteredClients.length > 0 && bounds.isValid() && filteredClients.length <= 150) {
        map.fitBounds(bounds, { padding: [50, 50], maxZoom: 16 });
      }
    }

    // --- Search & Multi-Dimensional Filtering Logic ---
    function executeFilter() {
      const q = (searchQuery || "").trim().toLowerCase();
      const keywords = q ? q.split(/\\s+/).filter(Boolean) : [];

      currentFiltered = clients.filter(c => {
        // 1. Search Query Match
        if (keywords.length > 0) {
          const targetStr = `${c.name || ''} ${c.address || ''} ${c.road || ''} ${c.industry || ''} ${c.contact || ''} ${c.phone || ''} ${c.notes || ''}`.toLowerCase();
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

      // Update Header Count Text
      document.getElementById('resultCountText').innerText = `顯示 ${currentFiltered.length} / ${clients.length} 家廠商`;
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

      // Zero Results Handling (With Smart Assistance)
      if (currentFiltered.length === 0) {
        const q = (searchQuery || "").trim();
        let noticeHtml = '';

        if (q) {
          // Check if relaxed search (ignoring road/industry filter) has results
          const keywords = q.toLowerCase().split(/\\s+/).filter(Boolean);
          const relaxedMatches = clients.filter(c => {
            const str = `${c.name || ''} ${c.address || ''} ${c.road || ''} ${c.industry || ''} ${c.contact || ''} ${c.phone || ''} ${c.notes || ''}`.toLowerCase();
            return keywords.every(kw => str.includes(kw));
          });

          if (relaxedMatches.length > 0 && (activeRoad !== 'ALL' || activeIndustry !== 'ALL' || activeStatus !== 'ALL')) {
            noticeHtml = `
              <div style="background:#FFFBEB; border:1px solid #FCD34D; padding:12px; border-radius:8px; margin-bottom:12px; text-align:left; font-size:12.5px; color:#92400E;">
                💡 <strong>提示：</strong>目前已啟用【${activeRoad !== 'ALL' ? activeRoad : ''} ${activeIndustry !== 'ALL' ? activeIndustry : ''} ${activeStatus !== 'ALL' ? activeStatus : ''}】篩選條件。<br>
                在全區中共有 <strong>${relaxedMatches.length}</strong> 家廠商符合「${q}」！<br>
                <button onclick="clearAllFiltersAndSearch()" class="btn btn-primary" style="margin-top:8px; font-size:12px; padding:4px 10px;">
                  🔓 解除標籤限制，顯示這 ${relaxedMatches.length} 家
                </button>
              </div>
            `;
          } else if (currentPark !== 'all') {
            // Check other parks
            let otherMatches = [];
            Object.keys(ALL_PARKS_DATA).forEach(pid => {
              if (pid !== currentPark) {
                const p = ALL_PARKS_DATA[pid];
                const matches = p.clients.filter(c => {
                  const str = `${c.name || ''} ${c.address || ''} ${c.road || ''} ${c.industry || ''} ${c.contact || ''} ${c.phone || ''} ${c.notes || ''}`.toLowerCase();
                  return keywords.every(kw => str.includes(kw));
                });
                if (matches.length > 0) {
                  otherMatches.push({ pid, name: p.name, count: matches.length, sample: matches[0].name });
                }
              }
            });

            if (otherMatches.length > 0) {
              noticeHtml = `
                <div style="background:#EFF6FF; border:1px solid #BFDBFE; padding:12px; border-radius:8px; margin-bottom:12px; text-align:left; font-size:12.5px; color:#1E40AF;">
                  📍 在目前園區未找到「<strong>${q}</strong>」，但在桃園其他園區找到符合廠商：<br>
                  <div style="margin-top:6px; display:flex; flex-direction:column; gap:4px;">
                    ${otherMatches.map(m => `
                      <div style="display:flex; justify-content:space-between; align-items:center; background:#FFF; padding:6px 10px; border-radius:6px; border:1px solid #DBEAFE;">
                        <span><strong>${m.name}</strong> (${m.count} 家，如 ${m.sample})</span>
                        <button onclick="switchPark('${m.pid}', '${q.replace(/'/g, "\\\\'")}')" class="btn btn-primary" style="padding:2px 8px; font-size:11px;">前往 ➔</button>
                      </div>
                    `).join('')}
                  </div>
                </div>
              `;
            }
          }
        }

        container.innerHTML = `
          <div style="text-align:center; padding:30px 16px; color:#6B7280;">
            ${noticeHtml}
            <div style="font-size:32px; margin-bottom:8px;">🔍</div>
            <div style="font-weight:700; font-size:15px; color:var(--navy);">找不到符合條件的廠商</div>
            <div style="font-size:12px; margin-top:4px;">請檢查關鍵字是否有錯字，或點擊上方「重設篩選」</div>
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

        card.innerHTML = `
          <div class="card-top">
            <div class="card-title">${c.name}</div>
            ${c.is_listed === '是' ? '<span class="badge-listed">★ 上市櫃</span>' : ''}
          </div>

          <div class="card-address">
            <span class="card-road">${c.road}</span>
            <span>${c.address}</span>
          </div>

          <div class="card-meta">
            <span>👤 ${c.contact || '總機/廠務'}</span>
            ${c.phone ? `<span>📞 <a href="tel:${c.phone}">${c.phone}</a></span>` : ''}
            <span class="badge-industry">${c.industry}</span>
          </div>

          <div class="card-notes" title="點擊卡片可查看地圖位置">
            📝 <strong>備忘：</strong><span id="note-text-${c.id}">${c.notes || '尚未填寫拜訪紀錄'}</span>
          </div>

          <div class="card-actions">
            <div>
              <select class="status-select ${statusClass}" onchange="changeClientStatus(${c.id}, this.value, event)">
                <option value="尚未拜訪" ${(c.status === '尚未拜訪' || c.status === '待拜訪') ? 'selected' : ''}>⏳ 尚未拜訪</option>
                <option value="洽談中" ${c.status === '洽談中' ? 'selected' : ''}>💬 洽談中</option>
                <option value="已拜訪" ${c.status === '已拜訪' ? 'selected' : ''}>✅ 已拜訪</option>
              </select>
            </div>

            <div style="display:flex; gap:6px;">
              <button class="btn" style="padding:4px 8px; font-size:11px;" onclick="editNotes(${c.id}, event)" title="修改備忘錄">
                ✏️ 備忘
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
        client.status = (client.status === '已拜訪') ? '尚未拜訪' : '已拜訪';
        saveCurrentParkData();
        renderList();
        if (markers[id]) {
          markers[id].openPopup();
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
      }
    };

    window.editNotes = function(id, event) {
      if (event) event.stopPropagation();
      const client = clients.find(c => c.id === id);
      if (!client) return;

      const newNote = prompt(`請輸入【${client.name}】的拜訪備忘或需求備註：`, client.notes || "");
      if (newNote !== null) {
        client.notes = newNote.trim();
        saveCurrentParkData();
        const noteSpan = document.getElementById(`note-text-${id}`);
        if (noteSpan) noteSpan.innerText = client.notes || '尚未填寫拜訪紀錄';
      }
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

      // All option
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

      // Sort by factory count descending
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

    // --- Park Switcher Handler ---
    window.switchPark = function(parkId, newSearchTerm) {
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
      loadParkData("zhongli");

      // Park Navigation Pills Click
      document.querySelectorAll('#parkNavBar .park-pill').forEach(pill => {
        pill.addEventListener('click', () => {
          const pid = pill.getAttribute('data-park');
          switchPark(pid);
        });
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

      // Search Input Handling (with robust Chinese IME & Button support)
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

      // Locate User GPS (外勤業務神功能)
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

      // Export CSV
      document.getElementById('btnExport').addEventListener('click', () => {
        let csvContent = "\\uFEFFid,name,road,address,lat,lng,industry,is_listed,status,contact,phone,notes\\n";
        clients.forEach(c => {
          const row = [
            c.id,
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
            `"${(c.notes || '').replace(/"/g, '""')}"`
          ].join(",");
          csvContent += row + "\\n";
        });

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        const parkName = currentPark === 'all' ? '全桃7大園區' : (ALL_PARKS_DATA[currentPark] ? ALL_PARKS_DATA[currentPark].name : '園區');
        a.download = `${parkName}_業務拜訪記錄_${new Date().toISOString().slice(0,10)}.csv`;
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

      document.getElementById('formAddClient').addEventListener('submit', (e) => {
        e.preventDefault();
        const center = (ALL_PARKS_DATA[currentPark] && ALL_PARKS_DATA[currentPark].center) || [24.9818, 121.2385];
        const newClient = {
          id: Date.now(),
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
          notes: document.getElementById('addNotes').value.trim()
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

    // Helper: Parse CSV
    function parseAndImportCSV(csvText) {
      const lines = csvText.split(/\\r?\\n/).filter(line => line.trim() !== "");
      if (lines.length <= 1) {
        alert("CSV 內容為空或格式不符");
        return;
      }

      const headers = lines[0].split(",").map(h => h.trim().replace(/^"|"$/g, ''));
      const imported = [];

      for (let i = 1; i < lines.length; i++) {
        const row = lines[i].split(",").map(val => val.trim().replace(/^"|"$/g, ''));
        if (row.length < 5) continue;

        imported.push({
          id: Date.now() + i,
          name: row[1] || `客戶 ${i}`,
          road: row[2] || "園區內",
          address: row[3] || "",
          lat: parseFloat(row[4]) || 24.9818,
          lng: parseFloat(row[5]) || 121.2385,
          industry: row[6] || "其他",
          is_listed: row[7] || "否",
          status: row[8] || "尚未拜訪",
          contact: row[9] || "",
          phone: row[10] || "",
          notes: row[11] || ""
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
        alert("解析 CSV 失敗，請確認欄位格式是否與範本一致。");
      }
    }
  </script>
</body>
</html>
'''

full_html = html_template.replace('__PARKS_DATA_PLACEHOLDER__', all_parks_json)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(full_html)

print(f"Generated index.html successfully! Size: {len(full_html.encode('utf-8'))} bytes")

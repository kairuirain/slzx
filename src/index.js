export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    // API: serve notices data
    if (path === '/api/notices') {
      try {
        return await env.ASSETS.fetch(new Request(url.origin + '/notices.json', request));
      } catch (e) {
        return new Response(JSON.stringify({ notices: [] }), {
          headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
        });
      }
    }

    // SPA pages: serve shell HTML
    const spaPaths = ['/', '/home', '/file', '/notice'];
    const isSpaPage = spaPaths.includes(path) || path.startsWith('/notice/');
    if (isSpaPage) {
      return new Response(renderHTML(), {
        headers: { 'Content-Type': 'text/html;charset=utf-8', 'Cache-Control': 'public, max-age=3600' }
      });
    }

    // Static assets
    try {
      return await env.ASSETS.fetch(request);
    } catch (e) {
      return new Response('Not Found', { status: 404 });
    }
  }
};

function renderHTML() {
  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>四川省双流中学 · 初2024级7班班委会</title>
  <style>
    :root {
      --primary: #1a5276;
      --primary-light: #2980b9;
      --accent: #e74c3c;
      --bg: #f0f3f8;
      --card-bg: #ffffff;
      --text: #2c3e50;
      --text-light: #7f8c8d;
      --border: #e1e8f0;
      --shadow: 0 2px 12px rgba(0,0,0,0.08);
      --shadow-hover: 0 6px 24px rgba(0,0,0,0.12);
      --radius: 12px;
      --transition: 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }

    * { margin: 0; padding: 0; box-sizing: border-box; }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", "Helvetica Neue", sans-serif;
      background: linear-gradient(135deg, #e8edf5 0%, #f0f3f8 30%, #eaf0f6 60%, #f5f0eb 100%);
      min-height: 100vh;
      color: var(--text);
      line-height: 1.6;
    }

    /* ─── Header / Brand ─── */
    .header {
      background: linear-gradient(135deg, #1a3a4a 0%, #1a5276 50%, #1f6f8b 100%);
      color: #fff;
      padding: 24px 24px 0;
      text-align: center;
      position: relative;
      overflow: hidden;
      box-shadow: 0 4px 20px rgba(26,82,118,0.25);
    }
    .header::before {
      content: ''; position: absolute; top: -50%; left: -50%;
      width: 200%; height: 200%;
      background: radial-gradient(circle at 30% 50%, rgba(255,255,255,0.06) 0%, transparent 60%);
    }
    .header-content { position: relative; z-index: 1; }
    .header h1 { font-size: 1.5rem; font-weight: 700; letter-spacing: 0.03em; text-shadow: 0 2px 4px rgba(0,0,0,0.15); }
    .header .subtitle { font-size: 0.88rem; opacity: 0.85; margin: 2px 0 6px; letter-spacing: 0.05em; }

    /* ─── Navigation ─── */
    .nav-bar {
      display: flex; justify-content: center; gap: 4px;
      position: relative; z-index: 2; padding: 4px 0 0;
    }
    .nav-link {
      display: inline-flex; align-items: center; gap: 6px;
      padding: 10px 24px; border-radius: 10px 10px 0 0;
      color: rgba(255,255,255,0.75); text-decoration: none;
      font-size: 0.95rem; font-weight: 500;
      transition: var(--transition); cursor: pointer;
    }
    .nav-link:hover { color: #fff; background: rgba(255,255,255,0.08); }
    .nav-link.active { color: var(--primary); background: #fff; font-weight: 700; }

    /* ─── Container ─── */
    .container {
      max-width: 1000px; margin: 0 auto; padding: 24px 20px 60px;
    }

    /* ─── Page sections ─── */
    .page { display: none; }
    .page.active { display: block; }

    /* ─── Home Page ─── */
    .home-hero {
      text-align: center; padding: 40px 20px 32px;
      background: var(--card-bg); border-radius: var(--radius);
      box-shadow: var(--shadow); margin-bottom: 20px;
    }
    .home-hero .hero-icon { font-size: 3.5rem; margin-bottom: 12px; }
    .home-hero h2 { font-size: 1.4rem; color: var(--primary); margin-bottom: 6px; }
    .home-hero p { color: var(--text-light); font-size: 0.93rem; }

    .home-stats {
      display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: 12px; margin-bottom: 24px;
    }
    .stat-card {
      background: var(--card-bg); border-radius: var(--radius);
      box-shadow: var(--shadow); padding: 18px 16px; text-align: center;
      transition: var(--transition);
    }
    .stat-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-hover); }
    .stat-card .stat-num { font-size: 1.8rem; font-weight: 700; color: var(--primary-light); }
    .stat-card .stat-label { font-size: 0.82rem; color: var(--text-light); margin-top: 2px; }

    .section-title {
      font-size: 1.1rem; font-weight: 700; color: var(--text);
      margin-bottom: 12px; display: flex; align-items: center; gap: 8px;
    }
    .section-title .count-badge {
      font-size: 0.75rem; background: var(--bg); color: var(--text-light);
      padding: 2px 10px; border-radius: 12px; font-weight: 400;
    }
    .view-all { font-size: 0.82rem; color: var(--primary-light); text-decoration: none; margin-left: auto; cursor: pointer; }
    .view-all:hover { text-decoration: underline; }

    /* ─── Notice Cards ─── */
    .notice-grid {
      display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 12px; margin-bottom: 24px;
    }
    .notice-card {
      background: var(--card-bg); border-radius: var(--radius);
      box-shadow: var(--shadow); padding: 18px 20px;
      cursor: pointer; transition: var(--transition);
      border: 1.5px solid transparent; position: relative;
    }
    .notice-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-hover); border-color: var(--primary-light); }
    .notice-card.pinned { border-left: 3px solid var(--accent); }
    .notice-card .pin-badge {
      position: absolute; top: 8px; right: 12px;
      color: var(--accent); font-size: 0.75rem; font-weight: 600;
    }
    .notice-card h4 { font-size: 0.98rem; color: var(--text); margin-bottom: 4px; padding-right: 48px; }
    .notice-card .notice-meta {
      font-size: 0.78rem; color: var(--text-light);
      display: flex; gap: 12px; margin-bottom: 8px;
    }
    .notice-card .notice-excerpt {
      font-size: 0.84rem; color: #5a6a7a;
      display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
      overflow: hidden;
    }

    /* ─── Notice Detail Page ─── */
    .notice-detail {
      background: var(--card-bg); border-radius: var(--radius);
      box-shadow: var(--shadow); padding: 32px 36px;
    }
    .notice-detail .back-btn {
      display: inline-flex; align-items: center; gap: 4px;
      color: var(--primary-light); background: none; border: none;
      font-size: 0.88rem; cursor: pointer; margin-bottom: 16px; padding: 4px 0;
    }
    .notice-detail .back-btn:hover { color: var(--primary); }
    .notice-detail h2 { font-size: 1.4rem; color: var(--text); margin-bottom: 8px; }
    .notice-detail .detail-meta {
      font-size: 0.84rem; color: var(--text-light);
      padding-bottom: 16px; border-bottom: 1px solid var(--border);
      margin-bottom: 20px; display: flex; gap: 16px;
    }
    .notice-detail .detail-content { line-height: 1.8; }

    /* ─── Markdown / Docx Content ─── */
    .md-content h1 { font-size: 1.5rem; margin: 1em 0 0.3em; color: #1a3a4a; border-bottom: 1px solid #eee; padding-bottom: 6px; }
    .md-content h2 { font-size: 1.25rem; margin: 0.8em 0 0.3em; color: #1a3a4a; }
    .md-content h3 { font-size: 1.1rem; margin: 0.6em 0 0.25em; color: #1a3a4a; }
    .md-content p { margin: 0.5em 0; }
    .md-content ul, .md-content ol { margin: 0.5em 0; padding-left: 2em; }
    .md-content li { margin: 0.2em 0; }
    .md-content code {
      background: #f0f0f0; padding: 2px 6px; border-radius: 4px;
      font-family: "Cascadia Code", monospace; font-size: 0.88em;
    }
    .md-content pre {
      background: #1e1e2e; color: #cdd6f4; padding: 16px; border-radius: 8px;
      overflow-x: auto; font-size: 0.85rem; line-height: 1.5; margin: 0.5em 0;
    }
    .md-content pre code { background: none; padding: 0; color: inherit; }
    .md-content blockquote {
      border-left: 3px solid var(--primary-light); padding: 8px 16px;
      margin: 0.5em 0; background: #f5f8fc; color: #5a6a7a;
    }
    .md-content table { border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 0.9rem; }
    .md-content table td, .md-content table th {
      border: 1px solid #d5dce6; padding: 8px 12px; text-align: left;
    }
    .md-content table th { background: #eaf2f8; font-weight: 600; }
    .md-content img { max-width: 100%; border-radius: 6px; }
    .md-content a { color: var(--primary-light); }
    .md-content hr { border: none; border-top: 1px solid var(--border); margin: 1em 0; }

    /* ─── Stats Bar ─── */
    .stats-bar {
      display: flex; align-items: center; justify-content: space-between;
      flex-wrap: wrap; gap: 12px; margin-bottom: 20px;
      padding: 16px 20px; background: var(--card-bg);
      border-radius: var(--radius); box-shadow: var(--shadow);
    }
    .stats-info { display: flex; align-items: center; gap: 8px; font-size: 0.95rem; color: var(--text-light); }
    .stats-count { background: var(--primary-light); color: #fff; padding: 3px 12px; border-radius: 20px; font-weight: 600; font-size: 0.9rem; }

    .search-box {
      display: flex; align-items: center; gap: 6px;
      background: var(--bg); border-radius: 24px;
      padding: 8px 16px; border: 1.5px solid var(--border);
      transition: var(--transition);
    }
    .search-box:focus-within { border-color: var(--primary-light); box-shadow: 0 0 0 3px rgba(41,128,185,0.12); }
    .search-box input { border: none; background: transparent; outline: none; font-size: 0.93rem; color: var(--text); width: 180px; font-family: inherit; }
    .search-box input::placeholder { color: #b0b8c1; }
    .search-icon { color: var(--text-light); font-size: 1rem; flex-shrink: 0; }

    /* ─── File Grid ─── */
    .file-grid {
      display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 14px;
    }
    .file-card {
      background: var(--card-bg); border-radius: var(--radius);
      padding: 18px 20px; display: flex; align-items: center; gap: 14px;
      box-shadow: var(--shadow); border: 1.5px solid transparent;
      cursor: pointer; transition: var(--transition); position: relative; overflow: hidden;
    }
    .file-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-hover); border-color: var(--primary-light); }
    .file-card:active { transform: translateY(0); }

    .file-icon {
      width: 48px; height: 48px; border-radius: 10px;
      display: flex; align-items: center; justify-content: center;
      font-size: 1.3rem; font-weight: 700; flex-shrink: 0; color: #fff;
    }
    .file-icon.pdf { background: linear-gradient(135deg, #e74c3c, #c0392b); }
    .file-icon.txt { background: linear-gradient(135deg, #3498db, #2980b9); }
    .file-icon.md { background: linear-gradient(135deg, #2ecc71, #27ae60); }
    .file-icon.docx, .file-icon.doc { background: linear-gradient(135deg, #2b7cd3, #1a5ca8); }
    .file-icon.xlsx, .file-icon.xls { background: linear-gradient(135deg, #27ae60, #1e8449); }
    .file-icon.pptx, .file-icon.ppt { background: linear-gradient(135deg, #e67e22, #ca6f1e); }
    .file-icon.img, .file-icon.jpg, .file-icon.jpeg, .file-icon.png, .file-icon.gif, .file-icon.webp { background: linear-gradient(135deg, #9b59b6, #7d3c98); }
    .file-icon.other { background: linear-gradient(135deg, #7f8c8d, #636e72); }

    .file-info { flex: 1; min-width: 0; }
    .file-name {
      font-size: 0.95rem; font-weight: 600; color: var(--text);
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .file-type-badge {
      display: inline-block; font-size: 0.72rem; color: var(--text-light);
      background: var(--bg); padding: 2px 8px; border-radius: 4px;
      margin-top: 4px; text-transform: uppercase; letter-spacing: 0.04em;
    }
    .file-actions { display: flex; flex-direction: column; gap: 6px; flex-shrink: 0; }

    .btn {
      display: inline-flex; align-items: center; justify-content: center; gap: 4px;
      border: none; border-radius: 8px; padding: 7px 14px;
      font-size: 0.82rem; font-weight: 500; cursor: pointer;
      transition: var(--transition); text-decoration: none; white-space: nowrap; font-family: inherit;
    }
    .btn-preview { background: #eaf2f8; color: var(--primary-light); }
    .btn-preview:hover { background: #d4e6f1; color: var(--primary); }
    .btn-download { background: var(--primary-light); color: #fff; }
    .btn-download:hover { background: var(--primary); box-shadow: 0 2px 8px rgba(26,82,118,0.3); }

    /* ─── Modal ─── */
    .modal-overlay {
      display: none; position: fixed; inset: 0;
      background: rgba(0,0,0,0.55); z-index: 1000;
      align-items: center; justify-content: center;
      backdrop-filter: blur(3px); animation: fadeIn 0.2s ease;
    }
    .modal-overlay.active { display: flex; }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    @keyframes slideUp { from { opacity: 0; transform: translateY(24px); } to { opacity: 1; transform: translateY(0); } }

    .modal {
      background: #fff; border-radius: 16px; width: 92vw; max-width: 900px;
      max-height: 88vh; display: flex; flex-direction: column;
      box-shadow: 0 20px 60px rgba(0,0,0,0.25); animation: slideUp 0.3s ease;
    }
    .modal-header {
      display: flex; align-items: center; justify-content: space-between;
      padding: 16px 24px; border-bottom: 1px solid var(--border);
    }
    .modal-title { font-size: 1.1rem; font-weight: 700; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .modal-close {
      width: 36px; height: 36px; border: none; background: var(--bg);
      border-radius: 50%; cursor: pointer; font-size: 1.2rem; color: var(--text-light);
      display: flex; align-items: center; justify-content: center; transition: var(--transition); flex-shrink: 0;
    }
    .modal-close:hover { background: #e74c3c; color: #fff; }
    .modal-body {
      flex: 1; overflow: auto; padding: 0; display: flex;
      align-items: center; justify-content: center; min-height: 300px;
    }
    .modal-body iframe { width: 100%; height: 75vh; border: none; }
    .modal-body pre {
      width: 100%; height: 70vh; margin: 0; padding: 24px;
      font-family: "Cascadia Code", "Fira Code", "Source Code Pro", "Courier New", monospace;
      font-size: 0.88rem; line-height: 1.7; white-space: pre-wrap; word-wrap: break-word;
      background: #fafbfc; color: #2c3e50; border: none; overflow: auto;
    }
    .docx-preview {
      width: 100%; max-height: 70vh; overflow: auto;
      padding: 32px 40px; background: #fff;
      font-size: 0.95rem; line-height: 1.8; color: #333;
    }
    .docx-preview h1 { font-size: 1.6rem; margin: 0.8em 0 0.4em; color: #1a3a4a; }
    .docx-preview h2 { font-size: 1.35rem; margin: 0.7em 0 0.35em; color: #1a3a4a; }
    .docx-preview h3 { font-size: 1.15rem; margin: 0.6em 0 0.3em; color: #1a3a4a; }
    .docx-preview h4, .docx-preview h5, .docx-preview h6 { margin: 0.5em 0 0.25em; color: #1a3a4a; }
    .docx-preview p { margin: 0.5em 0; }
    .docx-preview table { border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 0.9rem; }
    .docx-preview table td, .docx-preview table th { border: 1px solid #d5dce6; padding: 8px 12px; text-align: left; }
    .docx-preview table th { background: #eaf2f8; font-weight: 600; }
    .docx-preview ul, .docx-preview ol { margin: 0.5em 0; padding-left: 2em; }
    .docx-preview li { margin: 0.2em 0; }
    .docx-preview img { max-width: 100%; border-radius: 6px; }
    .docx-warnings {
      margin-top: 16px; padding: 8px 16px; background: #fef9e7;
      border-left: 3px solid #f1c40f; color: #7d6608;
      font-size: 0.82rem; border-radius: 0 6px 6px 0;
    }
    .modal-footer {
      padding: 12px 24px; border-top: 1px solid var(--border);
      display: flex; justify-content: flex-end; gap: 8px;
    }

    /* ─── Empty State ─── */
    .empty-state { text-align: center; padding: 60px 20px; color: var(--text-light); }
    .empty-icon { font-size: 4rem; margin-bottom: 16px; opacity: 0.5; }
    .empty-state h3 { font-size: 1.2rem; font-weight: 600; color: var(--text); margin-bottom: 8px; }
    .empty-state p { font-size: 0.9rem; }

    /* ─── Loading ─── */
    .loading-spinner { text-align: center; padding: 60px; color: var(--text-light); }
    .spinner {
      display: inline-block; width: 36px; height: 36px;
      border: 3px solid var(--border); border-top-color: var(--primary-light);
      border-radius: 50%; animation: spin 0.8s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }

    /* ─── Toast ─── */
    .toast {
      position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
      background: #2c3e50; color: #fff; padding: 10px 24px; border-radius: 24px;
      font-size: 0.88rem; z-index: 2000; opacity: 0;
      transition: opacity 0.3s; pointer-events: none;
    }
    .toast.show { opacity: 1; }

    /* ─── Footer ─── */
    .footer { text-align: center; padding: 24px; color: var(--text-light); font-size: 0.82rem; }

    /* ─── Responsive ─── */
    @media (max-width: 640px) {
      .header h1 { font-size: 1.2rem; }
      .nav-link { padding: 8px 16px; font-size: 0.85rem; }
      .file-grid, .notice-grid { grid-template-columns: 1fr; }
      .file-card { padding: 14px 16px; }
      .stats-bar { flex-direction: column; align-items: stretch; }
      .search-box input { width: 100%; }
      .modal { width: 96vw; max-height: 94vh; }
      .modal-body iframe, .modal-body pre { height: 60vh; }
      .home-stats { grid-template-columns: repeat(2, 1fr); }
      .notice-detail { padding: 20px 20px; }
    }
  </style>
  <script src="https://cdn.jsdelivr.net/npm/mammoth@1.8.0/mammoth.browser.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/marked@12.0.0/marked.min.js"></script>
</head>
<body>

  <!-- Header -->
  <header class="header">
    <div class="header-content">
      <h1>四川省双流中学</h1>
      <p class="subtitle">初2024级7班 · 班委会</p>
    </div>
    <nav class="nav-bar" id="navBar">
      <a class="nav-link" href="/home" data-page="home">🏠 首页</a>
      <a class="nav-link" href="/file" data-page="file">📂 文件</a>
      <a class="nav-link" href="/notice" data-page="notice">📢 通知</a>
    </nav>
  </header>

  <!-- Main Container -->
  <div class="container">
    <!-- Page: Home -->
    <div class="page" id="page-home">
      <div class="home-hero">
        <div class="hero-icon">📚</div>
        <h2>欢迎访问班委会管理系统</h2>
        <p>在这里查看最新通知，下载班级文件</p>
      </div>
      <div class="home-stats" id="homeStats"></div>
      <div class="section-title">
        📢 最新通知 <span class="count-badge" id="homeNoticeCount">0</span>
        <a class="view-all" href="/notice">查看全部 →</a>
      </div>
      <div class="notice-grid" id="homeNotices"><div class="loading-spinner"><div class="spinner"></div></div></div>
      <div class="section-title">
        📂 最新文件 <span class="count-badge" id="homeFileCount">0</span>
        <a class="view-all" href="/file">查看全部 →</a>
      </div>
      <div class="file-grid" id="homeFiles"><div class="loading-spinner"><div class="spinner"></div></div></div>
    </div>

    <!-- Page: File -->
    <div class="page" id="page-file">
      <div class="stats-bar">
        <div class="stats-info">📂 文件总数：<span class="stats-count" id="fileCount">0</span></div>
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input type="text" id="searchInput" placeholder="搜索文件..." oninput="filterFiles()">
        </div>
      </div>
      <div class="file-grid" id="fileGrid"><div class="loading-spinner"><div class="spinner"></div><p style="margin-top:12px;">正在加载文件列表...</p></div></div>
      <div class="empty-state" id="emptyState" style="display:none;">
        <div class="empty-icon">📭</div>
        <h3>暂无文件</h3>
        <p>班委会成员可通过管理工具上传文件</p>
      </div>
    </div>

    <!-- Page: Notice -->
    <div class="page" id="page-notice">
      <div id="noticeListView">
        <div class="section-title" style="margin-bottom:16px;">📢 全部通知 <span class="count-badge" id="noticeCount">0</span></div>
        <div class="notice-grid" id="noticeGrid"><div class="loading-spinner"><div class="spinner"></div></div></div>
      </div>
      <div id="noticeDetailView" style="display:none;"></div>
    </div>
  </div>

  <!-- Preview Modal -->
  <div class="modal-overlay" id="modalOverlay" onclick="closeModal(event)">
    <div class="modal" onclick="event.stopPropagation()">
      <div class="modal-header">
        <span class="modal-title" id="modalTitle">文件预览</span>
        <button class="modal-close" onclick="closeModal()" title="关闭">✕</button>
      </div>
      <div class="modal-body" id="modalBody"></div>
      <div class="modal-footer">
        <a class="btn btn-download" id="modalDownload" href="#" download>⬇ 下载文件</a>
      </div>
    </div>
  </div>

  <!-- Toast -->
  <div class="toast" id="toast"></div>

  <!-- Footer -->
  <div class="footer">四川省双流中学 初2024级7班 班委会 · 文件管理系统</div>

  <script>
    // ==================== 文件类型定义 ====================
    const FILE_TYPES = {
      pdf:   { icon: 'PDF',  cls: 'pdf',  previewable: true },
      txt:   { icon: 'TXT',  cls: 'txt',  previewable: true },
      md:    { icon: 'MD',   cls: 'md',   previewable: true },
      docx:  { icon: 'DOC',  cls: 'docx', previewable: true },
      doc:   { icon: 'DOC',  cls: 'doc',  previewable: false },
      xlsx:  { icon: 'XLS',  cls: 'xlsx', previewable: false },
      xls:   { icon: 'XLS',  cls: 'xls',  previewable: false },
      pptx:  { icon: 'PPT',  cls: 'pptx', previewable: false },
      ppt:   { icon: 'PPT',  cls: 'ppt',  previewable: false },
      jpg:   { icon: 'IMG',  cls: 'img',  previewable: true },
      jpeg:  { icon: 'IMG',  cls: 'img',  previewable: true },
      png:   { icon: 'IMG',  cls: 'img',  previewable: true },
      gif:   { icon: 'IMG',  cls: 'img',  previewable: true },
      webp:  { icon: 'IMG',  cls: 'img',  previewable: true },
      mp4:   { icon: 'VID',  cls: 'other', previewable: true },
      mp3:   { icon: 'AUD',  cls: 'other', previewable: true },
      zip:   { icon: 'ZIP',  cls: 'other', previewable: false },
    };

    function getFileTypeInfo(type) {
      return FILE_TYPES[type] || { icon: 'FILE', cls: 'other', previewable: false };
    }

    // ==================== 全局状态 ====================
    let allFiles = [];
    let allNotices = [];

    // ==================== 路由系统 ====================
    function getCurrentPage() {
      const path = window.location.pathname;
      if (path === '/file') return 'file';
      if (path === '/notice' || path.startsWith('/notice/')) return 'notice';
      return 'home';
    }

    function navigateTo(path) {
      history.pushState(null, '', path);
      router();
    }

    function router() {
      const page = getCurrentPage();
      // Update nav
      document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.toggle('active', link.dataset.page === page);
      });
      // Show/hide pages
      document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
      document.getElementById('page-' + page).classList.add('active');

      if (page === 'home') renderHome();
      else if (page === 'file') renderFilePage();
      else if (page === 'notice') {
        const match = location.pathname.match(/^\\/notice\\/(\\d+)$/);
        if (match) {
          renderNoticeDetail(match[1]);
        } else {
          document.getElementById('noticeListView').style.display = '';
          document.getElementById('noticeDetailView').style.display = 'none';
          renderNoticeList();
        }
      }
    }

    // Handle nav clicks
    document.getElementById('navBar').addEventListener('click', function(e) {
      const link = e.target.closest('.nav-link');
      if (link) {
        e.preventDefault();
        navigateTo(link.getAttribute('href'));
      }
    });

    // Handle back/forward
    window.addEventListener('popstate', router);
    // Handle clicks on view-all links
    document.addEventListener('click', function(e) {
      if (e.target.classList.contains('view-all')) {
        e.preventDefault();
        navigateTo(e.target.getAttribute('href'));
      }
    });

    // ==================== 工具函数 ====================
    function escapeHtml(str) {
      if (!str) return '';
      return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    function truncateText(text, len) {
      if (!text) return '';
      // Strip markdown
      const plain = text.replace(/[#*_~`>\\-\\[\\]\\(\\)!]/g, '').trim();
      return plain.length > len ? plain.substring(0, len) + '...' : plain;
    }

    function showToast(msg) {
      const toast = document.getElementById('toast');
      toast.textContent = msg;
      toast.classList.add('show');
      clearTimeout(toast._timeout);
      toast._timeout = setTimeout(() => toast.classList.remove('show'), 2000);
    }

    // ==================== 通知系统 ====================
    async function loadNotices() {
      try {
        const resp = await fetch('/api/notices');
        if (!resp.ok) throw new Error('加载失败');
        const data = await resp.json();
        allNotices = data.notices || [];
        return allNotices;
      } catch (err) {
        console.error('加载通知失败:', err);
        return [];
      }
    }

    function renderNoticeList(noticesToShow) {
      const notices = noticesToShow || allNotices;
      const grid = document.getElementById('noticeGrid');
      const countEl = document.getElementById('noticeCount');

      if (!grid) return;

      countEl.textContent = notices.length;

      if (notices.length === 0) {
        grid.innerHTML = '<div class="empty-state" style="grid-column:1/-1;"><div class="empty-icon">📋</div><h3>暂无通知</h3><p>班委会成员可发布通知</p></div>';
        return;
      }

      grid.innerHTML = notices.map(n => {
        const pinnedHtml = n.pinned ? '<span class="pin-badge">📌 置顶</span>' : '';
        const excerpt = truncateText(n.content, 80);
        return '<div class="notice-card' + (n.pinned ? ' pinned' : '') + '" onclick="viewNoticeDetail(\\'' + escapeHtml(n.id) + '\\')">' +
          pinnedHtml +
          '<h4>' + escapeHtml(n.title) + '</h4>' +
          '<div class="notice-meta"><span>✍ ' + escapeHtml(n.author || '班委会') + '</span><span>📅 ' + escapeHtml(n.date || '') + '</span></div>' +
          '<div class="notice-excerpt">' + escapeHtml(excerpt) + '</div>' +
          '</div>';
      }).join('');
    }

    function viewNoticeDetail(id) {
      navigateTo('/notice/' + id);
    }

    function renderNoticeDetail(id) {
      const notice = allNotices.find(n => n.id === id);
      const listView = document.getElementById('noticeListView');
      const detailView = document.getElementById('noticeDetailView');

      if (!notice) {
        detailView.innerHTML = '<div class="empty-state"><div class="empty-icon">❓</div><h3>通知不存在</h3></div>';
        listView.style.display = 'none';
        detailView.style.display = '';
        return;
      }

      listView.style.display = 'none';
      detailView.style.display = '';
      detailView.innerHTML =
        '<div class="notice-detail">' +
        '<button class="back-btn" onclick="navigateTo(\\'/notice\\')">← 返回通知列表</button>' +
        '<h2>' + escapeHtml(notice.title) + '</h2>' +
        '<div class="detail-meta"><span>✍ ' + escapeHtml(notice.author || '班委会') + '</span><span>📅 ' + escapeHtml(notice.date || '') + '</span>' + (notice.pinned ? '<span>📌 置顶</span>' : '') + '</div>' +
        '<div class="detail-content md-content">' + marked.parse(notice.content || '') + '</div>' +
        '</div>';
    }

    // ==================== 首页渲染 ====================
    function renderHome() {
      // Stats
      document.getElementById('homeStats').innerHTML =
        '<div class="stat-card"><div class="stat-num">' + allFiles.length + '</div><div class="stat-label">📂 文件数</div></div>' +
        '<div class="stat-card"><div class="stat-num">' + allNotices.length + '</div><div class="stat-label">📢 通知数</div></div>' +
        '<div class="stat-card"><div class="stat-num">' + allNotices.filter(n => n.pinned).length + '</div><div class="stat-label">📌 置顶通知</div></div>';

      // Latest 3 notices
      const sortedNotices = [...allNotices].sort((a, b) => {
        if (a.pinned && !b.pinned) return -1;
        if (!a.pinned && b.pinned) return 1;
        return (b.date || '').localeCompare(a.date || '');
      });
      document.getElementById('homeNoticeCount').textContent = sortedNotices.length;

      const homeNoticeGrid = document.getElementById('homeNotices');
      if (sortedNotices.length === 0) {
        homeNoticeGrid.innerHTML = '<div class="empty-state" style="padding:32px;"><div class="empty-icon" style="font-size:2.5rem;">📋</div><p>暂无通知</p></div>';
      } else {
        homeNoticeGrid.innerHTML = sortedNotices.slice(0, 3).map(n => {
          const pinnedHtml = n.pinned ? '<span class="pin-badge">📌 置顶</span>' : '';
          const excerpt = truncateText(n.content, 60);
          return '<div class="notice-card' + (n.pinned ? ' pinned' : '') + '" onclick="viewNoticeDetail(\\'' + escapeHtml(n.id) + '\\')">' +
            pinnedHtml +
            '<h4>' + escapeHtml(n.title) + '</h4>' +
            '<div class="notice-meta"><span>✍ ' + escapeHtml(n.author || '班委会') + '</span><span>📅 ' + escapeHtml(n.date || '') + '</span></div>' +
            '<div class="notice-excerpt">' + escapeHtml(excerpt) + '</div>' +
            '</div>';
        }).join('');
      }

      // Latest 6 files
      document.getElementById('homeFileCount').textContent = allFiles.length;
      const homeFileGrid = document.getElementById('homeFiles');
      if (allFiles.length === 0) {
        homeFileGrid.innerHTML = '<div class="empty-state" style="padding:32px;grid-column:1/-1;"><div class="empty-icon" style="font-size:2.5rem;">📭</div><p>暂无文件</p></div>';
      } else {
        homeFileGrid.innerHTML = allFiles.slice(0, 6).map(f => {
          const info = getFileTypeInfo(f.type);
          const previewBtn = info.previewable
            ? '<button class="btn btn-preview" onclick="event.stopPropagation(); previewFile(\\'' + escapeHtml(f.name) + '\\', \\'' + f.type + '\\', \\'' + escapeHtml(f.path) + '\\')">👁 预览</button>'
            : '';
          return '<div class="file-card" onclick="previewFile(\\'' + escapeHtml(f.name) + '\\', \\'' + f.type + '\\', \\'' + escapeHtml(f.path) + '\\')">' +
            '<div class="file-icon ' + info.cls + '">' + info.icon + '</div>' +
            '<div class="file-info"><div class="file-name" title="' + escapeHtml(f.displayName) + '">' + escapeHtml(f.displayName) + '</div><span class="file-type-badge">.' + f.type + '</span></div>' +
            '<div class="file-actions">' + previewBtn + '<a class="btn btn-download" href="' + f.path + '" download="' + escapeHtml(f.name) + '" onclick="event.stopPropagation(); showToast(\\'开始下载\\')">⬇ 下载</a></div>' +
            '</div>';
        }).join('');
      }
    }

    // ==================== 文件页渲染 ====================
    function renderFilePage() {
      renderFiles(allFiles);
    }

    async function loadFiles() {
      try {
        const resp = await fetch('/manifest.json');
        if (!resp.ok) throw new Error('清单加载失败');
        allFiles = await resp.json();
        if (getCurrentPage() === 'home') renderHome();
        if (getCurrentPage() === 'file') renderFiles(allFiles);
      } catch (err) {
        console.error('加载文件列表失败:', err);
        const grid = document.getElementById('fileGrid');
        if (grid) {
          grid.innerHTML = '<div class="empty-state" style="grid-column:1/-1;"><div class="empty-icon">⚠️</div><h3>加载失败</h3><p>无法加载文件列表，请检查服务是否正常运行。</p></div>';
        }
      }
    }

    function renderFiles(files) {
      const grid = document.getElementById('fileGrid');
      const empty = document.getElementById('emptyState');
      const countEl = document.getElementById('fileCount');
      if (!grid) return;

      if (countEl) countEl.textContent = files.length;

      if (files.length === 0) {
        grid.innerHTML = '';
        if (empty) empty.style.display = 'block';
        return;
      }

      if (empty) empty.style.display = 'none';
      grid.innerHTML = files.map(f => {
        const info = getFileTypeInfo(f.type);
        const previewBtn = info.previewable
          ? '<button class="btn btn-preview" onclick="event.stopPropagation(); previewFile(\\'' + escapeHtml(f.name) + '\\', \\'' + f.type + '\\', \\'' + escapeHtml(f.path) + '\\')">👁 预览</button>'
          : '';
        return '<div class="file-card" onclick="previewFile(\\'' + escapeHtml(f.name) + '\\', \\'' + f.type + '\\', \\'' + escapeHtml(f.path) + '\\')" data-search="' + escapeHtml(f.displayName.toLowerCase()) + '">' +
          '<div class="file-icon ' + info.cls + '">' + info.icon + '</div>' +
          '<div class="file-info"><div class="file-name" title="' + escapeHtml(f.displayName) + '">' + escapeHtml(f.displayName) + '</div><span class="file-type-badge">.' + f.type + '</span></div>' +
          '<div class="file-actions">' + previewBtn + '<a class="btn btn-download" href="' + f.path + '" download="' + escapeHtml(f.name) + '" onclick="event.stopPropagation(); showToast(\\'开始下载：' + escapeHtml(f.displayName) + '\\')">⬇ 下载</a></div>' +
          '</div>';
      }).join('');
    }

    function filterFiles() {
      const query = document.getElementById('searchInput').value.toLowerCase().trim();
      if (!query) { renderFiles(allFiles); return; }
      const filtered = allFiles.filter(f =>
        f.displayName.toLowerCase().includes(query) || f.type.toLowerCase().includes(query)
      );
      renderFiles(filtered);
    }

    // ==================== 文件预览 ====================
    async function previewFile(name, type, path) {
      const overlay = document.getElementById('modalOverlay');
      const title = document.getElementById('modalTitle');
      const body = document.getElementById('modalBody');
      const downloadLink = document.getElementById('modalDownload');

      title.textContent = name;
      downloadLink.href = path;
      downloadLink.download = name;
      overlay.classList.add('active');
      document.body.style.overflow = 'hidden';

      const info = getFileTypeInfo(type);

      if (!info.previewable) {
        body.innerHTML = '<div class="empty-state"><div class="empty-icon">📄</div><h3>此文件类型暂不支持在线预览</h3><p>请点击下方按钮下载文件后查看</p></div>';
        return;
      }

      body.innerHTML = '<div class="loading-spinner"><div class="spinner"></div></div>';

      try {
        if (type === 'txt') {
          const resp = await fetch(path);
          if (!resp.ok) throw new Error('加载失败');
          const text = await resp.text();
          body.innerHTML = '<pre>' + escapeHtml(text) + '</pre>';
        } else if (type === 'md') {
          const resp = await fetch(path);
          if (!resp.ok) throw new Error('加载失败');
          const text = await resp.text();
          body.innerHTML = '<div class="docx-preview md-content">' + marked.parse(text) + '</div>';
        } else if (type === 'docx') {
          const resp = await fetch(path);
          if (!resp.ok) throw new Error('加载失败');
          const arrayBuffer = await resp.arrayBuffer();
          const result = await mammoth.convertToHtml({ arrayBuffer });
          body.innerHTML = '<div class="docx-preview">' + result.value + (result.messages.length ? '<div class="docx-warnings">⚠ 部分内容格式可能无法完全保留</div>' : '') + '</div>';
        } else if (type === 'pdf') {
          body.innerHTML = '<iframe src="' + path + '#toolbar=1&navpanes=1" allowfullscreen></iframe>';
        } else if (['jpg','jpeg','png','gif','webp'].includes(type)) {
          body.innerHTML = '<div style="padding:20px;text-align:center;width:100%;"><img src="' + path + '" alt="' + escapeHtml(name) + '" style="max-width:100%;max-height:70vh;border-radius:8px;box-shadow:0 2px 12px rgba(0,0,0,0.1);"></div>';
        } else if (type === 'mp4') {
          body.innerHTML = '<div style="padding:20px;text-align:center;width:100%;"><video controls style="max-width:100%;max-height:70vh;border-radius:8px;"><source src="' + path + '" type="video/mp4">您的浏览器不支持视频播放</video></div>';
        } else if (type === 'mp3') {
          body.innerHTML = '<div style="padding:40px 20px;text-align:center;width:100%;"><audio controls style="width:100%;max-width:400px;"><source src="' + path + '" type="audio/mpeg">您的浏览器不支持音频播放</audio></div>';
        }
      } catch (err) {
        body.innerHTML = '<div class="empty-state"><div class="empty-icon">⚠️</div><h3>预览失败</h3><p>请尝试下载文件后查看</p></div>';
      }
    }

    function closeModal(e) {
      if (e && e.target !== document.getElementById('modalOverlay')) return;
      document.getElementById('modalOverlay').classList.remove('active');
      document.body.style.overflow = '';
      document.getElementById('modalBody').innerHTML = '';
    }

    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') {
        const overlay = document.getElementById('modalOverlay');
        if (overlay.classList.contains('active')) {
          overlay.classList.remove('active');
          document.body.style.overflow = '';
          document.getElementById('modalBody').innerHTML = '';
        }
      }
    });

    // ==================== 初始化 ====================
    async function init() {
      await Promise.all([loadFiles(), loadNotices()]);
      router();
    }

    init();
  </script>
</body>
</html>`;
}

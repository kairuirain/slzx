var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });

// src/index.js
var index_default = {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (url.pathname === "/" || url.pathname === "/index.html") {
      return new Response(getHTML(), {
        headers: {
          "Content-Type": "text/html;charset=utf-8",
          "Cache-Control": "public, max-age=3600"
        }
      });
    }
    try {
      return await env.ASSETS.fetch(request);
    } catch (e) {
      return new Response("Not Found", { status: 404 });
    }
  }
};
function getHTML() {
  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>\u56DB\u5DDD\u7701\u53CC\u6D41\u4E2D\u5B66 \xB7 \u521D2024\u7EA77\u73ED\u73ED\u59D4\u4F1A\u6587\u4EF6\u7BA1\u7406\u7CFB\u7EDF</title>
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

    /* \u2500\u2500\u2500 Header \u2500\u2500\u2500 */
    .header {
      background: linear-gradient(135deg, #1a3a4a 0%, #1a5276 50%, #1f6f8b 100%);
      color: #fff;
      padding: 28px 24px;
      text-align: center;
      position: relative;
      overflow: hidden;
      box-shadow: 0 4px 20px rgba(26, 82, 118, 0.25);
    }

    .header::before {
      content: '';
      position: absolute;
      top: -50%;
      left: -50%;
      width: 200%;
      height: 200%;
      background: radial-gradient(circle at 30% 50%, rgba(255,255,255,0.06) 0%, transparent 60%);
    }

    .header-content {
      position: relative;
      z-index: 1;
    }

    .school-badge {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 10px;
    }

    .school-icon {
      width: 48px;
      height: 48px;
      background: rgba(255,255,255,0.15);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 26px;
      backdrop-filter: blur(4px);
    }

    .header h1 {
      font-size: 1.7rem;
      font-weight: 700;
      letter-spacing: 0.03em;
      text-shadow: 0 2px 4px rgba(0,0,0,0.15);
    }

    .header .subtitle {
      font-size: 0.95rem;
      font-weight: 400;
      opacity: 0.85;
      margin-top: 4px;
      letter-spacing: 0.05em;
    }

    /* \u2500\u2500\u2500 Container \u2500\u2500\u2500 */
    .container {
      max-width: 1000px;
      margin: 0 auto;
      padding: 24px 20px 60px;
    }

    /* \u2500\u2500\u2500 Stats Bar \u2500\u2500\u2500 */
    .stats-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 12px;
      margin-bottom: 20px;
      padding: 16px 20px;
      background: var(--card-bg);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }

    .stats-info {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.95rem;
      color: var(--text-light);
    }

    .stats-count {
      background: var(--primary-light);
      color: #fff;
      padding: 3px 12px;
      border-radius: 20px;
      font-weight: 600;
      font-size: 0.9rem;
    }

    .search-box {
      display: flex;
      align-items: center;
      gap: 6px;
      background: var(--bg);
      border-radius: 24px;
      padding: 8px 16px;
      border: 1.5px solid var(--border);
      transition: var(--transition);
    }

    .search-box:focus-within {
      border-color: var(--primary-light);
      box-shadow: 0 0 0 3px rgba(41, 128, 185, 0.12);
    }

    .search-box input {
      border: none;
      background: transparent;
      outline: none;
      font-size: 0.93rem;
      color: var(--text);
      width: 180px;
      font-family: inherit;
    }

    .search-box input::placeholder { color: #b0b8c1; }

    .search-icon {
      color: var(--text-light);
      font-size: 1rem;
      flex-shrink: 0;
    }

    /* \u2500\u2500\u2500 File Grid \u2500\u2500\u2500 */
    .file-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 14px;
    }

    .file-card {
      background: var(--card-bg);
      border-radius: var(--radius);
      padding: 18px 20px;
      display: flex;
      align-items: center;
      gap: 14px;
      box-shadow: var(--shadow);
      border: 1.5px solid transparent;
      cursor: pointer;
      transition: var(--transition);
      position: relative;
      overflow: hidden;
    }

    .file-card:hover {
      transform: translateY(-2px);
      box-shadow: var(--shadow-hover);
      border-color: var(--primary-light);
    }

    .file-card:active {
      transform: translateY(0);
    }

    .file-icon {
      width: 48px;
      height: 48px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.3rem;
      font-weight: 700;
      flex-shrink: 0;
      color: #fff;
    }

    .file-icon.pdf { background: linear-gradient(135deg, #e74c3c, #c0392b); }
    .file-icon.txt { background: linear-gradient(135deg, #3498db, #2980b9); }
    .file-icon.docx, .file-icon.doc { background: linear-gradient(135deg, #2b7cd3, #1a5ca8); }
    .file-icon.xlsx, .file-icon.xls { background: linear-gradient(135deg, #27ae60, #1e8449); }
    .file-icon.pptx, .file-icon.ppt { background: linear-gradient(135deg, #e67e22, #ca6f1e); }
    .file-icon.img, .file-icon.jpg, .file-icon.jpeg, .file-icon.png, .file-icon.gif, .file-icon.webp { background: linear-gradient(135deg, #9b59b6, #7d3c98); }
    .file-icon.other { background: linear-gradient(135deg, #7f8c8d, #636e72); }

    .file-info {
      flex: 1;
      min-width: 0;
    }

    .file-name {
      font-size: 0.95rem;
      font-weight: 600;
      color: var(--text);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .file-type-badge {
      display: inline-block;
      font-size: 0.72rem;
      color: var(--text-light);
      background: var(--bg);
      padding: 2px 8px;
      border-radius: 4px;
      margin-top: 4px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }

    .file-actions {
      display: flex;
      flex-direction: column;
      gap: 6px;
      flex-shrink: 0;
    }

    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 4px;
      border: none;
      border-radius: 8px;
      padding: 7px 14px;
      font-size: 0.82rem;
      font-weight: 500;
      cursor: pointer;
      transition: var(--transition);
      text-decoration: none;
      white-space: nowrap;
      font-family: inherit;
    }

    .btn-preview {
      background: #eaf2f8;
      color: var(--primary-light);
    }

    .btn-preview:hover {
      background: #d4e6f1;
      color: var(--primary);
    }

    .btn-download {
      background: var(--primary-light);
      color: #fff;
    }

    .btn-download:hover {
      background: var(--primary);
      box-shadow: 0 2px 8px rgba(26, 82, 118, 0.3);
    }

    /* \u2500\u2500\u2500 Modal \u2500\u2500\u2500 */
    .modal-overlay {
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.55);
      z-index: 1000;
      align-items: center;
      justify-content: center;
      backdrop-filter: blur(3px);
      animation: fadeIn 0.2s ease;
    }

    .modal-overlay.active {
      display: flex;
    }

    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }

    @keyframes slideUp {
      from { opacity: 0; transform: translateY(24px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .modal {
      background: #fff;
      border-radius: 16px;
      width: 92vw;
      max-width: 900px;
      max-height: 88vh;
      display: flex;
      flex-direction: column;
      box-shadow: 0 20px 60px rgba(0,0,0,0.25);
      animation: slideUp 0.3s ease;
    }

    .modal-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px 24px;
      border-bottom: 1px solid var(--border);
    }

    .modal-title {
      font-size: 1.1rem;
      font-weight: 700;
      color: var(--text);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .modal-close {
      width: 36px;
      height: 36px;
      border: none;
      background: var(--bg);
      border-radius: 50%;
      cursor: pointer;
      font-size: 1.2rem;
      color: var(--text-light);
      display: flex;
      align-items: center;
      justify-content: center;
      transition: var(--transition);
      flex-shrink: 0;
    }

    .modal-close:hover {
      background: #e74c3c;
      color: #fff;
    }

    .modal-body {
      flex: 1;
      overflow: auto;
      padding: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 300px;
    }

    .modal-body iframe {
      width: 100%;
      height: 75vh;
      border: none;
    }

    .modal-body pre {
      width: 100%;
      height: 70vh;
      margin: 0;
      padding: 24px;
      font-family: "Cascadia Code", "Fira Code", "Source Code Pro", "Courier New", monospace;
      font-size: 0.88rem;
      line-height: 1.7;
      white-space: pre-wrap;
      word-wrap: break-word;
      background: #fafbfc;
      color: #2c3e50;
      border: none;
      overflow: auto;
    }

    .modal-footer {
      padding: 12px 24px;
      border-top: 1px solid var(--border);
      display: flex;
      justify-content: flex-end;
      gap: 8px;
    }

    /* \u2500\u2500\u2500 Empty State \u2500\u2500\u2500 */
    .empty-state {
      text-align: center;
      padding: 60px 20px;
      color: var(--text-light);
    }

    .empty-icon {
      font-size: 4rem;
      margin-bottom: 16px;
      opacity: 0.5;
    }

    .empty-state h3 {
      font-size: 1.2rem;
      font-weight: 600;
      color: var(--text);
      margin-bottom: 8px;
    }

    .empty-state p {
      font-size: 0.9rem;
    }

    /* \u2500\u2500\u2500 Loading \u2500\u2500\u2500 */
    .loading-spinner {
      text-align: center;
      padding: 60px;
      color: var(--text-light);
    }

    .spinner {
      display: inline-block;
      width: 36px;
      height: 36px;
      border: 3px solid var(--border);
      border-top-color: var(--primary-light);
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    /* \u2500\u2500\u2500 Toast \u2500\u2500\u2500 */
    .toast {
      position: fixed;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%);
      background: #2c3e50;
      color: #fff;
      padding: 10px 24px;
      border-radius: 24px;
      font-size: 0.88rem;
      z-index: 2000;
      opacity: 0;
      transition: opacity 0.3s;
      pointer-events: none;
    }

    .toast.show {
      opacity: 1;
    }

    /* \u2500\u2500\u2500 Footer \u2500\u2500\u2500 */
    .footer {
      text-align: center;
      padding: 24px;
      color: var(--text-light);
      font-size: 0.82rem;
    }

    /* \u2500\u2500\u2500 Responsive \u2500\u2500\u2500 */
    @media (max-width: 640px) {
      .header h1 {
        font-size: 1.3rem;
      }

      .file-grid {
        grid-template-columns: 1fr;
      }

      .file-card {
        padding: 14px 16px;
      }

      .stats-bar {
        flex-direction: column;
        align-items: stretch;
      }

      .search-box input {
        width: 100%;
      }

      .modal {
        width: 96vw;
        max-height: 94vh;
      }

      .modal-body iframe,
      .modal-body pre {
        height: 60vh;
      }
    }
  </style>
</head>
<body>

  <!-- Header -->
  <header class="header">
    <div class="header-content">
      <div class="school-badge">
        <div class="school-icon">\u{1F3EB}</div>
      </div>
      <h1>\u56DB\u5DDD\u7701\u53CC\u6D41\u4E2D\u5B66</h1>
      <p class="subtitle">\u521D2024\u7EA77\u73ED \xB7 \u73ED\u59D4\u4F1A\u6587\u4EF6\u7BA1\u7406\u7CFB\u7EDF</p>
    </div>
  </header>

  <!-- Main Container -->
  <div class="container">
    <!-- Stats Bar -->
    <div class="stats-bar">
      <div class="stats-info">
        \u{1F4C2} \u6587\u4EF6\u603B\u6570\uFF1A<span class="stats-count" id="fileCount">0</span>
      </div>
      <div class="search-box">
        <span class="search-icon">\u{1F50D}</span>
        <input type="text" id="searchInput" placeholder="\u641C\u7D22\u6587\u4EF6..." oninput="filterFiles()">
      </div>
    </div>

    <!-- File Grid -->
    <div class="file-grid" id="fileGrid">
      <div class="loading-spinner">
        <div class="spinner"></div>
        <p style="margin-top:12px;">\u6B63\u5728\u52A0\u8F7D\u6587\u4EF6\u5217\u8868...</p>
      </div>
    </div>

    <!-- Empty State (hidden by default) -->
    <div class="empty-state" id="emptyState" style="display:none;">
      <div class="empty-icon">\u{1F4ED}</div>
      <h3>\u6682\u65E0\u6587\u4EF6</h3>
      <p>\u5C06\u6587\u4EF6\u653E\u5165 /file \u76EE\u5F55\u5373\u53EF\u663E\u793A</p>
    </div>
  </div>

  <!-- Preview Modal -->
  <div class="modal-overlay" id="modalOverlay" onclick="closeModal(event)">
    <div class="modal" onclick="event.stopPropagation()">
      <div class="modal-header">
        <span class="modal-title" id="modalTitle">\u6587\u4EF6\u9884\u89C8</span>
        <button class="modal-close" onclick="closeModal()" title="\u5173\u95ED">\u2715</button>
      </div>
      <div class="modal-body" id="modalBody"></div>
      <div class="modal-footer">
        <a class="btn btn-download" id="modalDownload" href="#" download>\u2B07 \u4E0B\u8F7D\u6587\u4EF6</a>
      </div>
    </div>
  </div>

  <!-- Toast -->
  <div class="toast" id="toast"></div>

  <!-- Footer -->
  <div class="footer">
    \u56DB\u5DDD\u7701\u53CC\u6D41\u4E2D\u5B66 \u521D2024\u7EA77\u73ED \u73ED\u59D4\u4F1A \xB7 \u6587\u4EF6\u7BA1\u7406\u7CFB\u7EDF
  </div>

  <script>
    // ==================== \u6587\u4EF6\u7C7B\u578B\u5B9A\u4E49 ====================
    const FILE_TYPES = {
      pdf:   { icon: 'PDF',  cls: 'pdf',  previewable: true },
      txt:   { icon: 'TXT',  cls: 'txt',  previewable: true },
      docx:  { icon: 'DOC',  cls: 'docx', previewable: false },
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

    // ==================== \u5168\u5C40\u72B6\u6001 ====================
    let allFiles = [];

    // ==================== \u52A0\u8F7D\u6587\u4EF6\u5217\u8868 ====================
    async function loadFiles() {
      try {
        const resp = await fetch('/manifest.json');
        if (!resp.ok) throw new Error('\u6E05\u5355\u52A0\u8F7D\u5931\u8D25');
        allFiles = await resp.json();
        renderFiles(allFiles);
      } catch (err) {
        console.error('\u52A0\u8F7D\u6587\u4EF6\u5217\u8868\u5931\u8D25:', err);
        document.getElementById('fileGrid').innerHTML = \`
          <div class="empty-state" style="grid-column:1/-1;">
            <div class="empty-icon">\u26A0\uFE0F</div>
            <h3>\u52A0\u8F7D\u5931\u8D25</h3>
            <p>\u65E0\u6CD5\u52A0\u8F7D\u6587\u4EF6\u5217\u8868\uFF0C\u8BF7\u68C0\u67E5\u670D\u52A1\u662F\u5426\u6B63\u5E38\u8FD0\u884C\u3002</p>
          </div>\`;
      }
    }

    // ==================== \u6E32\u67D3\u6587\u4EF6\u5217\u8868 ====================
    function renderFiles(files) {
      const grid = document.getElementById('fileGrid');
      const empty = document.getElementById('emptyState');
      const countEl = document.getElementById('fileCount');

      countEl.textContent = files.length;

      if (files.length === 0) {
        grid.innerHTML = '';
        empty.style.display = 'block';
        return;
      }

      empty.style.display = 'none';
      grid.innerHTML = files.map(f => {
        const info = getFileTypeInfo(f.type);
        const previewBtn = info.previewable
          ? \`<button class="btn btn-preview" onclick="event.stopPropagation(); previewFile('\${escapeHtml(f.name)}', '\${f.type}', '\${escapeHtml(f.path)}')">\u{1F441} \u9884\u89C8</button>\`
          : '';

        return \`
          <div class="file-card" onclick="previewFile('\${escapeHtml(f.name)}', '\${f.type}', '\${escapeHtml(f.path)}')" data-search="\${escapeHtml(f.displayName.toLowerCase())}">
            <div class="file-icon \${info.cls}">\${info.icon}</div>
            <div class="file-info">
              <div class="file-name" title="\${escapeHtml(f.displayName)}">\${escapeHtml(f.displayName)}</div>
              <span class="file-type-badge">.\${f.type}</span>
            </div>
            <div class="file-actions">
              \${previewBtn}
              <a class="btn btn-download" href="\${f.path}" download="\${escapeHtml(f.name)}" onclick="event.stopPropagation(); showToast('\u5F00\u59CB\u4E0B\u8F7D\uFF1A\${escapeHtml(f.displayName)}')">\u2B07 \u4E0B\u8F7D</a>
            </div>
          </div>\`;
      }).join('');
    }

    function escapeHtml(str) {
      if (!str) return '';
      return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    // ==================== \u641C\u7D22\u8FC7\u6EE4 ====================
    function filterFiles() {
      const query = document.getElementById('searchInput').value.toLowerCase().trim();
      if (!query) {
        renderFiles(allFiles);
        return;
      }
      const filtered = allFiles.filter(f =>
        f.displayName.toLowerCase().includes(query) ||
        f.type.toLowerCase().includes(query)
      );
      renderFiles(filtered);
    }

    // ==================== \u6587\u4EF6\u9884\u89C8 ====================
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
        body.innerHTML = \`
          <div class="empty-state">
            <div class="empty-icon">\u{1F4C4}</div>
            <h3>\u6B64\u6587\u4EF6\u7C7B\u578B\u6682\u4E0D\u652F\u6301\u5728\u7EBF\u9884\u89C8</h3>
            <p>\u8BF7\u70B9\u51FB\u4E0B\u65B9\u6309\u94AE\u4E0B\u8F7D\u6587\u4EF6\u540E\u67E5\u770B</p>
          </div>\`;
        return;
      }

      // Show loading
      body.innerHTML = '<div class="loading-spinner"><div class="spinner"></div></div>';

      try {
        if (type === 'txt') {
          const resp = await fetch(path);
          if (!resp.ok) throw new Error('\u52A0\u8F7D\u5931\u8D25');
          const text = await resp.text();
          body.innerHTML = \`<pre>\${escapeHtml(text)}</pre>\`;
        } else if (type === 'pdf') {
          body.innerHTML = \`<iframe src="\${path}#toolbar=1&navpanes=1" allowfullscreen></iframe>\`;
        } else if (['jpg','jpeg','png','gif','webp'].includes(type)) {
          body.innerHTML = \`<div style="padding:20px;text-align:center;width:100%;"><img src="\${path}" alt="\${escapeHtml(name)}" style="max-width:100%;max-height:70vh;border-radius:8px;box-shadow:0 2px 12px rgba(0,0,0,0.1);"></div>\`;
        } else if (type === 'mp4') {
          body.innerHTML = \`<div style="padding:20px;text-align:center;width:100%;"><video controls style="max-width:100%;max-height:70vh;border-radius:8px;"><source src="\${path}" type="video/mp4">\u60A8\u7684\u6D4F\u89C8\u5668\u4E0D\u652F\u6301\u89C6\u9891\u64AD\u653E</video></div>\`;
        } else if (type === 'mp3') {
          body.innerHTML = \`<div style="padding:40px 20px;text-align:center;width:100%;"><audio controls style="width:100%;max-width:400px;"><source src="\${path}" type="audio/mpeg">\u60A8\u7684\u6D4F\u89C8\u5668\u4E0D\u652F\u6301\u97F3\u9891\u64AD\u653E</audio></div>\`;
        }
      } catch (err) {
        body.innerHTML = \`
          <div class="empty-state">
            <div class="empty-icon">\u26A0\uFE0F</div>
            <h3>\u9884\u89C8\u5931\u8D25</h3>
            <p>\u8BF7\u5C1D\u8BD5\u4E0B\u8F7D\u6587\u4EF6\u540E\u67E5\u770B</p>
          </div>\`;
      }
    }

    // ==================== \u5173\u95ED\u5F39\u7A97 ====================
    function closeModal(e) {
      if (e && e.target !== document.getElementById('modalOverlay')) return;
      document.getElementById('modalOverlay').classList.remove('active');
      document.body.style.overflow = '';
      document.getElementById('modalBody').innerHTML = '';
    }

    // \u952E\u76D8\u5FEB\u6377\u952E\uFF1AESC \u5173\u95ED\u5F39\u7A97
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

    // ==================== Toast ====================
    function showToast(msg) {
      const toast = document.getElementById('toast');
      toast.textContent = msg;
      toast.classList.add('show');
      clearTimeout(toast._timeout);
      toast._timeout = setTimeout(() => toast.classList.remove('show'), 2000);
    }

    // ==================== \u521D\u59CB\u5316 ====================
    loadFiles();
  <\/script>
</body>
</html>`;
}
__name(getHTML, "getHTML");
export {
  index_default as default
};
//# sourceMappingURL=index.js.map

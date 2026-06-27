const fs = require('fs');
const path = require('path');

const fileDir = path.join(__dirname, '..', 'public', 'file');
const manifestPath = path.join(__dirname, '..', 'public', 'manifest.json');

// Ensure public directory exists
const publicDir = path.join(__dirname, '..', 'public');
if (!fs.existsSync(publicDir)) {
  fs.mkdirSync(publicDir, { recursive: true });
}

// Ensure file directory exists
if (!fs.existsSync(fileDir)) {
  fs.mkdirSync(fileDir, { recursive: true });
}

// Read all files, filter by supported extensions
const supportedExts = ['.txt', '.md', '.pdf', '.docx', '.xlsx', '.pptx', '.doc', '.xls', '.ppt', '.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.mp3', '.zip'];
const files = fs.readdirSync(fileDir).filter(f => {
  const ext = path.extname(f).toLowerCase();
  return supportedExts.includes(ext) && !f.startsWith('.') && !f.startsWith('_');
});

const manifest = files.map(f => {
  const ext = path.extname(f).slice(1).toLowerCase();
  const displayName = path.basename(f, path.extname(f));
  return {
    name: f,
    displayName: displayName,
    type: ext,
    path: `/file/${encodeURIComponent(f)}`
  };
});

// Sort alphabetically by displayName
manifest.sort((a, b) => a.displayName.localeCompare(b.displayName, 'zh-CN'));

fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2), 'utf-8');
console.log(`✅ 文件清单已生成，共 ${manifest.length} 个文件。`);
manifest.forEach(f => console.log(`   📄 ${f.displayName}.${f.type}`));

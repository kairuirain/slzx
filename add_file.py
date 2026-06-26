#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
四川省双流中学 初2024级7班 班委会文件管理系统 — 文件管理工具 (PyQt5)

用法：
  1. 将文件拖拽到此脚本图标上（支持多文件）
  2. 双击运行 → 在窗口中拖入文件或点击按钮选择
  3. 命令行：python add_file.py "文件路径1" "文件路径2" ...

功能：
  - 文件增删、清单生成、一键部署
"""

import os
import sys
import json
import shutil
import subprocess
import urllib.parse
from pathlib import Path

# ==================== 配置 ====================
BASE_DIR = Path(__file__).resolve().parent
FILE_DIR = BASE_DIR / "public" / "file"
MANIFEST_PATH = BASE_DIR / "public" / "manifest.json"

SUPPORTED_EXTS = {
    ".txt", ".pdf", ".docx", ".doc", ".xlsx", ".xls",
    ".pptx", ".ppt", ".jpg", ".jpeg", ".png", ".gif",
    ".webp", ".mp4", ".mp3", ".zip"
}

FILE_TYPE_ICONS = {
    "pdf": "📕", "txt": "📘", "docx": "📙", "doc": "📙",
    "xlsx": "📗", "xls": "📗", "pptx": "📒", "ppt": "📒",
    "jpg": "🖼️", "jpeg": "🖼️", "png": "🖼️", "gif": "🖼️",
    "webp": "🖼️", "mp4": "🎬", "mp3": "🎵", "zip": "📦",
}

# ==================== 工具函数 ====================

def ensure_dirs():
    FILE_DIR.mkdir(parents=True, exist_ok=True)


def get_file_type(ext: str) -> str:
    return ext.lower().lstrip(".")


def get_file_icon(ftype: str) -> str:
    return FILE_TYPE_ICONS.get(ftype, "📄")


def copy_file_to_public(src: Path) -> bool:
    """复制文件到 public/file/，返回是否成功"""
    if not src.is_file():
        return False
    ext = src.suffix.lower()
    if ext not in SUPPORTED_EXTS:
        return False
    try:
        shutil.copy2(src, FILE_DIR / src.name)
        return True
    except Exception:
        return False


def delete_file_from_public(filename: str) -> bool:
    """从 public/file/ 删除文件"""
    target = FILE_DIR / filename
    if target.exists():
        target.unlink()
        return True
    return False


def load_manifest() -> list:
    """加载当前清单"""
    if MANIFEST_PATH.exists():
        try:
            return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def save_manifest(files: list):
    """保存清单"""
    MANIFEST_PATH.write_text(
        json.dumps(files, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def generate_manifest() -> list:
    """扫描 public/file/ 目录生成清单"""
    file_list = []
    if FILE_DIR.exists():
        for f in sorted(FILE_DIR.iterdir()):
            if not f.is_file():
                continue
            if f.name.startswith('.') or f.name.startswith('_'):
                continue
            ext = f.suffix.lower()
            if ext not in SUPPORTED_EXTS:
                continue
            ftype = get_file_type(ext)
            file_list.append({
                "name": f.name,
                "displayName": f.stem,
                "type": ftype,
                "path": f"/file/{urllib.parse.quote(f.name, safe='')}"
            })
    file_list.sort(key=lambda x: x["displayName"])
    save_manifest(file_list)
    return file_list


# ==================== PyQt5 界面 ====================

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
        QLabel, QStatusBar, QMessageBox, QProgressBar, QSplitter,
        QAbstractItemView, QMenu, QFileDialog, QStyle, QFrame,
        QTextEdit,
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QUrl
    from PyQt5.QtGui import QFont, QColor, QPalette, QDragEnterEvent, QDropEvent, QIcon
    from PyQt5.QtWidgets import QDesktopWidget
except ImportError:
    print("请先安装 PyQt5：pip install PyQt5")
    sys.exit(1)


class DeployWorker(QThread):
    """后台部署线程（实时输出）"""
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)

    def run(self):
        self._log("══════════════════════════════════")
        self._log("  Cloudflare Workers 部署日志")
        self._log("══════════════════════════════════")
        self._log("")
        self._log("> wrangler deploy")
        self._log("")

        try:
            # Windows 下使用 shell=True 并指定 UTF-8 编码
            proc = subprocess.Popen(
                "wrangler deploy",
                cwd=str(BASE_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )

            output_lines = []
            deploy_url = None

            for line in proc.stdout:
                line = line.rstrip("\n\r")
                output_lines.append(line)
                self._log(line)

                # 检测部署 URL
                if "https://" in line and "workers.dev" in line:
                    for part in line.strip().split():
                        if part.startswith("https://") and "workers.dev" in part:
                            deploy_url = part

            proc.wait(timeout=180)

            self._log("")
            self._log("──────────────────────────────")

            if proc.returncode == 0:
                if deploy_url:
                    self._log(f"✅ 部署成功！")
                    self._log(f"   {deploy_url}")
                    self.finished_signal.emit(True, f"部署成功！\n{deploy_url}")
                else:
                    self._log("✅ 部署成功！")
                    self.finished_signal.emit(True, "部署成功！")
            else:
                self._log(f"❌ 部署失败 (退出码: {proc.returncode})")
                self.finished_signal.emit(False, f"部署失败，退出码: {proc.returncode}")

        except subprocess.TimeoutExpired:
            self._log("❌ 部署超时（180秒）")
            self.finished_signal.emit(False, "部署超时（超过180秒）")
        except FileNotFoundError:
            self._log("❌ 未找到 wrangler 命令，请确保已安装 Cloudflare Wrangler")
            self.finished_signal.emit(False, "未找到 wrangler 命令")
        except Exception as e:
            self._log(f"❌ 部署出错: {str(e)}")
            self.finished_signal.emit(False, f"部署出错: {str(e)}")

    def _log(self, msg: str):
        """发送日志到 GUI 并同步输出到控制台"""
        print(msg)
        self.log_signal.emit(msg)


class GitWorker(QThread):
    """后台 Git 提交推送线程（实时输出）"""
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    need_commit_msg = pyqtSignal()

    def __init__(self, commit_msg: str = ""):
        super().__init__()
        self.commit_msg = commit_msg

    def run(self):
        self._log("══════════════════════════════════")
        self._log("  Git 提交 & 推送日志")
        self._log("══════════════════════════════════")
        self._log("")
        self._log(f"  远程仓库: origin")
        self._log(f"  分支: main")
        self._log("")

        try:
            # 步骤1: git add .
            self._log("──── 第 1 步：git add . ────")
            proc = subprocess.Popen(
                "git add .",
                cwd=str(BASE_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )
            for line in proc.stdout:
                line = line.rstrip("\n\r")
                if line.strip():
                    self._log(f"  {line}")
            proc.wait(timeout=60)
            if proc.returncode != 0:
                self._log(f"❌ git add 失败 (退出码: {proc.returncode})")
                self.finished_signal.emit(False, "git add 失败")
                return
            self._log("✅ 暂存完成")
            self._log("")

            # 步骤2: git commit
            self._log("──── 第 2 步：git commit ────")
            self._log(f"> git commit -m \"{self.commit_msg}\"")
            proc = subprocess.Popen(
                f'git commit -m "{self.commit_msg}"',
                cwd=str(BASE_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )
            for line in proc.stdout:
                line = line.rstrip("\n\r")
                if line.strip():
                    self._log(f"  {line}")
            proc.wait(timeout=60)
            if proc.returncode != 0:
                # "nothing to commit" 不算失败
                self._log("ℹ️ 没有需要提交的更改（可能已是最新）")
            else:
                self._log("✅ 提交完成")
            self._log("")

            # 步骤3: git push
            self._log("──── 第 3 步：git push ────")
            self._log("> git push")
            proc = subprocess.Popen(
                "git push",
                cwd=str(BASE_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )
            push_output = []
            for line in proc.stdout:
                line = line.rstrip("\n\r")
                if line.strip():
                    self._log(f"  {line}")
                    push_output.append(line)
            proc.wait(timeout=120)

            self._log("")
            self._log("──────────────────────────────")

            if proc.returncode == 0:
                self._log("✅ Git 提交与推送成功！")
                self.finished_signal.emit(True, "Git 提交与推送成功！")
            else:
                self._log(f"❌ git push 失败 (退出码: {proc.returncode})")
                self.finished_signal.emit(False, "git push 失败，请检查远程仓库权限")

        except subprocess.TimeoutExpired:
            self._log("❌ 操作超时")
            self.finished_signal.emit(False, "Git 操作超时")
        except FileNotFoundError:
            self._log("❌ 未找到 git 命令，请确保已安装 Git")
            self.finished_signal.emit(False, "未找到 git 命令")
        except Exception as e:
            self._log(f"❌ 操作出错: {str(e)}")
            self.finished_signal.emit(False, f"Git 操作出错: {str(e)}")

    def _log(self, msg: str):
        print(msg)
        self.log_signal.emit(msg)


class DeployLogWindow(QMainWindow):
    """独立的部署/操作日志窗口"""

    def __init__(self, parent=None, title="操作日志"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(750, 520)
        self.setMinimumSize(500, 350)
        self.setAttribute(Qt.WA_DeleteOnClose)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # 日志输出区域
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setFont(QFont("Consolas", 10))
        self.log_edit.setStyleSheet("""
            QTextEdit {
                background: #1a1a2e;
                color: #a0d2db;
                border: 1px solid #2d2d44;
                border-radius: 8px;
                padding: 10px;
            }
            QScrollBar:vertical {
                background: #1a1a2e;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #3d3d5c;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)
        layout.addWidget(self.log_edit)

        # 底部按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.lbl_status = QLabel("等待开始...")
        self.lbl_status.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        btn_layout.addWidget(self.lbl_status)

        self.btn_close = QPushButton("关闭")
        self.btn_close.setEnabled(False)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background: #3d3d5c; color: #a0d2db;
                border: none; border-radius: 6px;
                padding: 8px 24px; font-size: 13px;
            }
            QPushButton:hover { background: #4d4d7c; }
            QPushButton:disabled { background: #2a2a3a; color: #5a5a7a; }
        """)
        self.btn_close.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_close)

        layout.addLayout(btn_layout)

        # 居中于屏幕
        try:
            screen = QApplication.desktop().screenGeometry()
            self.move(
                (screen.width() - self.width()) // 2,
                (screen.height() - self.height()) // 2
            )
        except Exception:
            pass

    def append_log(self, msg: str):
        """追加日志行"""
        # 彩色高亮不同行类型
        color = "#a0d2db"
        if msg.startswith("✅"):
            color = "#00e676"
        elif msg.startswith("❌"):
            color = "#ff5252"
        elif msg.startswith("⚠"):
            color = "#ffd740"
        elif msg.startswith("🚀") or msg.startswith("📋"):
            color = "#448aff"
        elif msg.startswith("═") or msg.startswith("─"):
            color = "#5a5a7a"
        elif msg.startswith(">"):
            color = "#ffab40"

        self.log_edit.append(f'<span style="color:{color};">{self._escape(msg)}</span>')

        # 自动滚动到底部
        bar = self.log_edit.verticalScrollBar()
        bar.setValue(bar.maximum())

    def set_finished(self, success: bool):
        """标记部署完成"""
        self.btn_close.setEnabled(True)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background: #2980b9; color: white;
                border: none; border-radius: 6px;
                padding: 8px 24px; font-size: 13px; font-weight: bold;
            }
            QPushButton:hover { background: #1a5276; }
        """)
        status = "✅ 部署完成" if success else "❌ 部署失败"
        self.lbl_status.setText(status)
        self.lbl_status.setStyleSheet(
            "color: #00e676; font-size: 13px; font-weight: bold;"
            if success else
            "color: #ff5252; font-size: 13px; font-weight: bold;"
        )

    @staticmethod
    def _escape(text: str) -> str:
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class DropFrame(QFrame):
    """支持拖放文件的容器"""
    files_dropped = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Sunken)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("DropFrame { border: 2px dashed #2980b9; background: #eaf2f8; }")

    def dragLeaveEvent(self, event):
        self.setStyleSheet("")

    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet("")
        paths = []
        for url in event.mimeData().urls():
            p = url.toLocalFile()
            if p:
                paths.append(p)
        if paths:
            self.files_dropped.emit(paths)


class FileManagerWindow(QMainWindow):
    def __init__(self, init_files: list = None):
        super().__init__()
        self.setWindowTitle("四川省双流中学 初2024级7班 · 文件管理系统")
        self.resize(900, 600)
        self.setMinimumSize(700, 450)

        # 居中显示
        try:
            screen = QApplication.desktop().screenGeometry()
        except Exception:
            screen = None
        if screen:
            self.move(
                (screen.width() - self.width()) // 2,
                (screen.height() - self.height()) // 2
            )

        try:
            self._build_ui()
        except Exception as e:
            print(f"界面构建失败: {e}")
            import traceback
            traceback.print_exc()
            raise
        self._load_data()

        # 处理拖拽到图标传入的文件
        if init_files:
            QTimer.singleShot(300, lambda files=init_files: self._add_files(files))

    # ── 界面构建 ──

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(8)

        # 顶部标题
        title = QLabel("📂 班委会文件管理工具")
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1a5276; padding: 6px;")
        root_layout.addWidget(title)

        # 说明标签
        hint = QLabel("拖拽文件到此窗口  或  点击下方按钮选择文件")
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet("color: #7f8c8d; font-size: 13px; margin-bottom: 4px;")
        root_layout.addWidget(hint)

        # 拖放区域 + 文件表格
        splitter = QSplitter(Qt.Vertical)

        self.drop_frame = QVBoxLayout()
        self.drop_frame.setContentsMargins(0, 0, 0, 0)
        drop_widget = QWidget()
        drop_widget.setLayout(self.drop_frame)
        splitter.addWidget(drop_widget)

        # 文件表格
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["图标", "文件名", "类型", "操作"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._on_context_menu)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(2, 70)
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e1e8f0;
                border-radius: 6px;
                gridline-color: #f0f0f0;
                font-size: 13px;
            }
            QTableWidget::item { padding: 4px 8px; }
            QHeaderView::section {
                background: #f5f7fa;
                border: none;
                border-bottom: 2px solid #e1e8f0;
                padding: 8px;
                font-weight: bold;
                color: #2c3e50;
            }
            QTableWidget::item:selected {
                background: #d4e6f1;
                color: #1a5276;
            }
        """)

        self.drop_frame.addWidget(self.table)

        root_layout.addWidget(splitter)

        # 底部按钮栏
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_add = QPushButton("＋ 添加文件")
        self.btn_add.setStyleSheet(self._btn_style("#2980b9", "#1a5276"))
        self.btn_add.clicked.connect(self._on_add_files)
        self.btn_add.setMinimumHeight(36)
        btn_layout.addWidget(self.btn_add)

        self.btn_delete = QPushButton("🗑 删除选中")
        self.btn_delete.setStyleSheet(self._btn_style("#e74c3c", "#c0392b"))
        self.btn_delete.clicked.connect(self._on_delete_files)
        self.btn_delete.setMinimumHeight(36)
        btn_layout.addWidget(self.btn_delete)

        self.btn_refresh = QPushButton("🔄 刷新清单")
        self.btn_refresh.setStyleSheet(self._btn_style("#27ae60", "#1e8449"))
        self.btn_refresh.clicked.connect(self._load_data)
        self.btn_refresh.setMinimumHeight(36)
        btn_layout.addWidget(self.btn_refresh)

        btn_layout.addStretch()

        self.lbl_count = QLabel("共 0 个文件")
        self.lbl_count.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        btn_layout.addWidget(self.lbl_count)

        self.btn_git = QPushButton("📤 提交并推送")
        self.btn_git.setStyleSheet(self._btn_style("#8e44ad", "#6c3483"))
        self.btn_git.clicked.connect(self._on_git_push)
        self.btn_git.setMinimumHeight(36)
        btn_layout.addWidget(self.btn_git)

        self.btn_deploy = QPushButton("🚀 部署到 Cloudflare")
        self.btn_deploy.setStyleSheet(self._btn_style("#1a5276", "#0d344a"))
        self.btn_deploy.clicked.connect(self._on_deploy)
        self.btn_deploy.setMinimumHeight(36)
        btn_layout.addWidget(self.btn_deploy)

        root_layout.addLayout(btn_layout)

        # 状态栏
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("就绪")
        self.setStatusBar(self.status_bar)

        # 进度条
        self.progress = QProgressBar()
        self.progress.setMaximumWidth(200)
        self.progress.setMaximumHeight(18)
        self.progress.hide()
        self.status_bar.addPermanentWidget(self.progress)

        # 应用全局样式
        self.setStyleSheet("""
            QMainWindow { background: #f8f9fb; }
            QLabel { font-family: "Microsoft YaHei", "PingFang SC", sans-serif; }
        """)

    @staticmethod
    def _btn_style(bg, hover_bg):
        return f"""
            QPushButton {{
                background: {bg};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 16px;
                font-size: 13px;
                font-weight: bold;
                font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
            }}
            QPushButton:hover {{
                background: {hover_bg};
            }}
            QPushButton:pressed {{
                background: {hover_bg};
                padding: 7px 16px 5px 16px;
            }}
            QPushButton:disabled {{
                background: #bdc3c7;
                color: #ecf0f1;
            }}
        """

    # ── 数据与渲染 ──

    def _load_data(self):
        """加载文件清单并刷新表格"""
        self._manifest = generate_manifest()
        self._refresh_table()
        n = len(self._manifest)
        self.lbl_count.setText(f"共 {n} 个文件")
        self.status_bar.showMessage(f"清单已刷新，共 {n} 个文件")

    def _refresh_table(self):
        """刷新表格内容"""
        files = self._manifest
        self.table.setRowCount(len(files))
        for row, f in enumerate(files):
            # 图标
            icon_item = QTableWidgetItem(get_file_icon(f["type"]))
            icon_item.setTextAlignment(Qt.AlignCenter)
            icon_item.setFont(QFont("Segoe UI Emoji", 14))
            self.table.setItem(row, 0, icon_item)

            # 文件名
            name_item = QTableWidgetItem(f["displayName"])
            name_item.setToolTip(f"{f['displayName']}.{f['type']}")
            self.table.setItem(row, 1, name_item)

            # 类型徽章
            type_item = QTableWidgetItem(f" .{f['type']} ")
            type_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, type_item)

            # 操作按钮
            op_widget = QWidget()
            op_layout = QHBoxLayout(op_widget)
            op_layout.setContentsMargins(4, 2, 4, 2)
            op_layout.setSpacing(6)

            btn_del = QPushButton("删除")
            btn_del.setFixedSize(50, 26)
            btn_del.setStyleSheet(f"""
                QPushButton {{
                    background: #fdecea; color: #e74c3c;
                    border: 1px solid #f5c6cb; border-radius: 4px;
                    font-size: 12px;
                }}
                QPushButton:hover {{ background: #e74c3c; color: white; }}
            """)
            btn_del.clicked.connect(lambda checked, fn=f["name"]: self._delete_single(fn))
            op_layout.addWidget(btn_del)

            op_layout.addStretch()
            self.table.setCellWidget(row, 3, op_widget)

    # ── 文件增删 ──

    def _add_files(self, path_strings: list):
        """批量添加文件"""
        added = 0
        skipped = []
        for p_str in path_strings:
            src = Path(p_str.strip('"\''))
            if not src.exists():
                skipped.append(f"{src.name} (不存在)")
                continue
            if src.is_file():
                if copy_file_to_public(src):
                    added += 1
                else:
                    skipped.append(f"{src.name} (不支持的类型)")
            else:
                skipped.append(f"{src.name} (不是文件)")

        self._load_data()
        msg = f"成功添加 {added} 个文件。"
        if skipped:
            msg += f"\n跳过: {', '.join(skipped[:5])}"
            if len(skipped) > 5:
                msg += f" 等共 {len(skipped)} 项"
        self.status_bar.showMessage(msg)

    def _on_add_files(self):
        """点击添加文件按钮"""
        paths, _ = QFileDialog.getOpenFileNames(
            self, "选择要添加的文件",
            "",
            "所有支持的文件 ("
            "*.txt *.pdf *.docx *.doc *.xlsx *.xls *.pptx *.ppt "
            "*.jpg *.jpeg *.png *.gif *.webp *.mp4 *.mp3 *.zip"
            ");;所有文件 (*.*)"
        )
        if paths:
            self._add_files(paths)

    def _delete_single(self, filename: str):
        """删除单个文件"""
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除「{filename}」吗？\n此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            delete_file_from_public(filename)
            self._load_data()
            self.status_bar.showMessage(f"已删除: {filename}")

    def _on_delete_files(self):
        """删除选中行"""
        rows = set(idx.row() for idx in self.table.selectedIndexes())
        if not rows:
            QMessageBox.information(self, "提示", "请先选择要删除的文件。")
            return

        filenames = [self._manifest[r]["name"] for r in sorted(rows, reverse=True)]
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除 {len(filenames)} 个文件吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            for fn in filenames:
                delete_file_from_public(fn)
            self._load_data()
            self.status_bar.showMessage(f"已删除 {len(filenames)} 个文件")

    def _on_context_menu(self, pos):
        """右键菜单"""
        menu = QMenu()
        action_del = menu.addAction("🗑 删除选中")
        action_del.triggered.connect(self._on_delete_files)
        menu.exec_(self.table.viewport().mapToGlobal(pos))

    # ── 部署 ──

    def _on_deploy(self):
        """部署到 Cloudflare Workers"""
        reply = QMessageBox.question(
            self, "确认部署",
            "即将部署到 Cloudflare Workers (slzx)。\n请确保已登录 Wrangler 且网络畅通。\n\n继续？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        if reply != QMessageBox.Yes:
            return

        # 先确保清单是最新的
        self._load_data()

        # 打开日志窗口
        self.log_window = DeployLogWindow(self, title="部署日志 — Cloudflare Workers")
        self.log_window.show()

        self.btn_deploy.setEnabled(False)
        self.btn_deploy.setText("⏳ 部署中...")
        self.progress.setRange(0, 0)
        self.progress.show()
        self.status_bar.showMessage("正在部署，详见日志窗口...")

        self.worker = DeployWorker()
        self.worker.log_signal.connect(self.log_window.append_log)
        self.worker.finished_signal.connect(self._on_deploy_finished)
        self.worker.start()

    def _on_deploy_finished(self, success: bool, message: str):
        self.btn_deploy.setEnabled(True)
        self.btn_deploy.setText("🚀 部署到 Cloudflare")
        self.progress.hide()
        self.status_bar.showMessage(message)

        if hasattr(self, 'log_window') and self.log_window:
            self.log_window.set_finished(success)

    # ── Git 提交与推送 ──

    def _on_git_push(self):
        """Git 提交并推送到远程仓库"""
        # 弹出提交信息输入框
        from PyQt5.QtWidgets import QInputDialog
        commit_msg, ok = QInputDialog.getText(
            self, "提交信息",
            "请输入本次提交的描述信息：",
            text="更新文件"
        )
        if not ok or not commit_msg.strip():
            return

        commit_msg = commit_msg.strip()

        reply = QMessageBox.question(
            self, "确认提交",
            f"即将执行以下操作：\n\n"
            f"  1. git add .\n"
            f"  2. git commit -m \"{commit_msg}\"\n"
            f"  3. git push\n\n"
            f"远程仓库: origin/main\n\n"
            f"继续？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        if reply != QMessageBox.Yes:
            return

        # 先确保清单是最新的
        self._load_data()

        # 打开日志窗口
        self.git_log_window = DeployLogWindow(self, title="Git 提交日志")
        self.git_log_window.show()

        self.btn_git.setEnabled(False)
        self.btn_git.setText("⏳ 推送中...")
        self.progress.setRange(0, 0)
        self.progress.show()
        self.status_bar.showMessage("正在提交到 Git...")

        self.git_worker = GitWorker(commit_msg)
        self.git_worker.log_signal.connect(self.git_log_window.append_log)
        self.git_worker.finished_signal.connect(self._on_git_finished)
        self.git_worker.start()

    def _on_git_finished(self, success: bool, message: str):
        self.btn_git.setEnabled(True)
        self.btn_git.setText("📤 提交并推送")
        self.progress.hide()
        self.status_bar.showMessage(message)

        if hasattr(self, 'git_log_window') and self.git_log_window:
            self.git_log_window.set_finished(success)


# ==================== 入口 ====================

def main():
    ensure_dirs()

    app = QApplication(sys.argv)
    app.setApplicationName("SLZX-FileManager")
    app.setStyle("Fusion")

    # 设置 Fusion 调色板
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#f8f9fb"))
    palette.setColor(QPalette.WindowText, QColor("#2c3e50"))
    palette.setColor(QPalette.Highlight, QColor("#2980b9"))
    app.setPalette(palette)

    # 收集命令行传入的文件（拖拽到图标）
    init_files = []
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            init_files.append(arg)

    window = FileManagerWindow(init_files if init_files else None)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # 确保错误信息能在闪退后可见
        import traceback
        traceback.print_exc()
        print(f"\n程序崩溃: {e}")
        # 尝试用消息框显示错误
        try:
            from PyQt5.QtWidgets import QApplication, QMessageBox
            app = QApplication(sys.argv[:1])
            QMessageBox.critical(None, "程序错误", f"发生未处理的异常:\n\n{str(e)}\n\n详情请查看控制台输出。")
        except Exception:
            pass
        input("\n按回车键退出...")

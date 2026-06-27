#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
四川省双流中学 初2024级7班 班委会 — 后台管理工具 (PyQt5)

功能：
  通知管理 — 新建/编辑/删除通知，支持 Markdown 内容，存储到 public/notices.json
  文件管理 — 拖拽上传 Word/PDF/TXT/MD 文件，自动生成清单，部署与 Git 推送

用法：
  1. 双击运行 → 图形化管理界面
  2. 将文件拖拽到图标上自动导入文件管理（支持多文件）
"""

import os
import sys
import json
import shutil
import subprocess
import urllib.parse
from datetime import date
from pathlib import Path

# ==================== 配置 ====================
BASE_DIR = Path(__file__).resolve().parent
FILE_DIR = BASE_DIR / "public" / "file"
MANIFEST_PATH = BASE_DIR / "public" / "manifest.json"
NOTICES_PATH = BASE_DIR / "public" / "notices.json"

# 文件管理支持的格式（限制为 word/pdf/txt/md）
SUPPORTED_EXTS = {".docx", ".doc", ".pdf", ".txt", ".md"}

FILE_TYPE_ICONS = {
    "pdf": "📕", "txt": "📘", "docx": "📙", "doc": "📙",
    "md": "📝", "xlsx": "📗", "xls": "📗",
    "jpg": "🖼️", "jpeg": "🖼️", "png": "🖼️", "gif": "🖼️",
    "webp": "🖼️", "mp4": "🎬", "mp3": "🎵", "zip": "📦",
}

EXT_LABELS = {
    ".txt": "文本文件 (*.txt)",
    ".md": "Markdown (*.md)",
    ".pdf": "PDF 文档 (*.pdf)",
    ".docx": "Word 文档 (*.docx)",
    ".doc": "Word 文档 (*.doc)",
}

# ==================== 工具函数 ====================

def ensure_dirs():
    FILE_DIR.mkdir(parents=True, exist_ok=True)


def get_file_type(ext: str) -> str:
    return ext.lower().lstrip(".")


def get_file_icon(ftype: str) -> str:
    return FILE_TYPE_ICONS.get(ftype, "📄")


def copy_file_to_public(src: Path) -> bool:
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
    target = FILE_DIR / filename
    if target.exists():
        target.unlink()
        return True
    return False


def generate_manifest() -> list:
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
    MANIFEST_PATH.write_text(
        json.dumps(file_list, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    return file_list


def load_notices() -> dict:
    if NOTICES_PATH.exists():
        try:
            return json.loads(NOTICES_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"notices": []}


def save_notices(data: dict):
    NOTICES_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


# ==================== 智能提交信息生成 ====================

def get_staged_diff() -> dict:
    """获取暂存区的 diff 摘要，返回 {stat: str, files: list}"""
    result = {"stat": "", "files": [], "changed_notices": False,
              "changed_manifest": False, "changed_code": False}
    try:
        # 获取文件变更摘要
        proc = subprocess.run(
            "git diff --staged --stat", cwd=str(BASE_DIR),
            capture_output=True, text=True, shell=True, timeout=30,
            encoding="utf-8", errors="replace"
        )
        result["stat"] = proc.stdout.strip()

        # 获取文件变更列表
        proc2 = subprocess.run(
            "git diff --staged --name-status", cwd=str(BASE_DIR),
            capture_output=True, text=True, shell=True, timeout=30,
            encoding="utf-8", errors="replace"
        )
        for line in proc2.stdout.strip().splitlines():
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                status, filename = parts[0].strip(), parts[1].strip()
                result["files"].append({"status": status, "name": filename})
                # 分类
                if "notices.json" in filename:
                    result["changed_notices"] = True
                elif "manifest.json" in filename:
                    result["changed_manifest"] = True
                elif filename.endswith((".js", ".py", ".toml", ".json", ".css", ".html")):
                    result["changed_code"] = True
    except Exception:
        pass
    return result


def generate_commit_message(diff_data: dict) -> str:
    """根据 diff 数据智能生成提交信息"""
    files = diff_data.get("files", [])
    if not files:
        return "更新文件与通知"

    added = []
    modified = []
    deleted = []
    notice_files = []
    code_files = []

    for f in files:
        name = f["name"]
        status = f["status"]
        basename = name.split("/")[-1] if "/" in name else name

        if "notices.json" in name:
            notice_files.append(basename)
        elif basename.endswith((".js", ".py", ".toml", ".json", ".bat")):
            if status == "A":
                added.append(basename)
            elif status == "D":
                deleted.append(basename)
            else:
                code_files.append(basename)
        elif basename.startswith("."):
            continue  # 忽略隐藏文件
        elif status == "A":
            # 提取文件名主体（去掉扩展名）
            stem = basename.rsplit(".", 1)[0] if "." in basename else basename
            added.append(stem)
        elif status == "D":
            stem = basename.rsplit(".", 1)[0] if "." in basename else basename
            deleted.append(stem)
        else:
            stem = basename.rsplit(".", 1)[0] if "." in basename else basename
            modified.append(stem)

    parts = []

    # 通知变更
    if diff_data["changed_notices"] or notice_files:
        parts.append("更新通知")

    # 文件变更
    file_changes = []
    if added:
        names = _smart_join(added[:4])
        suffix = "等" if len(added) > 4 else ""
        file_changes.append(f"新增: {names}{suffix}")
    if deleted:
        names = _smart_join(deleted[:4])
        suffix = "等" if len(deleted) > 4 else ""
        file_changes.append(f"移除: {names}{suffix}")
    if modified:
        names = _smart_join(modified[:4])
        suffix = "等" if len(modified) > 4 else ""
        file_changes.append(f"更新: {names}{suffix}")

    # 代码变更
    if code_files and not (added or deleted or modified):
        names = _smart_join(code_files[:4])
        suffix = "等" if len(code_files) > 4 else ""
        parts.append(f"更新代码: {names}{suffix}")

    if file_changes:
        parts.append("；".join(file_changes))

    # 如果只有代码文件变更且没有其他分类
    if diff_data["changed_code"] and not file_changes and not parts:
        parts.append("更新系统代码")

    if not parts:
        parts.append("更新文件")

    return "；".join(parts) if len(parts) > 1 else parts[0]


def _smart_join(names: list) -> str:
    """智能拼接名称列表"""
    if len(names) <= 2:
        return "、".join(names)
    return "、".join(names)


# ==================== 提交对话框 ====================

class CommitDialog(QDialog):
    """独立的提交确认窗口，展示 diff 摘要和智能生成的提交信息"""

    commit_confirmed = pyqtSignal(str)  # 发送最终提交信息

    def __init__(self, suggested_msg: str, diff_stat: str, file_list: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("提交代码变更 — Git Commit")
        self.resize(720, 560)
        self.setMinimumSize(550, 420)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setModal(True)

        self.suggested_msg = suggested_msg
        self.diff_stat = diff_stat
        self.file_list = file_list

        self._build_ui()
        self._center()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # 标题
        title = QLabel("📤 提交代码变更")
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        title.setStyleSheet("color: #1a5276;")
        layout.addWidget(title)

        # 变更摘要
        summary_group = QGroupBox("变更摘要")
        summary_group.setStyleSheet("""
            QGroupBox { font-weight: bold; color: #2c3e50; border: 1px solid #e1e8f0; border-radius: 8px; margin-top: 8px; padding-top: 16px; }
            QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }
        """)
        summary_layout = QVBoxLayout(summary_group)
        summary_layout.setContentsMargins(10, 12, 10, 10)

        # 文件列表
        if self.file_list:
            file_text = self._format_file_list()
            file_label = QLabel(file_text)
            file_label.setFont(QFont("Consolas", 10))
            file_label.setStyleSheet("color: #2c3e50; background: #f8f9fb; padding: 8px 12px; border-radius: 4px;")
            file_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            file_label.setWordWrap(True)
            summary_layout.addWidget(file_label)

        # diff 统计
        if self.diff_stat:
            stat_text = QPlainTextEdit()
            stat_text.setReadOnly(True)
            stat_text.setFont(QFont("Consolas", 9))
            stat_text.setMaximumHeight(100)
            stat_text.setStyleSheet("""
                QPlainTextEdit { background: #1a1a2e; color: #a0d2db; border: 1px solid #2d2d44; border-radius: 6px; padding: 8px; }
            """)
            stat_text.setPlainText(self.diff_stat)
            summary_layout.addWidget(stat_text)

        layout.addWidget(summary_group)

        # 提交信息
        msg_group = QGroupBox("提交信息")
        msg_group.setStyleSheet("""
            QGroupBox { font-weight: bold; color: #2c3e50; border: 1px solid #e1e8f0; border-radius: 8px; margin-top: 8px; padding-top: 16px; }
            QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }
        """)
        msg_layout = QVBoxLayout(msg_group)
        msg_layout.setContentsMargins(10, 12, 10, 10)

        # 提示标签
        hint_layout = QHBoxLayout()
        hint_icon = QLabel("💡")
        hint_label = QLabel("已根据文件变更智能生成提交信息，您可以修改后确认提交")
        hint_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        hint_layout.addWidget(hint_icon)
        hint_layout.addWidget(hint_label)
        hint_layout.addStretch()
        msg_layout.addLayout(hint_layout)

        # 编辑框
        self.msg_edit = QTextEdit()
        self.msg_edit.setPlainText(self.suggested_msg)
        self.msg_edit.setFont(QFont("Microsoft YaHei", 11))
        self.msg_edit.setMinimumHeight(80)
        self.msg_edit.setMaximumHeight(160)
        self.msg_edit.setStyleSheet("""
            QTextEdit { border: 2px solid #2980b9; border-radius: 6px; padding: 10px; background: #fafbfc; }
            QTextEdit:focus { border-color: #1a5276; }
        """)
        msg_layout.addWidget(self.msg_edit)

        # 操作提示
        ops_hint = QLabel("将会执行：git add . → git commit → git push  (远程仓库: origin/main)")
        ops_hint.setStyleSheet("color: #95a5a6; font-size: 11px; padding-left: 4px;")
        msg_layout.addWidget(ops_hint)

        layout.addWidget(msg_group)

        # 按钮栏
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_reset = QPushButton("🔄 重置为推荐")
        self.btn_reset.setStyleSheet(self._btn_style("#95a5a6", "#7f8c8d"))
        self.btn_reset.clicked.connect(lambda: self.msg_edit.setPlainText(self.suggested_msg))
        btn_layout.addWidget(self.btn_reset)

        btn_layout.addStretch()

        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.setStyleSheet(self._btn_style("#bdc3c7", "#95a5a6"))
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_commit = QPushButton("✅ 确认提交并推送")
        self.btn_commit.setStyleSheet("""
            QPushButton {
                background: #2980b9; color: white; border: none; border-radius: 6px;
                padding: 10px 24px; font-size: 14px; font-weight: bold;
                font-family: "Microsoft YaHei", sans-serif;
            }
            QPushButton:hover { background: #1a5276; }
        """)
        self.btn_commit.clicked.connect(self._on_confirm)
        btn_layout.addWidget(self.btn_commit)

        layout.addLayout(btn_layout)

    def _format_file_list(self) -> str:
        """格式化文件列表"""
        lines = []
        status_map = {"A": "➕ 新增", "M": "✏️ 修改", "D": "🗑 删除",
                      "R": "🔄 重命名", "C": "📋 复制", "T": "📝 类型变更"}
        for f in self.file_list:
            s = status_map.get(f["status"], f["status"])
            lines.append(f"  {s}  {f['name']}")
        return "\n".join(lines)

    def _on_confirm(self):
        msg = self.msg_edit.toPlainText().strip()
        if not msg:
            QMessageBox.warning(self, "提示", "请输入提交信息。")
            return
        self.accept()
        self.commit_confirmed.emit(msg)

    def _center(self):
        try:
            screen = QApplication.desktop().screenGeometry()
            self.move(
                (screen.width() - self.width()) // 2,
                (screen.height() - self.height()) // 2
            )
        except Exception:
            pass

    @staticmethod
    def _btn_style(bg, hover_bg):
        return f"""
            QPushButton {{
                background: {bg}; color: white; border: none; border-radius: 6px;
                padding: 8px 20px; font-size: 13px; font-weight: bold;
                font-family: "Microsoft YaHei", sans-serif;
            }}
            QPushButton:hover {{ background: {hover_bg}; }}
        """


# ==================== PyQt5 界面 ====================

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
        QLabel, QStatusBar, QMessageBox, QSplitter,
        QAbstractItemView, QMenu, QFileDialog, QFrame,
        QTextEdit, QLineEdit, QCheckBox, QTabWidget, QGroupBox,
        QFormLayout, QInputDialog, QProgressBar, QDialog, QDialogButtonBox,
        QPlainTextEdit,
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
    from PyQt5.QtGui import QFont, QColor, QPalette, QDragEnterEvent, QDropEvent
    from PyQt5.QtWidgets import QDesktopWidget
except ImportError:
    print("请先安装 PyQt5：pip install PyQt5")
    sys.exit(1)


# ==================== 后台线程 ====================

class DeployWorker(QThread):
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
                if "https://" in line and "workers.dev" in line:
                    for part in line.strip().split():
                        if part.startswith("https://") and "workers.dev" in part:
                            deploy_url = part
            proc.wait(timeout=180)
            self._log("")
            self._log("──────────────────────────────")
            if proc.returncode == 0:
                msg = f"部署成功！\n{deploy_url}" if deploy_url else "部署成功！"
                self._log(f"✅ {msg}")
                self.finished_signal.emit(True, msg)
            else:
                self._log(f"❌ 部署失败 (退出码: {proc.returncode})")
                self.finished_signal.emit(False, f"部署失败，退出码: {proc.returncode}")
        except subprocess.TimeoutExpired:
            self._log("❌ 部署超时（180秒）")
            self.finished_signal.emit(False, "部署超时")
        except FileNotFoundError:
            self._log("❌ 未找到 wrangler 命令")
            self.finished_signal.emit(False, "未找到 wrangler 命令")
        except Exception as e:
            self._log(f"❌ 部署出错: {str(e)}")
            self.finished_signal.emit(False, f"部署出错: {str(e)}")

    def _log(self, msg: str):
        print(msg)
        self.log_signal.emit(msg)


class GitWorker(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)

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
            self._log("──── 第 1 步：git add . ────")
            proc = subprocess.Popen("git add .", cwd=str(BASE_DIR), stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT, shell=True, encoding="utf-8",
                                     errors="replace", bufsize=1)
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

            self._log("──── 第 2 步：git commit ────")
            self._log(f'> git commit -m "{self.commit_msg}"')
            proc = subprocess.Popen(f'git commit -m "{self.commit_msg}"', cwd=str(BASE_DIR),
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True,
                                     encoding="utf-8", errors="replace", bufsize=1)
            for line in proc.stdout:
                line = line.rstrip("\n\r")
                if line.strip():
                    self._log(f"  {line}")
            proc.wait(timeout=60)
            if proc.returncode != 0:
                self._log("ℹ️ 没有需要提交的更改（可能已是最新）")
            else:
                self._log("✅ 提交完成")
            self._log("")

            self._log("──── 第 3 步：git push ────")
            self._log("> git push")
            proc = subprocess.Popen("git push", cwd=str(BASE_DIR), stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT, shell=True, encoding="utf-8",
                                     errors="replace", bufsize=1)
            for line in proc.stdout:
                line = line.rstrip("\n\r")
                if line.strip():
                    self._log(f"  {line}")
            proc.wait(timeout=120)
            self._log("")
            self._log("──────────────────────────────")
            if proc.returncode == 0:
                self._log("✅ Git 提交与推送成功！")
                self.finished_signal.emit(True, "Git 提交与推送成功！")
            else:
                self._log(f"❌ git push 失败 (退出码: {proc.returncode})")
                self.finished_signal.emit(False, "git push 失败")
        except subprocess.TimeoutExpired:
            self._log("❌ 操作超时")
            self.finished_signal.emit(False, "Git 操作超时")
        except FileNotFoundError:
            self._log("❌ 未找到 git 命令")
            self.finished_signal.emit(False, "未找到 git 命令")
        except Exception as e:
            self._log(f"❌ 操作出错: {str(e)}")
            self.finished_signal.emit(False, f"Git 操作出错: {str(e)}")

    def _log(self, msg: str):
        print(msg)
        self.log_signal.emit(msg)


class LogWindow(QMainWindow):
    """独立的操作日志窗口"""

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

        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setFont(QFont("Consolas", 10))
        self.log_edit.setStyleSheet("""
            QTextEdit {
                background: #1a1a2e; color: #a0d2db;
                border: 1px solid #2d2d44; border-radius: 8px; padding: 10px;
            }
            QScrollBar:vertical { background: #1a1a2e; width: 10px; border-radius: 5px; }
            QScrollBar::handle:vertical { background: #3d3d5c; border-radius: 5px; min-height: 30px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)
        layout.addWidget(self.log_edit)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.lbl_status = QLabel("等待开始...")
        self.lbl_status.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        btn_layout.addWidget(self.lbl_status)

        self.btn_close = QPushButton("关闭")
        self.btn_close.setEnabled(False)
        self.btn_close.setStyleSheet("""
            QPushButton { background: #3d3d5c; color: #a0d2db; border: none; border-radius: 6px; padding: 8px 24px; font-size: 13px; }
            QPushButton:hover { background: #4d4d7c; }
            QPushButton:disabled { background: #2a2a3a; color: #5a5a7a; }
        """)
        self.btn_close.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)

        try:
            screen = QApplication.desktop().screenGeometry()
            self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)
        except Exception:
            pass

    def append_log(self, msg: str):
        color = "#a0d2db"
        if msg.startswith("✅"): color = "#00e676"
        elif msg.startswith("❌"): color = "#ff5252"
        elif msg.startswith("⚠"): color = "#ffd740"
        elif msg.startswith("═") or msg.startswith("─"): color = "#5a5a7a"
        elif msg.startswith(">"): color = "#ffab40"
        self.log_edit.append(f'<span style="color:{color};">{self._escape(msg)}</span>')
        bar = self.log_edit.verticalScrollBar()
        bar.setValue(bar.maximum())

    def set_finished(self, success: bool):
        self.btn_close.setEnabled(True)
        self.btn_close.setStyleSheet("""
            QPushButton { background: #2980b9; color: white; border: none; border-radius: 6px; padding: 8px 24px; font-size: 13px; font-weight: bold; }
            QPushButton:hover { background: #1a5276; }
        """)
        status = "✅ 完成" if success else "❌ 失败"
        color = "#00e676" if success else "#ff5252"
        self.lbl_status.setText(status)
        self.lbl_status.setStyleSheet(f"color: {color}; font-size: 13px; font-weight: bold;")

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


# ==================== 主窗口 ====================

class AdminWindow(QMainWindow):
    def __init__(self, init_files: list = None):
        super().__init__()
        self.setWindowTitle("四川省双流中学 初2024级7班 · 后台管理工具")
        self.resize(950, 680)
        self.setMinimumSize(750, 500)
        try:
            screen = QApplication.desktop().screenGeometry()
            self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)
        except Exception:
            pass

        self._manifest = []
        self._notices_data = {"notices": []}
        self._editing_notice_id = None

        self._build_ui()
        self._load_all()

        if init_files:
            QTimer.singleShot(300, lambda files=init_files: self._add_files(files))

    # ==================== UI 构建 ====================

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(6)

        # 标题
        title = QLabel("⚙️ 班委会后台管理工具")
        title.setFont(QFont("Microsoft YaHei", 15, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1a5276; padding: 6px;")
        root.addWidget(title)

        # 标签页
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #e1e8f0; border-radius: 8px; background: #fff; }
            QTabBar::tab {
                background: #eaf0f6; padding: 10px 24px; margin-right: 2px;
                border-top-left-radius: 8px; border-top-right-radius: 8px;
                font-size: 13px; font-weight: 500;
            }
            QTabBar::tab:selected { background: #fff; font-weight: 700; color: #1a5276; }
            QTabBar::tab:hover { background: #d4e6f1; }
        """)
        root.addWidget(self.tabs)

        self._build_notice_tab()
        self._build_file_tab()

        # 状态栏
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("就绪")
        self.setStatusBar(self.status_bar)

        self.progress = QProgressBar()
        self.progress.setMaximumWidth(200)
        self.progress.setMaximumHeight(18)
        self.progress.hide()
        self.status_bar.addPermanentWidget(self.progress)

    # ── 通知管理标签页 ──

    def _build_notice_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # 按钮栏
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.notice_btn_new = QPushButton("＋ 新建通知")
        self.notice_btn_new.setStyleSheet(self._btn_style("#2980b9", "#1a5276"))
        self.notice_btn_new.clicked.connect(self._notice_new)
        btn_row.addWidget(self.notice_btn_new)

        self.notice_btn_edit = QPushButton("✎ 编辑选中")
        self.notice_btn_edit.setStyleSheet(self._btn_style("#8e44ad", "#6c3483"))
        self.notice_btn_edit.clicked.connect(self._notice_edit)
        btn_row.addWidget(self.notice_btn_edit)

        self.notice_btn_delete = QPushButton("🗑 删除选中")
        self.notice_btn_delete.setStyleSheet(self._btn_style("#e74c3c", "#c0392b"))
        self.notice_btn_delete.clicked.connect(self._notice_delete)
        btn_row.addWidget(self.notice_btn_delete)

        btn_row.addStretch()

        self.notice_btn_save = QPushButton("💾 保存到文件")
        self.notice_btn_save.setStyleSheet(self._btn_style("#27ae60", "#1e8449"))
        self.notice_btn_save.clicked.connect(self._notice_save_to_file)
        btn_row.addWidget(self.notice_btn_save)

        layout.addLayout(btn_row)

        # 分割区域
        splitter = QSplitter(Qt.Vertical)

        # 通知列表表格
        self.notice_table = QTableWidget()
        self.notice_table.setColumnCount(5)
        self.notice_table.setHorizontalHeaderLabels(["置顶", "标题", "作者", "日期", "ID"])
        self.notice_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.notice_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.notice_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.notice_table.setAlternatingRowColors(True)
        self.notice_table.horizontalHeader().setStretchLastSection(True)
        self.notice_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.notice_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.notice_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.notice_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.notice_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.notice_table.setColumnWidth(0, 50)
        self.notice_table.setColumnWidth(2, 100)
        self.notice_table.setColumnWidth(3, 110)
        self.notice_table.setColumnWidth(4, 50)
        self.notice_table.verticalHeader().setDefaultSectionSize(36)
        self.notice_table.setStyleSheet("""
            QTableWidget { border: 1px solid #e1e8f0; border-radius: 6px; gridline-color: #f0f0f0; font-size: 13px; }
            QTableWidget::item { padding: 2px 6px; }
            QHeaderView::section { background: #f5f7fa; border: none; border-bottom: 2px solid #e1e8f0; padding: 6px; font-weight: bold; color: #2c3e50; }
            QTableWidget::item:selected { background: #d4e6f1; color: #1a5276; }
        """)
        self.notice_table.doubleClicked.connect(self._notice_edit)
        splitter.addWidget(self.notice_table)

        # 编辑面板
        edit_widget = QWidget()
        edit_layout = QVBoxLayout(edit_widget)
        edit_layout.setContentsMargins(0, 8, 0, 0)
        edit_layout.setSpacing(6)

        # 标题
        form1 = QHBoxLayout()
        form1.addWidget(QLabel("标题："))
        self.notice_title_input = QLineEdit()
        self.notice_title_input.setPlaceholderText("输入通知标题...")
        self.notice_title_input.setStyleSheet("padding: 6px 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 13px;")
        form1.addWidget(self.notice_title_input)
        edit_layout.addLayout(form1)

        # 作者 / 日期 / 置顶
        form2 = QHBoxLayout()
        form2.addWidget(QLabel("作者："))
        self.notice_author_input = QLineEdit("班委会")
        self.notice_author_input.setMaximumWidth(140)
        self.notice_author_input.setStyleSheet("padding: 4px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 13px;")
        form2.addWidget(self.notice_author_input)
        form2.addSpacing(16)
        form2.addWidget(QLabel("日期："))
        self.notice_date_input = QLineEdit(date.today().isoformat())
        self.notice_date_input.setMaximumWidth(120)
        self.notice_date_input.setStyleSheet("padding: 4px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 13px;")
        form2.addWidget(self.notice_date_input)
        form2.addStretch()
        self.notice_pinned_cb = QCheckBox("📌 置顶")
        form2.addWidget(self.notice_pinned_cb)
        edit_layout.addLayout(form2)

        # 内容编辑
        self.notice_content_edit = QTextEdit()
        self.notice_content_edit.setPlaceholderText("通知内容（支持 Markdown 格式）...")
        self.notice_content_edit.setFont(QFont("Microsoft YaHei", 11))
        self.notice_content_edit.setStyleSheet("""
            QTextEdit { border: 1px solid #ddd; border-radius: 4px; padding: 8px; background: #fafbfc; }
        """)
        self.notice_content_edit.setMinimumHeight(120)
        edit_layout.addWidget(self.notice_content_edit)

        # 按钮
        form3 = QHBoxLayout()
        form3.addStretch()
        self.notice_btn_apply = QPushButton("✅ 应用更改")
        self.notice_btn_apply.setStyleSheet(self._btn_style("#2980b9", "#1a5276"))
        self.notice_btn_apply.clicked.connect(self._notice_apply)
        form3.addWidget(self.notice_btn_apply)
        self.notice_btn_cancel = QPushButton("取消编辑")
        self.notice_btn_cancel.setStyleSheet(self._btn_style("#95a5a6", "#7f8c8d"))
        self.notice_btn_cancel.clicked.connect(self._notice_cancel)
        form3.addWidget(self.notice_btn_cancel)
        edit_layout.addLayout(form3)

        splitter.addWidget(edit_widget)
        splitter.setSizes([300, 220])
        layout.addWidget(splitter)

        self.tabs.addTab(tab, "📢 通知管理")

    # ── 文件管理标签页 ──

    def _build_file_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # 提示标签
        hint = QLabel("拖拽 Word / PDF / TXT / Markdown 文件到此标签页  或  点击下方按钮选择文件")
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet("color: #7f8c8d; font-size: 13px; margin-bottom: 2px;")
        layout.addWidget(hint)

        # 拖放区域 + 表格
        splitter = QSplitter(Qt.Vertical)

        self.file_drop_frame = DropFrame()
        self.file_drop_frame.setMinimumHeight(60)
        self.file_drop_frame.files_dropped.connect(self._add_files)
        drop_layout = QVBoxLayout(self.file_drop_frame)
        drop_layout.setContentsMargins(2, 2, 2, 2)

        self.file_table = QTableWidget()
        self.file_table.setColumnCount(4)
        self.file_table.setHorizontalHeaderLabels(["图标", "文件名", "类型", "操作"])
        self.file_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.file_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.file_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.file_table.setAlternatingRowColors(True)
        self.file_table.horizontalHeader().setStretchLastSection(True)
        self.file_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.file_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.file_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.file_table.setColumnWidth(0, 50)
        self.file_table.setColumnWidth(2, 70)
        self.file_table.verticalHeader().setDefaultSectionSize(40)
        self.file_table.setStyleSheet("""
            QTableWidget { border: 1px solid #e1e8f0; border-radius: 6px; gridline-color: #f0f0f0; font-size: 13px; }
            QTableWidget::item { padding: 4px 8px; }
            QHeaderView::section { background: #f5f7fa; border: none; border-bottom: 2px solid #e1e8f0; padding: 8px; font-weight: bold; color: #2c3e50; }
            QTableWidget::item:selected { background: #d4e6f1; color: #1a5276; }
        """)
        drop_layout.addWidget(self.file_table)
        splitter.addWidget(self.file_drop_frame)

        layout.addWidget(splitter)

        # 按钮栏
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.file_btn_add = QPushButton("＋ 添加文件")
        self.file_btn_add.setStyleSheet(self._btn_style("#2980b9", "#1a5276"))
        self.file_btn_add.clicked.connect(self._on_add_files)
        self.file_btn_add.setMinimumHeight(36)
        btn_row.addWidget(self.file_btn_add)

        self.file_btn_delete = QPushButton("🗑 删除选中")
        self.file_btn_delete.setStyleSheet(self._btn_style("#e74c3c", "#c0392b"))
        self.file_btn_delete.clicked.connect(self._on_delete_files)
        self.file_btn_delete.setMinimumHeight(36)
        btn_row.addWidget(self.file_btn_delete)

        self.file_btn_refresh = QPushButton("🔄 刷新清单")
        self.file_btn_refresh.setStyleSheet(self._btn_style("#27ae60", "#1e8449"))
        self.file_btn_refresh.clicked.connect(self._load_file_data)
        self.file_btn_refresh.setMinimumHeight(36)
        btn_row.addWidget(self.file_btn_refresh)

        btn_row.addStretch()

        self.lbl_file_count = QLabel("共 0 个文件")
        self.lbl_file_count.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        btn_row.addWidget(self.lbl_file_count)

        self.file_btn_git = QPushButton("📤 提交并推送")
        self.file_btn_git.setStyleSheet(self._btn_style("#8e44ad", "#6c3483"))
        self.file_btn_git.clicked.connect(self._on_git_push)
        self.file_btn_git.setMinimumHeight(36)
        btn_row.addWidget(self.file_btn_git)

        self.file_btn_deploy = QPushButton("🚀 部署到 Cloudflare")
        self.file_btn_deploy.setStyleSheet(self._btn_style("#1a5276", "#0d344a"))
        self.file_btn_deploy.clicked.connect(self._on_deploy)
        self.file_btn_deploy.setMinimumHeight(36)
        btn_row.addWidget(self.file_btn_deploy)

        layout.addLayout(btn_row)

        self.tabs.addTab(tab, "📂 文件管理")

    # ==================== 样式辅助 ====================

    @staticmethod
    def _btn_style(bg, hover_bg):
        return f"""
            QPushButton {{
                background: {bg}; color: white; border: none; border-radius: 6px;
                padding: 6px 16px; font-size: 13px; font-weight: bold;
                font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
            }}
            QPushButton:hover {{ background: {hover_bg}; }}
            QPushButton:pressed {{ background: {hover_bg}; padding: 7px 16px 5px 16px; }}
            QPushButton:disabled {{ background: #bdc3c7; color: #ecf0f1; }}
        """

    # ==================== 数据加载 ====================

    def _load_all(self):
        self._load_notice_data()
        self._load_file_data()

    def _load_notice_data(self):
        self._notices_data = load_notices()
        self._refresh_notice_table()

    def _load_file_data(self):
        self._manifest = generate_manifest()
        self._refresh_file_table()
        n = len(self._manifest)
        self.lbl_file_count.setText(f"共 {n} 个文件")
        self.status_bar.showMessage(f"文件清单已刷新，共 {n} 个文件")

    # ==================== 通知管理 — 表格渲染 ====================

    def _refresh_notice_table(self):
        notices = self._notices_data.get("notices", [])
        self.notice_table.setRowCount(len(notices))
        for row, n in enumerate(notices):
            pinned_item = QTableWidgetItem("📌" if n.get("pinned") else "")
            pinned_item.setTextAlignment(Qt.AlignCenter)
            pinned_item.setFont(QFont("Segoe UI Emoji", 12))
            self.notice_table.setItem(row, 0, pinned_item)

            title_item = QTableWidgetItem(n.get("title", ""))
            title_item.setToolTip(n.get("title", ""))
            self.notice_table.setItem(row, 1, title_item)

            author_item = QTableWidgetItem(n.get("author", ""))
            author_item.setTextAlignment(Qt.AlignCenter)
            self.notice_table.setItem(row, 2, author_item)

            date_item = QTableWidgetItem(n.get("date", ""))
            date_item.setTextAlignment(Qt.AlignCenter)
            self.notice_table.setItem(row, 3, date_item)

            id_item = QTableWidgetItem(str(n.get("id", "")))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.notice_table.setItem(row, 4, id_item)

    # ==================== 通知管理 — 操作 ====================

    def _get_selected_notice_row(self) -> int:
        rows = set(idx.row() for idx in self.notice_table.selectedIndexes())
        return list(rows)[0] if rows else -1

    def _notice_new(self):
        self._editing_notice_id = None
        self.notice_title_input.clear()
        self.notice_author_input.setText("班委会")
        self.notice_date_input.setText(date.today().isoformat())
        self.notice_pinned_cb.setChecked(False)
        self.notice_content_edit.clear()
        self.status_bar.showMessage("新建通知 — 填写信息后点击「应用更改」")

    def _notice_edit(self):
        row = self._get_selected_notice_row()
        if row < 0:
            QMessageBox.information(self, "提示", "请先选择一条通知。")
            return
        notices = self._notices_data.get("notices", [])
        n = notices[row]
        self._editing_notice_id = n.get("id")
        self.notice_title_input.setText(n.get("title", ""))
        self.notice_author_input.setText(n.get("author", "班委会"))
        self.notice_date_input.setText(n.get("date", ""))
        self.notice_pinned_cb.setChecked(n.get("pinned", False))
        self.notice_content_edit.setPlainText(n.get("content", ""))
        self.status_bar.showMessage(f"正在编辑：{n.get('title', '')}")

    def _notice_apply(self):
        title = self.notice_title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "提示", "请输入通知标题。")
            return

        notices = self._notices_data.get("notices", [])

        notice_obj = {
            "title": title,
            "content": self.notice_content_edit.toPlainText().strip(),
            "author": self.notice_author_input.text().strip() or "班委会",
            "date": self.notice_date_input.text().strip() or date.today().isoformat(),
            "pinned": self.notice_pinned_cb.isChecked(),
        }

        if self._editing_notice_id:
            # 编辑已有通知
            for n in notices:
                if n.get("id") == self._editing_notice_id:
                    notice_obj["id"] = self._editing_notice_id
                    n.update(notice_obj)
                    break
            self.status_bar.showMessage(f"通知「{title}」已更新")
        else:
            # 新建通知
            max_id = max((int(n.get("id", 0)) for n in notices), default=0)
            notice_obj["id"] = str(max_id + 1)
            notices.append(notice_obj)
            self.status_bar.showMessage(f"通知「{title}」已添加")

        self._notices_data["notices"] = notices
        self._refresh_notice_table()
        self._editing_notice_id = None

    def _notice_cancel(self):
        self._editing_notice_id = None
        self.notice_title_input.clear()
        self.notice_content_edit.clear()
        self.status_bar.showMessage("已取消编辑")

    def _notice_delete(self):
        row = self._get_selected_notice_row()
        if row < 0:
            QMessageBox.information(self, "提示", "请先选择一条通知。")
            return
        notices = self._notices_data.get("notices", [])
        n = notices[row]
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除通知「{n.get('title', '')}」吗？\n此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            del notices[row]
            self._notices_data["notices"] = notices
            self._refresh_notice_table()
            self.status_bar.showMessage(f"通知已删除")

    def _notice_save_to_file(self):
        save_notices(self._notices_data)
        count = len(self._notices_data.get("notices", []))
        self.status_bar.showMessage(f"通知数据已保存到 notices.json（共 {count} 条）")
        QMessageBox.information(self, "保存成功", f"通知已写入 public/notices.json\n共 {count} 条通知。\n\n如需更新网站，请使用 Git 提交推送或直接部署。")

    # ==================== 文件管理 — 表格渲染 ====================

    def _refresh_file_table(self):
        files = self._manifest
        self.file_table.setRowCount(len(files))
        for row, f in enumerate(files):
            icon_item = QTableWidgetItem(get_file_icon(f["type"]))
            icon_item.setTextAlignment(Qt.AlignCenter)
            icon_item.setFont(QFont("Segoe UI Emoji", 14))
            self.file_table.setItem(row, 0, icon_item)

            name_item = QTableWidgetItem(f["displayName"])
            name_item.setToolTip(f"{f['displayName']}.{f['type']}")
            self.file_table.setItem(row, 1, name_item)

            type_item = QTableWidgetItem(f" .{f['type']} ")
            type_item.setTextAlignment(Qt.AlignCenter)
            self.file_table.setItem(row, 2, type_item)

            op_widget = QWidget()
            op_layout = QHBoxLayout(op_widget)
            op_layout.setContentsMargins(4, 2, 4, 2)
            op_layout.setSpacing(6)
            btn_del = QPushButton("删除")
            btn_del.setFixedSize(50, 26)
            btn_del.setStyleSheet("""
                QPushButton { background: #fdecea; color: #e74c3c; border: 1px solid #f5c6cb; border-radius: 4px; font-size: 12px; }
                QPushButton:hover { background: #e74c3c; color: white; }
            """)
            btn_del.clicked.connect(lambda checked, fn=f["name"]: self._delete_single_file(fn))
            op_layout.addWidget(btn_del)
            op_layout.addStretch()
            self.file_table.setCellWidget(row, 3, op_widget)

    # ==================== 文件管理 — 操作 ====================

    def _add_files(self, path_strings: list):
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
                    skipped.append(f"{src.name} (不支持的格式)")
            else:
                skipped.append(f"{src.name} (不是文件)")

        self._load_file_data()
        msg = f"成功添加 {added} 个文件。"
        if skipped:
            msg += f" 跳过: {'; '.join(skipped[:5])}"
        self.status_bar.showMessage(msg)

    def _on_add_files(self):
        filter_str = ";;".join([EXT_LABELS[ext] for ext in SUPPORTED_EXTS])
        filter_str = f"支持的文件 ({' '.join(SUPPORTED_EXTS)});;{filter_str};;所有文件 (*.*)"
        paths, _ = QFileDialog.getOpenFileNames(self, "选择要添加的文件", "", filter_str)
        if paths:
            self._add_files(paths)

    def _delete_single_file(self, filename: str):
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除「{filename}」吗？\n此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            delete_file_from_public(filename)
            self._load_file_data()
            self.status_bar.showMessage(f"已删除: {filename}")

    def _on_delete_files(self):
        rows = set(idx.row() for idx in self.file_table.selectedIndexes())
        if not rows:
            QMessageBox.information(self, "提示", "请先选择要删除的文件。")
            return
        filenames = [self._manifest[r]["name"] for r in sorted(rows, reverse=True)]
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除 {len(filenames)} 个文件吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            for fn in filenames:
                delete_file_from_public(fn)
            self._load_file_data()
            self.status_bar.showMessage(f"已删除 {len(filenames)} 个文件")

    # ==================== Git 提交与推送 ====================

    def _on_git_push(self):
        """打开独立的提交确认窗口，支持智能提交信息"""
        # 保存通知和刷新清单
        self._notice_save_to_file()
        self._load_file_data()

        # git add 暂存所有更改
        self.status_bar.showMessage("正在分析文件变更...")
        try:
            subprocess.run("git add .", cwd=str(BASE_DIR), shell=True,
                           capture_output=True, timeout=30)
        except Exception:
            pass

        # 获取 diff 并生成智能提交信息
        diff_data = get_staged_diff()
        suggested_msg = generate_commit_message(diff_data)

        # 打开提交对话框
        dialog = CommitDialog(
            suggested_msg=suggested_msg,
            diff_stat=diff_data.get("stat", ""),
            file_list=diff_data.get("files", []),
            parent=self
        )

        if dialog.exec_() != QDialog.Accepted:
            self.status_bar.showMessage("已取消提交")
            return

        commit_msg = dialog.msg_edit.toPlainText().strip()

        # 打开日志窗口并开始提交
        self.log_window = LogWindow(self, title="Git 提交日志")
        self.log_window.show()

        self.file_btn_git.setEnabled(False)
        self.file_btn_git.setText("⏳ 推送中...")
        self.progress.setRange(0, 0)
        self.progress.show()
        self.status_bar.showMessage("正在提交到 Git...")

        self.git_worker = GitWorker(commit_msg)
        self.git_worker.log_signal.connect(self.log_window.append_log)
        self.git_worker.finished_signal.connect(self._on_git_finished)
        self.git_worker.start()

    def _on_git_finished(self, success: bool, message: str):
        self.file_btn_git.setEnabled(True)
        self.file_btn_git.setText("📤 提交并推送")
        self.progress.hide()
        self.status_bar.showMessage(message)
        if hasattr(self, 'log_window') and self.log_window:
            self.log_window.set_finished(success)

    # ==================== 部署到 Cloudflare ====================

    def _on_deploy(self):
        reply = QMessageBox.question(
            self, "确认部署",
            "即将部署到 Cloudflare Workers。\n请确保已登录 Wrangler 且网络畅通。\n\n继续？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
        )
        if reply != QMessageBox.Yes:
            return

        # 保存通知和清单
        self._notice_save_to_file()
        self._load_file_data()

        self.deploy_log_window = LogWindow(self, title="部署日志 — Cloudflare Workers")
        self.deploy_log_window.show()

        self.file_btn_deploy.setEnabled(False)
        self.file_btn_deploy.setText("⏳ 部署中...")
        self.progress.setRange(0, 0)
        self.progress.show()
        self.status_bar.showMessage("正在部署，详见日志窗口...")

        self.deploy_worker = DeployWorker()
        self.deploy_worker.log_signal.connect(self.deploy_log_window.append_log)
        self.deploy_worker.finished_signal.connect(self._on_deploy_finished)
        self.deploy_worker.start()

    def _on_deploy_finished(self, success: bool, message: str):
        self.file_btn_deploy.setEnabled(True)
        self.file_btn_deploy.setText("🚀 部署到 Cloudflare")
        self.progress.hide()
        self.status_bar.showMessage(message)
        if hasattr(self, 'deploy_log_window') and self.deploy_log_window:
            self.deploy_log_window.set_finished(success)


# ==================== 入口 ====================

def main():
    ensure_dirs()

    app = QApplication(sys.argv)
    app.setApplicationName("SLZX-Admin")
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#f8f9fb"))
    palette.setColor(QPalette.WindowText, QColor("#2c3e50"))
    palette.setColor(QPalette.Highlight, QColor("#2980b9"))
    app.setPalette(palette)

    # 收集命令行传入的文件
    init_files = []
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            init_files.append(arg)

    window = AdminWindow(init_files if init_files else None)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n程序崩溃: {e}")
        try:
            from PyQt5.QtWidgets import QApplication, QMessageBox
            app = QApplication(sys.argv[:1])
            QMessageBox.critical(None, "程序错误", f"发生未处理的异常:\n\n{str(e)}\n\n详情请查看控制台输出。")
        except Exception:
            pass
        input("\n按回车键退出...")

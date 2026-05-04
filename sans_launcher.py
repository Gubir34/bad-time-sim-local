"""
Sans Fight Launcher
-------------------
Mevcut HTML/JS oyununu (c2-sans-fight) PyQt6 WebEngine ile
native pencerede çalıştırır.

Kurulum:
    pip install PyQt6 PyQt6-WebEngine

Kullanım:
    python sans_launcher.py                        # online mod (GitHub Pages)
    python sans_launcher.py --local ./c2-sans-fight # local klasör modu
    python sans_launcher.py --fullscreen            # tam ekran
"""

import sys
import os
import argparse
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMainWindow, QSplashScreen, QLabel
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEnginePage, QWebEngineProfile
from PyQt6.QtCore import QUrl, Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QIcon, QColor, QPainter, QFont

# ── Sabitler ────────────────────────────────────────────────────────────────
ONLINE_URL   = "https://sans-simulator.github.io/c2-sans-fight/"
WINDOW_TITLE = "Bad Time Simulator"
DEFAULT_W    = 960
DEFAULT_H    = 640
BG_COLOR     = "#000000"


# ── Custom Page: console logları terminale yönlendir ────────────────────────
class GamePage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, line, source):
        level_str = ["INFO", "WARN", "ERR "][min(level.value, 2)]
        print(f"[JS {level_str}] {source}:{line} — {message}")


# ── Ana pencere ─────────────────────────────────────────────────────────────
class SansWindow(QMainWindow):
    def __init__(self, url: str, fullscreen: bool = False):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.setStyleSheet(f"background-color: {BG_COLOR};")

        # WebEngine profil & sayfa
        profile = QWebEngineProfile("sans_fight", self)
        profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)

        self.page = GamePage(profile, self)
        self._configure_settings(self.page.settings())

        # WebView
        self.view = QWebEngineView(self)
        self.view.setPage(self.page)
        self.view.setStyleSheet(f"background-color: {BG_COLOR};")
        self.setCentralWidget(self.view)

        # Pencere boyutu
        if fullscreen:
            self.showFullScreen()
        else:
            self.resize(DEFAULT_W, DEFAULT_H)
            self._center_window()
            self.show()

        # URL yükle
        self.view.setUrl(QUrl(url))
        self.view.loadFinished.connect(self._on_load)

    def _configure_settings(self, s: QWebEngineSettings):
        """Oyun için gerekli tüm WebEngine ayarları."""
        s.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled,           True)
        s.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls,   True)
        s.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled,                True)
        s.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled,  True)
        s.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
        s.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled,         True)

    def _center_window(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width()  - self.width())  // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def _on_load(self, ok: bool):
        if ok:
            print("[Launcher] Sayfa yüklendi ✓")
            # Construct 2 bazen canvas boyutunu yanlış alır, zorla tetikle
            self.view.page().runJavaScript(
                "window.dispatchEvent(new Event('resize'));"
            )
        else:
            print("[Launcher] Sayfa yüklenemedi ✗")

    def keyPressEvent(self, event):
        """F11 = fullscreen toggle, ESC = normal pencere."""
        if event.key() == Qt.Key.Key_F11:
            if self.isFullScreen():
                self.showNormal()
                self.resize(DEFAULT_W, DEFAULT_H)
                self._center_window()
            else:
                self.showFullScreen()
        elif event.key() == Qt.Key.Key_Escape and self.isFullScreen():
            self.showNormal()
            self.resize(DEFAULT_W, DEFAULT_H)
            self._center_window()
        else:
            super().keyPressEvent(event)


# ── Splash screen ─────────────────────────────────────────────────────────
def make_splash() -> QSplashScreen:
    px = QPixmap(400, 200)
    px.fill(QColor("#000000"))
    p = QPainter(px)
    p.setPen(QColor("#ffffff"))
    font = QFont("Courier New", 18, QFont.Weight.Bold)
    p.setFont(font)
    p.drawText(px.rect(), Qt.AlignmentFlag.AlignCenter, "* Bad Time Simulator *\n\nLoading...")
    p.end()
    splash = QSplashScreen(px, Qt.WindowType.WindowStaysOnTopHint)
    return splash


# ── Entry point ──────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Sans Fight Launcher")
    parser.add_argument("--local",      metavar="DIR",  help="Local repo klasörü (index.html burada olmalı)")
    parser.add_argument("--fullscreen", action="store_true", help="Tam ekran başlat")
    parser.add_argument("--no-splash",  action="store_true", help="Splash ekranını atla")
    args = parser.parse_args()

    # URL belirle
    if args.local:
        local_path = Path(args.local).resolve()
        index = local_path / "index.html"
        if not index.exists():
            print(f"[Hata] {index} bulunamadı!")
            sys.exit(1)
        url = QUrl.fromLocalFile(str(index)).toString()
        print(f"[Launcher] Local mod: {url}")
    else:
        url = ONLINE_URL
        print(f"[Launcher] Online mod: {url}")

    # GPU process crash'lerini önle (bazı sistemlerde gerekli)
    os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--disable-gpu-sandbox")

    app = QApplication(sys.argv)
    app.setApplicationName(WINDOW_TITLE)

    # Splash
    splash = None
    if not args.no_splash:
        splash = make_splash()
        splash.show()
        app.processEvents()

    # Ana pencere
    win = SansWindow(url, fullscreen=args.fullscreen)

    if splash:
        QTimer.singleShot(1500, splash.close)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
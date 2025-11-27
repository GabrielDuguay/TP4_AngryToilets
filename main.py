from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QMenu, QPushButton, QToolBar, QWidget

from controller.game_controller import GameController
from model.game_model import GameModel
from view.game_view import GameView
from view.options_dialog import OptionsDialog
from view.trajectory_window import TrajectoryWindow


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Angry Toilets - PyQt + PyMunk")

        self.model = GameModel()
        self.controller = GameController(self.model)
        self.game_view = GameView(self.model, self.controller)
        self.trajectory_window = TrajectoryWindow(self)
        self.options_dialog = OptionsDialog(self.trajectory_window, self)

        self.setCentralWidget(self.game_view)
        self._build_toolbar()
        self._build_menu()

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Actions")
        reload_button = QPushButton("Relancer")
        reload_button.clicked.connect(self.controller.reset_projectile)
        toolbar.addWidget(reload_button)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

    def _build_menu(self) -> None:
        options_menu = self.menuBar().addMenu("Options")
        action_open_graph = options_menu.addAction("Graphique")
        action_open_graph.triggered.connect(self._open_options_dialog)

    def _open_options_dialog(self) -> None:
        self.trajectory_window.set_points(self.model.trajectory)
        self.options_dialog.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

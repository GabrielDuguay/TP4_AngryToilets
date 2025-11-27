from __future__ import annotations

from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from view.trajectory_window import TrajectoryWindow


class OptionsDialog(QDialog):
    def __init__(self, trajectory_window: TrajectoryWindow, parent=None) -> None:
        super().__init__(parent)
        self.trajectory_window = trajectory_window
        self.setWindowTitle("Options")
        self.setModal(False)
        self._build_ui()

    def _build_ui(self) -> None:
        description = QLabel(
            "Cliquez sur le bouton ci-dessous pour afficher le graphique\n"
            "de la dernière trajectoire calculée."
        )
        graph_button = QPushButton("Graphique")
        graph_button.clicked.connect(self._show_graph)

        layout = QVBoxLayout()
        layout.addWidget(description)
        layout.addWidget(graph_button)
        layout.addStretch(1)
        self.setLayout(layout)

    def _show_graph(self) -> None:
        self.trajectory_window.show()
        self.trajectory_window.raise_()
        self.trajectory_window.activateWindow()

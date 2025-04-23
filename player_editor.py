from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDoubleSpinBox, QDialogButtonBox, QLabel, QWidget, QGraphicsTextItem
from PyQt6.QtCore import Qt

class PlayerEditorDialog(QDialog):
    def __init__(self, player, parent=None):
        super().__init__(parent)
        self.player = player
        self.setWindowTitle("Spieler bearbeiten")
        
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Editable player's custom name (unter dem Spieler)
        self.name_edit = QLineEdit(self)
        # Initialisiere mit dem bestehenden name_label
        self.name_edit.setText(player.name_label if hasattr(player, "name_label") else "")
        form_layout.addRow("Spielername:", self.name_edit)
        
        main_layout.addLayout(form_layout)
        
        # Dialog buttons
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        main_layout.addWidget(self.buttonBox)
        
    def accept(self):
        # Update custom name_label unter dem Spieler
        new_name = self.name_edit.text()
        self.player.name_label = new_name
        self.player.name_text.setPlainText(new_name)
        # Repositioniere das Namens-Label zentriert unter dem Spieler
        if hasattr(self.player, 'updateNameTextPosition'):
            self.player.updateNameTextPosition()
        super().accept()

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDoubleSpinBox, QDialogButtonBox, QLabel, QWidget, QGraphicsTextItem
from PyQt6.QtCore import Qt

class PlayerEditorDialog(QDialog): #Dialog für die Spielerbearbeitung 
    def __init__(self, player, parent=None):
        super().__init__(parent)
        self.player = player
        self.setWindowTitle("Spieler bearbeiten")
        
        main_layout = QVBoxLayout(self) #Layout für den Dialog
        form_layout = QFormLayout()
        
        #bearbeitbare Spielernamen (unter dem Spieler) 
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
        
    def accept(self): #akzeptiert die Änderungen und speichert sie  
        new_name = self.name_edit.text()
        self.player.name_label = new_name 
        self.player.name_text.setPlainText(new_name)
        #ändert den Namen des Spielers und aktualisiert die Position des Namenslabels 
        if hasattr(self.player, 'updateNameTextPosition'):
            self.player.updateNameTextPosition()
        super().accept()

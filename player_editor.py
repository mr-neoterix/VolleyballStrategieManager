from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDoubleSpinBox, QDialogButtonBox, QLabel, QWidget, QGraphicsTextItem  # Importiert notwendige Widgets von PyQt6 für Dialoge und Layouts.
from PyQt6.QtCore import Qt  # Importiert Qt-Kernfunktionalitäten.

class PlayerEditorDialog(QDialog): # Dialog für die Spielerbearbeitung.
    def __init__(self, player, parent=None):  # Konstruktor des Dialogs, nimmt ein Spielerobjekt und ein optionales Eltern-Widget entgegen.
        super().__init__(parent)  # Ruft den Konstruktor der Basisklasse QDialog auf.
        self.player = player  # Speichert das übergebene Spielerobjekt.
        self.setWindowTitle("Spieler bearbeiten")  # Setzt den Fenstertitel des Dialogs.
        
        main_layout = QVBoxLayout(self) # Layout für den Dialog. Erstellt ein vertikales Hauptlayout.
        form_layout = QFormLayout()  # Erstellt ein Formularlayout für Eingabefelder.
        
        # Bearbeitbare Spielernamen (unter dem Spieler).
        self.name_edit = QLineEdit(self)  # Erstellt ein einzeiliges Textfeld zur Bearbeitung des Spielernamens.
        # Initialisiere mit dem bestehenden name_label.
        self.name_edit.setText(player.name_label if hasattr(player, "name_label") else "")  # Setzt den Text des Eingabefelds auf den aktuellen Namen des Spielers, falls vorhanden.
        form_layout.addRow("Spielername:", self.name_edit)  # Fügt dem Formularlayout eine Zeile für den Spielernamen hinzu.
        
        main_layout.addLayout(form_layout)  # Fügt das Formularlayout zum Hauptlayout hinzu.
        
        # Dialog-Buttons.
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)  # Erstellt eine Button-Box mit OK- und Abbrechen-Buttons.
        self.buttonBox.accepted.connect(self.accept)  # Verbindet das accepted-Signal (OK-Klick) mit der accept-Methode des Dialogs.
        self.buttonBox.rejected.connect(self.reject)  # Verbindet das rejected-Signal (Abbrechen-Klick) mit der reject-Methode des Dialogs.
        main_layout.addWidget(self.buttonBox)  # Fügt die Button-Box zum Hauptlayout hinzu.
        
    def accept(self): # Akzeptiert die Änderungen und speichert sie.
        new_name = self.name_edit.text()  # Liest den neuen Namen aus dem Eingabefeld.
        self.player.name_label = new_name  # Aktualisiert das name_label-Attribut des Spielerobjekts.
        self.player.name_text.setPlainText(new_name)  # Aktualisiert den Text des QGraphicsTextItem des Spielers.
        # Ändert den Namen des Spielers und aktualisiert die Position des Namenslabels.
        if hasattr(self.player, 'updateNameTextPosition'):  # Überprüft, ob der Spieler eine Methode zur Aktualisierung der Namenstextposition hat.
            self.player.updateNameTextPosition()  # Ruft die Methode zur Aktualisierung der Position des Namenstextes auf.
        super().accept()  # Ruft die accept-Methode der Basisklasse auf, um den Dialog zu schließen.

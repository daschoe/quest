"""A textfield of which the entry gets validated before the next page is loaded."""

from PySide6.QtCore import QRegularExpression, QLocale
from PySide6.QtGui import QIntValidator, QDoubleValidator, QRegularExpressionValidator
from PySide6.QtWidgets import QLineEdit


class PasswordEntry(QLineEdit):
    """A textfield of which the entry gets validated against a list of possible entries
    when the user wants to go to the next page."""
    def __init__(self, file_passwords, qid, policy=None, parent=None, objectname=None):
        """
        Parameters
        ----------
        file_passwords : str
            file/path of valid entries for this field (line separated)
        qid : str
            id of the question
        policy : list<str>, optional
            restricts the entry possibilities of this field; choose between "int", "double" and "regex" for the first entry,
            for details see `AnswerTextField.py`
        parent : QObject, optional
            widget/layout this widget is embedded in
        objectname : str, optional
            name of the object, if it is supposed to be styled individually

        Raises
        ------
        ValueError
            if an unknown type of policy is given
        """
        super(PasswordEntry, self).__init__(parent=parent)
        if file_passwords != "":
            with open(file_passwords) as f:
                self.passwords = f.read().splitlines()
        else:
            self.passwords = []

        if objectname is not None:
            self.name = objectname
            self.setObjectName(objectname)
        else:
            self.name = None
        if policy is not None and policy != ["None"]:
            if policy[0].lower() == "int":
                self.setValidator(QIntValidator(bottom=int(policy[1]), top=int(policy[2])))
            elif policy[0].lower() == "double":
                validator = QDoubleValidator(bottom=float(policy[1]), top=float(policy[2]), decimals=int(policy[3]))
                validator.setNotation(QDoubleValidator.Notation.StandardNotation)
                self.setValidator(validator)
                if QLocale().decimalPoint() == ",":  # workaround: QDoubleValidator only registers "," but not "." (depending on locale)
                    self.textChanged.connect(lambda: self.setText(self.text().replace(".", ",")))
            elif policy[0].lower() == "regex":
                self.setValidator(QRegularExpressionValidator(QRegularExpression(policy[1])))
            else:
                raise ValueError("Unknown validator found {}.".format(policy[0]))
        self.textChanged.connect(lambda: parent.log(qid, self))

    def validate(self):
        """Check if the user-given string is in the list of valid passwords."""
        if (len(self.text()) > 0) and (len(self.passwords) > 0) and (not self.text() in self.passwords):
            self.setToolTip("Invalid password.")
            self.setObjectName("required")
            return False
        elif (len(self.text()) == 0) and (len(self.passwords) > 0) and (not self.text() in self.passwords):
            return False
        elif (len(self.text()) == 0) and (len(self.passwords) > 0) and ('' in self.passwords):
            return True
        else:
            self.setToolTip("")
            self.setObjectName(self.name if self.name is not None else "")
            return True

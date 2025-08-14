"""
This class creates a Textfield.
"""
from PySide6.QtCore import QRegularExpression, QLocale
from PySide6.QtGui import QIntValidator, QDoubleValidator, QRegularExpressionValidator
from PySide6.QtWidgets import QPlainTextEdit, QLineEdit


def make_answers(size, qid, policy=None, parent=None, objectname=None):
    """
        Create a textfield of the specified size.

        Parameters
        ----------
        size : int
            1 is a single line text field, >1 a multiline text field
        qid : str
            id of the question
        policy : list[str], optional
            restriction what can be entered, e.g. int, double, regex, with according parameters
        parent : QObject, optional
            widget/layout this widget is embedded in
        objectname : str, optional
            name of the object, if it is supposed to be styled individually

        Raises
        ------
        ValueError
            if an unknown type of policy is specified or if a value <=0 is given for `size`

        Returns
        -------
        QLineEdit or QPlainTextEdit
            the created text field
    """
    if size == 1:
        text = QLineEdit()
        if objectname is not None:
            text.setObjectName(objectname)
        if policy is not None and policy != ["None"]:
            if policy[0].lower() == "int":
                text.setValidator(QIntValidator(bottom=int(policy[1]), top=int(policy[2])))
            elif policy[0].lower() == "double":
                validator = QDoubleValidator(bottom=float(policy[1]), top=float(policy[2]), decimals=int(policy[3]))
                validator.setNotation(QDoubleValidator.Notation.StandardNotation)
                # another parameter would be: notation (scientific 1.5E-2 or standard 0.015=default)
                text.setValidator(validator)
                if QLocale().decimalPoint() == ",":  # workaround: QDoubleValidator only registers "," but not "." (depending on locale)
                    text.textChanged.connect(lambda: text.setText(text.text().replace(".", ",")))
            elif policy[0].lower() == "regex":
                text.setValidator(QRegularExpressionValidator(QRegularExpression(policy[1])))
            else:
                raise ValueError(f"Unknown validator found {policy[0]}.")
    elif size > 1:
        # big text fields do not use validators
        text = QPlainTextEdit()
        if objectname is not None:
            text.setObjectName(objectname)
        # set size/height
        # print(size, text.font().pointSize(), size * QFontMetrics(text.font()).lineSpacing())
        # text.setFixedHeight(size * QFontMetrics(text.font()).lineSpacing()*2)
    else:
        raise ValueError(f"Size of text answer needs to be >= 1. Found {size}.")
    text.textChanged.connect(lambda: parent.log(qid, text))
    return text

"""Customized QTreeWidget with drag&drop functionality according to the questionnaire structure."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragMoveEvent
from PySide6.QtWidgets import QTreeWidget, QAbstractItemView, QInputDialog, QLineEdit


# noinspection PyUnresolvedReferences
class Tree(QTreeWidget):
    """QTreeWidget with custom drag&drop features.

    Attributes
    ----------
    tree_changed : pyqtSignal
        a notification is sent whenever the tree structure changes
    error_message : pyqtSignal
        a notification that is sent when an action is aborted
    parent : QObject, optional
        widget/layout this widget is embedded in
    """
    tree_changed = Signal()
    error_message = Signal(str)

    def __init__(self, parent=None):
        """

        Parameters
        ----------
        parent : QObject, optional
            widget/layout this widget is embedded in
        """
        super().__init__(parent)

        self.header().hide()
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDragEnabled(True)
        self.setDefaultDropAction(Qt.MoveAction)

    def dragMoveEvent(self, event):
        """Changed behaviour on dragging.

        Don't accept any drops from somewhere else.

        Parameters
        ----------
        event : QDragMoveEvent
        """
        super().dragMoveEvent(event)
        if self.dropIndicatorPosition() == QAbstractItemView.OnViewport:
            # do not accept drop on the viewport
            event.ignore()

    def dropEvent(self, event):
        """Changed behaviour on drop, according to the questionnaire structure.

        This means: \n
        - questions can only be dropped on pages or above/below other questions. If they are moved to another page, it has to be checked that there is no other question with that name.
        - pages can only be dropped on the root element or above/below other pages.
        - the root element can't be moved anywhere.

        Parameters
        ----------
        event : QDropEvent
        """
        source = self.indexFromItem(self.selectedItems()[0])
        if event.source() == self:
            if self.dropIndicatorPosition() == QAbstractItemView.OnViewport:
                event.ignore()
            if self.dropIndicatorPosition() == QAbstractItemView.OnItem:
                tree_target_item = self.itemAt(event.position().toPoint())
                target_children = []
                for ch in range(self.itemAt(event.position().toPoint()).childCount()):
                    target_children.append(self.itemAt(event.position().toPoint()).child(ch))
                if tree_target_item.parent() is None:  # something was dropped on root
                    if source.parent().data() == tree_target_item.text(0):
                        # root item only accepts pages
                        super().dropEvent(event)
                        self.tree_changed.emit()
                    else:
                        event.ignore()  # Tried to drop question on root
                elif tree_target_item.parent().parent() is None and source.parent().data() is not None and source.parent().parent().data() is not None and source.parent().parent().parent().data() is None:
                    # question on page
                    if tree_target_item.text(0) == source.parent().data():
                        event.ignore()  # dropped on the same page it already is in
                    else:
                        if tree_target_item.childCount() == 0:
                            super().dropEvent(event)
                            self.tree_changed.emit()
                        else:
                            found = False
                            children = []
                            for child in range(tree_target_item.childCount()):
                                children.append(tree_target_item.child(child))
                                if tree_target_item.child(child).text(0) == source.data():
                                    found = True
                            if not found:  # just drop the question
                                super().dropEvent(event)
                                self.tree_changed.emit()
                            else:
                                text, ok = self.rename_question(children)
                                if ok:
                                    present = False
                                    for ch in children:
                                        if text == ch.text(0):
                                            event.ignore()
                                            present = True
                                            self.error_message.emit("Move aborted. Name already exists.")
                                    if not present:
                                        self.currentItem().setText(0, text)
                                        super().dropEvent(event)
                                        self.tree_changed.emit()
                                else:
                                    event.ignore()
                                    self.error_message.emit("Move aborted.")

                else:
                    event.ignore()
            else:  # move above/below item
                tree_target_item = self.itemAt(event.position().toPoint())
                if tree_target_item.parent() is None:
                    event.ignore()  # don't move anything above/below root
                elif (tree_target_item.parent().parent() is None and source.parent().parent().data() is not None) or \
                        (tree_target_item.parent().parent() is not None and source.parent().parent().data() is None):
                    # dragged question above/below page OR page above/below question
                    event.ignore()
                elif tree_target_item.parent().text(0) != source.parent().data():
                    # one question ist dropped above/below another from a different page
                    # -> check if a child named like this already exists
                    children_found = True
                    current_item = tree_target_item
                    children = [current_item]
                    while children_found:
                        item_below = self.itemBelow(current_item)
                        if item_below is not None and item_below.parent().text(0) == tree_target_item.parent().text(0):
                            children.append(item_below)
                            current_item = item_below
                        else:
                            children_found = False
                    children_found = True
                    current_item = tree_target_item
                    while children_found:
                        item_above = self.itemAbove(current_item)
                        if item_above.parent().text(0) == tree_target_item.parent().text(0):
                            children.append(item_above)
                            current_item = item_above
                        else:
                            children_found = False
                    found = False
                    for ch in children:
                        if ch.text(0) == source.data():
                            found = True
                    if not found:  # just drop the question
                        super().dropEvent(event)
                        self.tree_changed.emit()
                    else:
                        text, ok = self.rename_question(children)
                        if ok:
                            present = False
                            for ch in children:
                                if text == ch.text(0):
                                    event.ignore()
                                    present = True
                                    self.error_message.emit("Move aborted. Name already exists.")
                            if not present:
                                self.currentItem().setText(0, text)
                                super().dropEvent(event)
                                self.tree_changed.emit()
                        else:
                            event.ignore()
                            self.error_message.emit("Move aborted.")
                else:
                    super().dropEvent(event)
                    self.tree_changed.emit()

    def rename_question(self, children):
        """Renaming dialog and logic for moving a question.

        Parameters
        ----------
        children : list of QTreeWidgetItem
            list of question-nodes of the page the question got moved to.

        Returns
        -------
        tuple
            text : str or None
                new name of the question or None if the renaming process was cancelled
            ok : bool
                True if renaming was executed successfully
        """
        text, ok = QInputDialog.getText(self, "Rename question", "Rename the moved question (the name already existed):", QLineEdit.Normal)
        if not ok:
            return None, ok
        else:
            for ch in children:
                if text == ch.text(0):
                    text, ok = self.rename_question(children)
            return text, ok

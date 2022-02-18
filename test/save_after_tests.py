"""Testing the behaviour of save_after"""

from context import *


@pytest.fixture
def gui_init():
    """Start GUI"""
    gui = QEditGuiMain()
    return gui


@pytest.fixture
def run():
    """Execute the questionnaire."""
    return StackedWindowGui("./test/save_test.txt")


@pytest.fixture
def run2():
    """Execute the questionnaire."""
    return StackedWindowGui("./test/save_test_2.txt")


@pytest.fixture
def run3():
    """Execute the questionnaire."""
    return StackedWindowGui("./test/save_test_3.txt")


# noinspection PyArgumentList
def test_execute_questionnaire_1(run, qtbot):
    if os.path.exists("./test/results/results.csv"):
        os.remove("./test/results/results.csv")
    assert run.Stack.count() == 2
    assert run.forwardbutton.text() == "Absenden"
    assert run.forwardbutton.isEnabled()
    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(run.forwardbutton, Qt.LeftButton)
    assert run.forwardbutton.text() == "Absenden"
    assert run.forwardbutton.isEnabled() == False

    os.remove("./test/results/results.csv")


# noinspection PyArgumentList
def test_execute_questionnaire_2(run2, qtbot):
    if os.path.exists("./test/results/results.csv"):
        os.remove("./test/results/results.csv")
    assert run2.Stack.count() == 2
    assert run2.forwardbutton.text() == "Weiter"
    assert run2.forwardbutton.isEnabled()
    QTest.mouseClick(run2.forwardbutton, Qt.LeftButton)
    assert run2.forwardbutton.text() == "Absenden"
    assert run2.forwardbutton.isEnabled()
    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(run2.forwardbutton, Qt.LeftButton)
    assert run2.forwardbutton.isEnabled() == False

    os.remove("./test/results/results.csv")


# noinspection PyArgumentList
def test_execute_questionnaire_3(run3, qtbot):
    if os.path.exists("./test/results/results.csv"):
        os.remove("./test/results/results.csv")
    assert run3.Stack.count() == 3
    assert run3.forwardbutton.text() == "Absenden"
    assert run3.forwardbutton.isEnabled()
    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(run3.forwardbutton, Qt.LeftButton)
    assert run3.forwardbutton.text() == "Weiter"
    assert run3.forwardbutton.isEnabled()
    QTest.mouseClick(run3.forwardbutton, Qt.LeftButton)
    assert run3.forwardbutton.text() == "Weiter"
    assert run3.forwardbutton.isEnabled() == False

    os.remove("./test/results/results.csv")

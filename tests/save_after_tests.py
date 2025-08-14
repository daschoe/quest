"""Testing the behaviour of save_after"""

from tests.context import pytest, QEditGuiMain, QTimer, StackedWindowGui, QTest, Qt, handle_dialog, os


@pytest.fixture
def gui_init():
    """Start GUI"""
    gui = QEditGuiMain()
    return gui


@pytest.fixture
def run():
    """Execute the questionnaire."""
    return StackedWindowGui(os.path.join(os.getcwd(), "tests/save_test.txt"))


@pytest.fixture
def run2():
    """Execute the questionnaire."""
    return StackedWindowGui(os.path.join(os.getcwd(), "tests/save_test_2.txt"))


@pytest.fixture
def run3():
    """Execute the questionnaire."""
    return StackedWindowGui(os.path.join(os.getcwd(), "tests/save_test_3.txt"))


# noinspection PyArgumentList
def test_execute_questionnaire_1(run, qtbot):
    if os.path.exists("./tests/results/results.csv"):
        [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]
    assert run.Stack.count() == 2
    assert run.forwardbutton.text() == "Absenden"
    assert run.forwardbutton.isEnabled()
    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(run.forwardbutton, Qt.MouseButton.LeftButton)
    assert run.forwardbutton.text() == "Absenden"
    assert not run.forwardbutton.isEnabled()

    [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]


# noinspection PyArgumentList
def test_execute_questionnaire_2(run2, qtbot):
    if os.path.exists("./tests/results/results.csv"):
        [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]
    assert run2.Stack.count() == 2
    assert run2.forwardbutton.text() == "Weiter"
    assert run2.forwardbutton.isEnabled()
    QTest.mouseClick(run2.forwardbutton, Qt.MouseButton.LeftButton)
    assert run2.forwardbutton.text() == "Absenden"
    assert run2.forwardbutton.isEnabled()
    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(run2.forwardbutton, Qt.MouseButton.LeftButton)
    assert not run2.forwardbutton.isEnabled()
    [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]


# noinspection PyArgumentList
def test_execute_questionnaire_3(run3, qtbot):
    if os.path.exists("./tests/results/results.csv"):
        [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]
    assert run3.Stack.count() == 3
    assert run3.forwardbutton.text() == "Absenden"
    assert run3.forwardbutton.isEnabled()
    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(run3.forwardbutton, Qt.MouseButton.LeftButton)
    assert run3.forwardbutton.text() == "Weiter"
    assert run3.forwardbutton.isEnabled()
    QTest.mouseClick(run3.forwardbutton, Qt.MouseButton.LeftButton)
    assert run3.forwardbutton.text() == "Weiter"
    assert not run3.forwardbutton.isEnabled()

    [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]

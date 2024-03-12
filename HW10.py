import re, random, sys
from collections import Counter, defaultdict
from math import prod
from string import ascii_lowercase
from pathlib import Path
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import requests
from bs4 import BeautifulSoup


LETTERS = {
    Qt.Key.Key_A: 'a',
    Qt.Key.Key_B: 'b',
    Qt.Key.Key_C: 'c',
    Qt.Key.Key_D: 'd',
    Qt.Key.Key_E: 'e',
    Qt.Key.Key_F: 'f',
    Qt.Key.Key_G: 'g',
    Qt.Key.Key_H: 'h',
    Qt.Key.Key_I: 'i',
    Qt.Key.Key_J: 'j',
    Qt.Key.Key_K: 'k',
    Qt.Key.Key_L: 'l',
    Qt.Key.Key_M: 'm',
    Qt.Key.Key_N: 'n',
    Qt.Key.Key_O: 'o',
    Qt.Key.Key_P: 'p',
    Qt.Key.Key_Q: 'q',
    Qt.Key.Key_R: 'r',
    Qt.Key.Key_S: 's',
    Qt.Key.Key_T: 't',
    Qt.Key.Key_U: 'u',
    Qt.Key.Key_V: 'v',
    Qt.Key.Key_W: 'w',
    Qt.Key.Key_X: 'x',
    Qt.Key.Key_Y: 'y',
    Qt.Key.Key_Z: 'z'
}

WORDLIST = Path("wordle-answers-alphabetical.txt").read_text().splitlines()
frequencies = Counter(''.join(WORDLIST))

QLABEL_BASE = "QLabel {{background: #{}; color: #00aeef; border: 3px inset #5252cc; font: 'Noto Serif';}}"
QLABEL_DEFAULT = "QLabel {background: #002050; color: #00aeef; border: 3px outset #5252cc; font: 'Noto Serif';}"

def get_weight(word):
    occurences = Counter()
    weight = 0
    for letter in word:
        weight += frequencies[letter] * 0.5**occurences[letter]
        occurences[letter]+=1
    return weight

def sort_by_weight(words):
    return sorted(words, key=lambda x: - get_weight(x))

class Cell(QLabel):
    representation = {
        'Absent': QLABEL_BASE.format('ff4200'),
        'Correct': QLABEL_BASE.format('55ff00'),
        'Present': QLABEL_BASE.format('ccff00')
    }
    def __init__(self):
        super().__init__()
        self.setFixedSize(64, 64)
        self.setFont(Font(36))
        self.setStyleSheet(QLABEL_DEFAULT)
    
    def represent(self, state):
        self.setStyleSheet(Cell.representation[state])
        self.repaint()
    
    def reset(self):
        self.setStyleSheet(QLABEL_DEFAULT)
        self.setText('')

class Font(QFont):
    def __init__(self, size):
        super().__init__()
        self.setFamily("Noto Serif")
        self.setStyleHint(QFont.StyleHint.Times)
        self.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setPointSize(size)
        self.setHintingPreference(QFont.HintingPreference.PreferFullHinting)

class LeftPane(QListWidget):
    def __init__(self):
        super(LeftPane, self).__init__()
        font = Font(9)
        self.setFont(font)
        self.setDragDropMode(QAbstractItemView.DragDropMode.NoDragDrop)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(True)
        self.setFixedWidth(80)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.itemClicked.connect(self.onItemClicked)
    
    def onItemClicked(self, item):
        choice = item.text()
        board = self.window().board
        if board.tries < 6: ## Number of guesses
            board.guess = list(choice)
            for i, l in zip(range(5), choice):
                board.grid.itemAtPosition(board.tries, i).widget().setText(l)
            board.evaluate()

class Board(QGroupBox):
    def __init__(self):
        super().__init__()
        self.tries = 0
        self.column = 0
        self.answer = random.choice(WORDLIST)
        self.guess = []
        self.agent = Agent()
        self.grid = QGridLayout(self)
        self.won = False
        for row in range(6): ## Number of guesses
            for column in range(5):
                self.grid.addWidget(Cell(), row, column)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    def judge(self, guess):
        judgement = []
        for a, b in zip(self.answer, guess):
            if b not in self.answer:
                judgement.append('Absent')
            elif a == b:
                judgement.append('Correct')
            else:
                judgement.append('Present')
        return judgement
    
    def represent(self, judgement):
        for column, state in zip(range(5), judgement):
            self.grid.itemAtPosition(self.tries, column).widget().represent(state)
    
    def reset(self):
        self.answer = random.choice(WORDLIST)
        self.agent = Agent()
        self.guess.clear()
        for row in range(self.tries):
            for column in range(5):
                self.grid.itemAtPosition(row, column).widget().reset()
        self.column = 0
        self.tries = 0
        self.window().leftpane.clear()
        self.window().leftpane.addItems(WORDLIST)

    def checkWord(self, word):
        url = f"https://dictionary.com/browse/{''.join(word)}"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        result = soup.find_all('span', {'class':'E17D6zMGNMyhZ9DoRo9R'})
        print(len(result))

    
    def evaluate(self):
        if self.tries < 6: ## Number of guesses
            # if ''.join(self.guess) not in WORDLIST:

            ### Attempting to check any word at all ###

            # correctLetters = {i : len([j for j in self.answer if j == i]) for i in list(self.answer)}
            # sequence = []
            # for num,i in enumerate(self.guess):
            #     if i in correctLetters.keys():

            #         if correctLetters[i] > 0:
            #             correctLetters[i] = correctLetters[i] - 1
            #             if self.guess[num] == self.answer[num]:
            #                 sequence.append("Green")
            #             else:
            #                 sequence.append("Yellow")
            #         else: 
            #             sequence.append("Red")
            #     else:
            #         sequence.append("Red")

            # for n, i in enumerate(self.answer):
            #     if i in self.guess:
            #         seq[self.answer.find(i)] = "Green"

            # tempAns = self.answer
            # tempGuess = self.guess
            # seq = []
            # for i in range(5):
            #     for j in range(5):
            #         if tempAns[i] == tempGuess[j]:
            #             seq[i] = "Green"
            #             tempGuess[j] = "="
            #             continue
            #             # BREAK OUT OF THE FIRST FOR LOOP
            #         elif: tempAns[i] in tempGuess:
            #             seq[i] = "Yellow"
            #             tempGuess[tempGuess.find(tempAns[i])] = "-"
            #         else:
            #             seq[i] = "Red"
            # WHILE LOOPS USE THEMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM CYCLE I AND J THEN ADD ONE TO EACH

            # if ''.join(self.guess) not in WORDLIST:
            # print(f"https://dictionary.com/browse/{''.join(self.guess)}")
            # r = requests.get(f"https://dictionary.com/browse/{''.join(self.guess)}")
            # soup = BeautifulSoup(r.text, "html.parser")
            # result = soup.find_all('span', {'class':'E17D6zMGNMyhZ9DoRo9R'})
            # print(len(result))
            # self.checkWord(self.guess)
            url = f"https://www.dictionary.com/browse/{''.join(self.guess)}"
            r = requests.get(url)
            # print(r.status_code)
            if len(self.guess) == 5:
                if r.status_code == 200:
                    judgement = ["Absent", "Absent", "Absent", "Absent", "Absent"]
                    i = 0
                    tempAns = list(self.answer)
                    tempGuess = self.guess
                    # if len(tempGuess)==5:
                    while i < len(tempGuess):
                        if tempGuess[i] in tempAns:
                            if tempGuess[i] == tempAns[i]:
                                judgement[i] = ("Correct")
                                tempAns[i] = 0
                        i += 1
                    i = 0
                    while i < len(tempGuess):
                        if tempGuess[i] in tempAns and judgement[i] != "Correct":
                            judgement[i] = ("Present")
                            tempAns[tempAns.index(tempGuess[i])] = 0
                        # else:
                        #     judgement[i] = ("Absent")
                        i += 1
                    print(self.answer) # Checking answer on terminal

                    # HAH IT WORKS IT WOOOORKS

                    ### ###

                    self.agent.update(list(zip(self.guess, judgement)))
                    self.window().leftpane.clear()
                    self.window().leftpane.addItems(self.agent.pool)
                    self.guess.clear()
                    self.column = 0
                    self.represent(judgement)
                    self.tries += 1

                    if judgement == ['Correct'] * 5:
                        # if ''.join(self.guess) not in WORDLIST:
                        msg = QMessageBox(self.window())
                        msg.setIcon(QMessageBox.Icon.Information)
                        msg.setText('Congratulations! You won!')
                        msg.setWindowTitle('Success')
                        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                        msg.exec()
                        self.reset()

                else:
                    msg = QMessageBox(self.window())
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setText('Invalid word.')
                    msg.setWindowTitle('Invalid Input')
                    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                    msg.exec()



                # msg = QMessageBox(self.window())
                # msg.setIcon(QMessageBox.Icon.Warning)
                # msg.setText('Inputted word is not present in the wordlist')
                # msg.setWindowTitle('Invalid Input')
                # msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                # msg.exec()
                # return
            # if len(self.guess) == 5:

                # judgement = ["Absent", "Absent", "Absenta", "Absent", "Absent"]
                # i = 0
                # tempAns = list(self.answer)
                # tempGuess = self.guess
                # # if len(tempGuess)==5:
                # while i < len(tempGuess):
                #     if tempGuess[i] in tempAns:
                #         if tempGuess[i] == tempAns[i]:
                #             judgement[i] = ("Correct")
                #             tempAns[i] = 0
                #         else:
                #             judgement[i] = ("Present")
                #             tempAns[tempAns.index(tempGuess[i])] = 0
                #     else:
                #         judgement[i] = ("Absent")
                #     i += 1

                # # judgement = self.judge(self.guess)
                # self.agent.update(list(zip(self.guess, judgement)))
                # self.window().leftpane.clear()
                # self.window().leftpane.addItems(self.agent.pool)
                # self.guess.clear()
                # self.column = 0
                # self.represent(judgement)
                # self.tries += 1
                # if judgement == ['Correct'] * 5:
                #     # if ''.join(self.guess) not in WORDLIST:
                #     msg = QMessageBox(self.window())
                #     msg.setIcon(QMessageBox.Icon.Information)
                #     msg.setText('Congratulations! You won!')
                #     msg.setWindowTitle('Success')
                #     msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                #     msg.exec()
                #     self.reset()
            if self.tries == 6: ## Number of guesses
                msg = QMessageBox(self.window())
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setText('Condolences... You lost...')
                msg.setWindowTitle('Failure')
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
                self.reset()
    
    
    def keyPressEvent(self, e: QKeyEvent) -> None:
        # if self.grid.itemAtPosition(self.tries, self.column) != None:
        if (e.key() in LETTERS) & (self.grid.itemAtPosition(self.tries, self.column) != None):
            letter = LETTERS[e.key()]
            if self.column < 5:
                self.guess.append(letter)
                self.grid.itemAtPosition(self.tries, self.column).widget().setText(letter)
                self.column += 1
        elif e.key() == Qt.Key.Key_Backspace:
            if self.column > 0:
                self.guess.pop(-1)
                self.column -= 1
                self.grid.itemAtPosition(self.tries, self.column).widget().reset()
        elif e.key() == Qt.Key.Key_Return:
            self.evaluate()

class Agent:
    def __init__(self):
        self.pool = WORDLIST.copy()
        self.letters = ascii_lowercase
        self.pattern = ''
        self.present = set()
    
    def update(self, conditions):
        pool = list()
        self.process(conditions)
        for word in self.pool:
            if re.match(self.pattern, word):
                if not self.present or all(l in word for l in self.present):
                    pool.append(word)
        self.pool = sort_by_weight(pool)
    
    def process(self, conditions):
        for letter, state in conditions:
            if state == 'Absent':
                self.letters = self.letters.replace(letter, '')
        
        pattern = []
        self.present.clear()
        for letter, state in conditions:
            if state == 'Absent':
                pattern.append('[' + self.letters + ']')
            elif state == 'Present':
                pattern.append('[' + self.letters.replace(letter, '') + ']')
                self.present.add(letter)
            elif state == 'Correct':
                pattern.append(letter)
        
        self.pattern = '^' + ''.join(pattern) + '$'

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        frame = self.frameGeometry()
        center = self.screen().availableGeometry().center()
        frame.moveCenter(center)
        self.move(frame.topLeft())
        font = Font(10)
        self.setFont(font)
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.hbox = QHBoxLayout(self.centralwidget)
        self.leftpane = LeftPane()
        self.leftpane.addItems(WORDLIST)
        self.hbox.addWidget(self.leftpane)
        self.leftpane.setHidden(True)
        self.board = Board()
        self.hbox.addWidget(self.board)
        self.setWindowTitle('Wordle 2 Bitches')

if __name__ == '__main__':
    app = QApplication([])
    app.setStyle('Fusion')
    window = Window()
    window.show()
    window.setFixedSize(window.size())
    sys.exit(app.exec())
from PySide2 import QtCore, QtWidgets, QtGui
from random import shuffle

class mainWindow(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.phase = None;
        self.selected_card = None;
        self.selected_card_button = None;
        self.drawn_card = None;
        
        self.deck = []
        self.hand = []
        self.tableau = []
        self.tableau_new = []
        self.doors = []
        self.hand_enabled = True
        
        self.build_deck()
        self.restockHand()
        
        self.setup_UI()
        
        self.choose_card_phase()
        
    def build_deck(self):
        
        deck = []
        colors = ["brown", "green", "blue", "red"]

        for clrInd in range(4):
            for i in range(2): deck.append((colors[clrInd], "[]")) # doors
            for i in range(3): deck.append((colors[clrInd], "D"))  # moon
            for i in range(4): deck.append((colors[clrInd], "@++"))  # key
            for i in range(6+clrInd): deck.append((colors[clrInd], "*"))  # sun

        for i in range(10): deck.append(("", "NMR")) # Nightmare

        shuffle(deck)
        self.deck = deck
        
    def restockHand(self): # Returns True or False depending on whether or not you can continue(True) or lose (False)
        print("Restocking")
        needToReshuffle = []
        while len(self.hand)<5:
            if len(self.deck)==0: return(False)
            potential_card = self.deck.pop(0)
            if potential_card[1]=='NMR' or potential_card[1]=='[]':
                needToReshuffle.append(potential_card)
            else:
                self.hand.append(potential_card)
        for card in needToReshuffle: self.deck.append(card)
        shuffle(self.deck)
        return(True)
    
    def checkWin(self):
        if len(self.doors)==8: return(True)
        return(False)
        
    def check_final(self):
        box = QtWidgets.QMessageBox()
        box.setStyleSheet("font-size: 26px")
        if self.checkWin():
            message = "YOU WON!!!  "
        else:
            message = "YOU LOST!!!  "
        box.setText(message)
        result = box.exec_()
        exit()

    def hasKey(self, color=None):
        if color is None:
            for card in self.hand:
                if card[1]=='@++': return(True)
            return(False)
        else:
            for card in self.hand:
                if card[1]=='@++' and card[0]==color: return(True)
            return(False)

    def isNightmare(self, card):
        return(card[1]=='NMR')

    def isKey(self, card):
        return(card[1]=='@++')

    def isDoor(self, card):
        return(card[1]=='[]')
        
    def set_message(self, message):
        return
        self.message_area.setText(message)
        
    def enable_hand(self, status, exclude_selected=False):
        self.hand_enabled = status
        
    def enable_hand_actions(self,status):
        
        if status:
            self.action_frame.play_btn.setEnabled(True)
            self.action_frame.discard_btn.setEnabled(True)
        else:
            self.action_frame.play_btn.setEnabled(False)
            self.action_frame.discard_btn.setEnabled(False)
        
    def setup_UI(self):
    
        self.layout = QtWidgets.QVBoxLayout()
        
        self.setStyleSheet("font-size: 18px")
        
        self.top_frame = TopFrame(self)
        #self.message_area = self.top_frame.message_area
        self.doors_frame = self.top_frame.doors_frame
        
        self.middle_frame = MiddleFrame(self)
        self.deck_number = self.middle_frame.deck_number
        self.hand_frame = self.middle_frame.hand_frame
        self.action_frame = self.middle_frame.action_frame
        
        self.tableau_frame = TableauFrame(self)
        
        self.layout.addWidget(self.top_frame)
        self.layout.addWidget(self.middle_frame)
        self.layout.addWidget(self.tableau_frame)
        
        self.setLayout(self.layout)
        
    def update_UI(self):
        
        for card in self.tableau_new:
            self.tableau_frame.add_card(card)
        self.tableau_new = []
        
        num_of_doors = len(self.doors)
        for i in range(8):
            if i < num_of_doors:
                card = self.doors[i]
            else:
                card = []
            self.doors_frame.doors[i].set_card_image(card)
            
        num_hand = len(self.hand)
        for i in range(5):
            if i < num_hand:
                card = self.hand[i]
            else:
                card = []
            self.hand_frame.cards[i].set_card_image(card)
            
        self.deck_number.setText("Cards in deck: " + str(len(self.deck)))
        
    def choose_card_phase(self):
        self.phase = "choose"
        self.set_message("Click on a card in the hand to choose")
        self.enable_hand(True)
        self.enable_hand_actions(False)
        print(self.hand)

    def choose_card(self):
        if self.hand_enabled:
        
            print(self.hand)
            
            if self.selected_card_button:
                self.selected_card_button.setStyleSheet("border: 3px solid white");
            self.sender().setStyleSheet("border: 3px solid gray");
            
            self.selected_card_button = self.sender()
            self.selected_card = self.sender().card_index
            print(self.hand[self.selected_card])
            if self.phase != "action":
                self.choose_action_phase()
        
    def choose_action_phase(self):
        self.phase = "action"
        self.set_message("Card selected. Choose whether to play or discard card, or choose another card")
        #self.enable_hand(False)
        self.enable_hand_actions(True)
        
    def play_card(self):
    
        card = self.hand[self.selected_card]
    
        if len(self.tableau)==0 or self.tableau[-1][1]!=card[1]: # Different symbols
            
            card = self.hand.pop(self.selected_card)
            self.hand_frame.cards[self.selected_card].set_empty_card()
            self.tableau.append(card)
            self.tableau_new.append(card)
            
            if len(self.tableau)>2:
                if self.tableau[-1][0]==self.tableau[-2][0] and self.tableau[-1][0]==self.tableau[-3][0]: # Matching colors
                    door_index=-1
                    for i,c in enumerate(self.deck):
                        if self.isDoor(c) and c[0]==self.tableau[-1][0]:
                            door_index=i
                    if door_index!=-1:# found one of that color...claim it
                        self.doors.append(self.deck.pop(door_index))
                    else:
                        box = QtWidgets.QMessageBox()
                        box.setText("Three cards of matching colors in a row but no matching door found.    ")
                        result = box.exec_()
        
        else:
            box = QtWidgets.QMessageBox()
            box.setText("Cannot play a card that matches the previous symbol.    ")
            result = box.exec_()
            
        self.update_UI()
        self.enable_hand_actions(False)
        self.draw_cards()
        
    def discard_card(self):
    
        card = self.hand.pop(self.selected_card)
        self.hand_frame.cards[self.selected_card].set_empty_card()
    
        if self.isKey(card):
            self.prophecy()
        else:
            self.draw_cards()
    
    def draw_cards(self):
    
        if self.checkWin():
            box = QtWidgets.QMessageBox()
            box.setText("YOU WON!!!")
            result = box.exec_()
            exit()
        
        self.update_UI()
    
        if len(self.deck) != 0:
    
            if len(self.hand) < 5:
                self.show_deck()
                card = self.deck.pop(0)
                self.drawn_card = card
                print("Drawn card: " + str(card))
                if self.isNightmare(card):
                    self.deal_with_nightmare()
                elif self.isDoor(card):
                    self.deal_with_door(card)
                else:
                    self.hand.append(card)
                    self.draw_cards()
                    
            else:
                print("Hand full")
                self.update_UI()
                self.choose_card_phase()
                    
        else:
            print("No more cards in deck")
            self.check_final()

    def deal_with_nightmare(self):
        
        print("Nightmare!")
        self.enable_hand(False)
        self.enable_hand_actions(False)
        self.nightmare_window = NightmareWindow(self)
        self.nightmare_window.show()
            
    def discard_hand(self):
        
        while len(self.hand)!=0: self.hand.pop(0)
        self.restockHand()
        self.draw_cards()
        
    def discard_top_5(self):
            
        top5=[]
        for i in range(5):
            if len(self.deck) == 0: break
            potential_card = self.deck.pop(0)
            if potential_card[1] == 'NMR' or potential_card == '[]':
                top5.append(potential_card)

        for card in top5: self.deck.append(card)
        shuffle(self.deck)
        self.draw_cards()
            
    def discard_key(self):

        index_of_key=0
        for i,card in enumerate(self.hand):
            if card[1] == '@++': index_of_key = i
        del self.hand[index_of_key]
        self.update_UI()
        self.draw_cards()
        
    def discard_door(self):

        self.deck.append(self.doors.pop(0))
        shuffle(self.deck)
        self.draw_cards()

    def deal_with_door(self, door):
    
        if self.hasKey(door[0]):
        
            box = QtWidgets.QMessageBox()
            box.setText("You were dealt a " + door[0] + " door. Do you want to use your key?")
            box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            result = box.exec_()

            if result == QtWidgets.QMessageBox.No:
                self.dont_use_key()
            elif result == QtWidgets.QMessageBox.Yes:
                self.use_key()
            
            self.update_UI()
            self.draw_cards()
            
        else:
            box = QtWidgets.QMessageBox()
            box.setText("You were dealt a " + door[0] + " door but you do not have a matching key")
            result = box.exec_()
            self.deck.append(door)
            shuffle(self.deck)
            self.update_UI()
            self.draw_cards()
            
    def use_key(self):
            
        door = self.drawn_card
        index_of_key = 0
        for i, card in enumerate(self.hand):
            if card[1] == '@++' and card[0]==door[0]: index_of_key = i
        del self.hand[index_of_key]
        self.doors.append(door)
     
    def dont_use_key(self):
         
        door = self.drawn_card
        print("You chose not to use your key")
        self.deck.append(door)
        shuffle(self.deck)

    def prophecy(self):
    
        cardsToDisplay = []
        while len(self.deck)>0 and len(cardsToDisplay)<5:
             cardsToDisplay.append(self.deck.pop(0))
        
        self.enable_hand(False)
        self.enable_hand_actions(False)
        self.prophecy_window = ProphecyWindow(cardsToDisplay, self)
        self.prophecy_window.show()
        
            
    def return_to_deck(self, card):
        self.deck.insert(0, card)
        self.show_deck()
        
    def show_deck(self):
        if len(self.deck) > 3:
            x = 3
        else:
            x = len(self.deck)
        for i in range(x):
            print(str(i) + " - " + str(self.deck[i]))

            
class NightmareWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget) 
        
        self.central_widget.layout = QtWidgets.QVBoxLayout()
        
        self.nightmare_card = QtWidgets.QLabel(self.central_widget)
        pixmap = QtGui.QPixmap("img/nightmare.jpg")
        pixmap = pixmap.scaledToWidth(100)
        self.nightmare_card.setPixmap(pixmap)
        self.nightmare_card.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.nightmare_card.setAlignment(QtCore.Qt.AlignCenter)
        self.central_widget.layout.addWidget(self.nightmare_card)
        
        self.label = QtWidgets.QLabel(self.central_widget)
        self.label.setText("YOU WERE DEALT A NIGHTMARE!!!")
        self.label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.central_widget.layout.addWidget(self.label, QtCore.Qt.AlignHCenter)
        
        self.discard_key_button = QtWidgets.QPushButton(self.central_widget, text="Discard a key card from your hand")
        if self.parent().hasKey():
            self.discard_key_button.clicked.connect(self.discard_key)
        else:
            self.discard_key_button.setEnabled(False)
        self.central_widget.layout.addWidget(self.discard_key_button)
        
        self.discard_door_button = QtWidgets.QPushButton(self.central_widget, text="Discard a door card from your doors")
        if len(self.parent().doors)!=0:
            self.discard_door_button.clicked.connect(self.discard_door)
        else:
            self.discard_door_button.setEnabled(False)
        self.central_widget.layout.addWidget(self.discard_door_button)
        
        self.discard_top_button = QtWidgets.QPushButton(self.central_widget, text="Discard top 5 deck cards excluding doors/nightmares")
        self.discard_top_button.clicked.connect(self.discard_top_5)
        self.central_widget.layout.addWidget(self.discard_top_button)
        
        self.discard_hand_button = QtWidgets.QPushButton(self.central_widget, text="Discard your entire hand")
        self.discard_hand_button.clicked.connect(self.discard_hand)
        self.central_widget.layout.addWidget(self.discard_hand_button)
        
        self.central_widget.setLayout(self.central_widget.layout)
        
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, False)
        
        print("Set nightmare window")
        
    def discard_key(self):
        self.close()
        self.parent().discard_key()
        
    def discard_door(self):
        self.close()
        self.parent().discard_door()
        
    def discard_hand(self):
        self.close()
        self.parent().discard_hand()
        
    def discard_top_5(self):
        self.close()
        self.parent().discard_top_5()
        
    
class ProphecyWindow(QtWidgets.QMainWindow):

    def __init__(self, cards, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.cards = cards
        self.processed = 0
        self.card_buttons = []
        self.first_choice = True;
        
        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget) 
        
        self.layout = QtWidgets.QVBoxLayout()
        
        self.label = QtWidgets.QLabel(self.central_widget)
        self.label.setText("PROPHECY - Choose a card to discard")
        self.label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.label)
        
        self.cards_frame = QtWidgets.QWidget(self.central_widget)
        self.cards_frame.layout = QtWidgets.QHBoxLayout()
        
        print("Prophecy cards: " + str(self.cards))
        
        for i, card in enumerate(self.cards):
            card_button = CardButton(i, card, "large", self.cards_frame)
            card_button.clicked.connect(self.choose_card)
            card_button.setStyleSheet("border: 3px solid white")
            self.card_buttons.append(card_button)
            self.cards_frame.layout.addWidget(card_button)
            
        self.cards_frame.setLayout(self.cards_frame.layout)
            
        self.layout.addWidget(self.cards_frame)
        
        self.central_widget.setLayout(self.layout)
        
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, False)
        
        print("Setup prophecy window")
        
    def choose_card(self):
    
        sender = self.sender()
        
        if not sender.card:
            return
    
        card_index = sender.card_index
        
        if self.first_choice:
            self.first_choice = False
            self.label.setText("PROPHECY - Select order to add back to deck")
        else:
            self.parent().return_to_deck(self.cards[card_index])
            
        sender.set_empty_card()
        self.processed = self.processed + 1
        
        if self.processed == len(self.cards):
            self.close()
            self.parent().draw_cards()
            
class CardButton(QtWidgets.QLabel):

    clicked = QtCore.Signal(str)

    def __init__(self, index, card, size, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.card_index = index
        self.card = card
        self.size = size
        self.setScaledContents(True)
        self.set_card_image(card)
        
    def mousePressEvent(self, event):
        self.clicked.emit(str(self.card_index))
        
    def set_card_image(self, card):
    
        if card:
        
            if card[1] == "NMR":
                path = "img/nightmare.jpg"
                
            else:
    
                color = card[0]
                symbol = card[1]
            
                if symbol == "[]":
                    symbol = "door"
                elif symbol == "D":
                    symbol = "moon"
                elif symbol == "*":
                    symbol = "sun"
                elif symbol == "@++":
                    symbol = "key"
                    
                path = "img/" + color + "-" + symbol + ".jpg"
            
        else:
            path = "img/empty.png"
            
        if self.size == "small":
            width = 50
        elif self.size == "large":
            width = 100
        
        pixmap = QtGui.QPixmap(path)
        pixmap = pixmap.scaledToWidth(width)
        self.setPixmap(pixmap)

    def set_empty_card(self):
        self.card = []
        self.setStyleSheet("border: 3px solid white");
        self.set_card_image([])

        
class TopFrame(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.layout = QtWidgets.QHBoxLayout()
        
        '''
        self.message_area = QtWidgets.QLabel(self)
        self.message_area.setText("Welcome to the game")
        self.layout.addWidget(self.message_area)
        '''
        
        self.doors_frame = QtWidgets.QWidget(self)
        self.doors_frame.layout = QtWidgets.QHBoxLayout()
        self.doors_frame.doors = []
        for i in range(8):
            door_placeholder = CardButton(i, [], "small", self.doors_frame)
            door_placeholder.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            self.doors_frame.layout.addWidget(door_placeholder)
            self.doors_frame.doors.append(door_placeholder)
        self.doors_frame.setLayout(self.doors_frame.layout)
        self.layout.addWidget(self.doors_frame)
        
        self.setLayout(self.layout)

        
class MiddleFrame(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.layout = QtWidgets.QHBoxLayout()
        
        self.deck_number = QtWidgets.QLabel(self)
        self.deck_number.setText("Cards in deck: " + str(len(self.parent().deck)))
        self.layout.addWidget(self.deck_number)
        
        self.hand_frame = QtWidgets.QWidget(self)
        self.hand_frame.layout = QtWidgets.QHBoxLayout()
        self.hand_frame.cards = []
        for i, card in enumerate(self.parent().hand):
            hand_card = CardButton(i, card, "large", self.hand_frame)
            hand_card.clicked.connect(self.parent().choose_card)
            hand_card.setStyleSheet("border: 3px solid white");
            self.hand_frame.layout.addWidget(hand_card)
            self.hand_frame.cards.append(hand_card)
        self.hand_frame.setLayout(self.hand_frame.layout)
        self.layout.addWidget(self.hand_frame)
        
        self.action_frame = QtWidgets.QWidget(self)
        self.action_frame.layout = QtWidgets.QVBoxLayout()
        self.action_frame.play_btn = QtWidgets.QPushButton(self.action_frame, text="PLAY")
        self.action_frame.play_btn.clicked.connect(self.parent().play_card)
        self.action_frame.layout.addWidget(self.action_frame.play_btn)
        self.action_frame.discard_btn = QtWidgets.QPushButton(self.action_frame, text="DISCARD")
        self.action_frame.discard_btn.clicked.connect(self.parent().discard_card)
        self.action_frame.layout.addWidget(self.action_frame.discard_btn)
        self.action_frame.setLayout(self.action_frame.layout)
        self.layout.addWidget(self.action_frame)
        
        self.setLayout(self.layout)
        
class TableauFrame(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.cards = []
        
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        
    def add_card(self, card):
    
        
        print("TABLEAU FRAME:" + str(self.cards))
        row, column = divmod(len(self.cards), 12)
        self.cards.append(card)
    
        new_card = CardButton(0, card, "small", self)
        new_card.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.layout.addWidget(new_card, row, column)
        self.setLayout(self.layout)
        
        
def main():
            
    app = QtWidgets.QApplication()
    window = mainWindow()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
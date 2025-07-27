import pyxel
import random

class Card:
    def __init__(self, suit, rank):
        self.suit = suit  # 0:♠, 1:♥, 2:♦, 3:♣
        self.rank = rank  # 1-13 (A,2-10,J,Q,K)
        self.face_up = False
    
    def get_display_rank(self):
        if self.rank == 1:
            return "A"
        elif self.rank == 11:
            return "J"
        elif self.rank == 12:
            return "Q"
        elif self.rank == 13:
            return "K"
        else:
            return str(self.rank)
    
    def get_suit_symbol(self):
        symbols = ["♠", "♥", "♦", "♣"]
        return symbols[self.suit]
    
    def get_color(self):
        return 8 if self.suit in [1, 2] else 0  # 赤 or 黒

class MonteCarloGame:
    def __init__(self):
        self.cards = []
        self.deck = []  # 山札
        self.selected_cards = []
        self.score = 0
        self.game_over = False
        self.win = False
        self.selected_pos = None
        
        # カード配置の設定
        self.card_width = 26
        self.card_height = 32
        self.grid_cols = 5
        self.grid_rows = 5
        self.start_x = 8
        self.start_y = 40
        
        self.init_game()
    
    def init_game(self):
        # デッキを作成
        deck = []
        for suit in range(4):
            for rank in range(1, 14):
                deck.append(Card(suit, rank))
        
        random.shuffle(deck)
        
        # 5x5のグリッドに配置
        self.cards = []
        for row in range(self.grid_rows):
            card_row = []
            for col in range(self.grid_cols):
                if len(deck) > 0:
                    card = deck.pop()
                    card.face_up = True
                    card_row.append(card)
                else:
                    card_row.append(None)
            self.cards.append(card_row)
        
        # 残りのカードは山札に
        self.deck = deck
        
        self.selected_cards = []
        self.score = 0
        self.game_over = False
        self.win = False
    
    def get_card_pos(self, row, col):
        x = self.start_x + col * (self.card_width + 2)
        y = self.start_y + row * (self.card_height + 2)
        return x, y
    
    def get_clicked_card(self, mx, my):
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                if self.cards[row][col] is not None:
                    x, y = self.get_card_pos(row, col)
                    if x <= mx <= x + self.card_width and y <= my <= y + self.card_height:
                        return row, col
        return None, None
    
    def are_adjacent(self, pos1, pos2):
        # 2つの位置が隣接しているかチェック（縦・横・斜め）
        row1, col1 = pos1
        row2, col2 = pos2
        
        row_diff = abs(row1 - row2)
        col_diff = abs(col1 - col2)
        
        # 隣接の条件：行と列の差がそれぞれ1以下で、かつ同じ位置ではない
        return (row_diff <= 1 and col_diff <= 1) and (row_diff + col_diff > 0)
    
    def can_remove_pair(self, card1, card2, pos1, pos2):
        # 隣接チェック
        if not self.are_adjacent(pos1, pos2):
            return False
        
        # 同じランクまたは合計が11になる場合
        if card1.rank == card2.rank:
            return True
        if card1.rank + card2.rank == 11:
            return True
        return False
    
    def remove_selected_cards(self):
        if len(self.selected_cards) == 2:
            row1, col1 = self.selected_cards[0]
            row2, col2 = self.selected_cards[1]
            card1 = self.cards[row1][col1]
            card2 = self.cards[row2][col2]
            pos1 = (row1, col1)
            pos2 = (row2, col2)
            
            if self.can_remove_pair(card1, card2, pos1, pos2):
                self.cards[row1][col1] = None
                self.cards[row2][col2] = None
                self.score += 10
                # カードは削除のみ、詰めは行わない
                return True
        return False
    
    def compact_cards(self):
        # 左上方向にカードを詰める
        # まず全てのカードを収集
        all_cards = []
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                if self.cards[row][col] is not None:
                    all_cards.append(self.cards[row][col])
                self.cards[row][col] = None
        
        # 山札からカードを補充して25枚にする
        while len(all_cards) < 25 and len(self.deck) > 0:
            card = self.deck.pop()
            card.face_up = True
            all_cards.append(card)
        
        # 左上から順番に配置
        card_index = 0
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                if card_index < len(all_cards):
                    self.cards[row][col] = all_cards[card_index]
                    card_index += 1
    
    def check_game_over(self):
        # 残りカードをチェック
        remaining_cards = []
        remaining_positions = []
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                if self.cards[row][col] is not None:
                    remaining_cards.append(self.cards[row][col])
                    remaining_positions.append((row, col))
        
        # 全てのカードがなくなり、山札も空の場合は勝利
        if len(remaining_cards) == 0 and len(self.deck) == 0:
            self.win = True
            self.game_over = True
            return
        
        # 場にカードがない場合（山札から補充されるはず）
        if len(remaining_cards) == 0:
            return
        
        # ペアが作れるかチェック（手詰まり判定）
        for i in range(len(remaining_cards)):
            for j in range(i + 1, len(remaining_cards)):
                if self.can_remove_pair(remaining_cards[i], remaining_cards[j], 
                                      remaining_positions[i], remaining_positions[j]):
                    return  # まだペアが作れる
        
        # ペアが作れない場合はゲームオーバー
        self.game_over = True
    
    def update(self):
        if self.game_over:
            if pyxel.btnp(pyxel.KEY_R):
                self.init_game()
            return
        
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mx, my = pyxel.mouse_x, pyxel.mouse_y
            
            # OKボタンの判定 (画面下部)
            if 60 <= mx <= 100 and 200 <= my <= 220:
                self.compact_cards()
                self.check_game_over()
                return
            
            row, col = self.get_clicked_card(mx, my)
            
            if row is not None and col is not None:
                pos = (row, col)
                
                if pos in self.selected_cards:
                    self.selected_cards.remove(pos)
                else:
                    self.selected_cards.append(pos)
                    
                    if len(self.selected_cards) > 2:
                        self.selected_cards.pop(0)
                    
                    if len(self.selected_cards) == 2:
                        if self.remove_selected_cards():
                            self.selected_cards = []
    
    def draw_card(self, card, x, y, selected=False):
        # カード背景
        color = 7 if not selected else 10
        pyxel.rect(x, y, self.card_width, self.card_height, color)
        pyxel.rectb(x, y, self.card_width, self.card_height, 0)
        
        if card and card.face_up:
            # ランク表示
            rank_str = card.get_display_rank()
            text_color = card.get_color()
            pyxel.text(x + 2, y + 2, rank_str, text_color)
            
            # スート表示（簡易版）
            suit_symbols = ["S", "H", "D", "C"]
            pyxel.text(x + 2, y + 16, suit_symbols[card.suit], text_color)
    
    def draw(self):
        pyxel.cls(15)  # 白背景
        
        # タイトル
        pyxel.text(8, 8, "Monte Carlo", 0)
        pyxel.text(8, 18, f"Score: {self.score}", 0)
        
        # 山札の枚数表示
        pyxel.text(110, 8, f"Deck: {len(self.deck)}", 0)
        
        # 山札の描画（右上）
        if len(self.deck) > 0:
            pyxel.rect(130, 20, 20, 25, 1)
            pyxel.rectb(130, 20, 20, 25, 0)
            pyxel.text(137, 30, "?", 7)
        
        # カード描画
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                card = self.cards[row][col]
                if card is not None:
                    x, y = self.get_card_pos(row, col)
                    selected = (row, col) in self.selected_cards
                    self.draw_card(card, x, y, selected)
        
        # ゲームオーバー表示
        if self.game_over:
            pyxel.rect(20, 100, 120, 80, 0)
            pyxel.rectb(20, 100, 120, 80, 7)
            
            if self.win:
                pyxel.text(60, 115, "YOU WIN!", 10)
            else:
                pyxel.text(50, 115, "GAME OVER", 8)
                pyxel.text(55, 125, "No moves!", 8)
            
            pyxel.text(35, 140, f"Final Score: {self.score}", 7)
            pyxel.text(40, 155, "Press R to restart", 7)
        
        # OKボタン描画
        if not self.game_over:
            pyxel.rect(60, 200, 40, 20, 11)
            pyxel.rectb(60, 200, 40, 20, 0)
            pyxel.text(73, 208, "OK", 0)
        
        # 操作説明
        if not self.game_over:
            pyxel.text(8, 230, "Adjacent cards only", 0)
            pyxel.text(8, 240, "Same rank or sum=11", 0)
            pyxel.text(8, 250, "Click OK to compact", 0)

def main():
    game = MonteCarloGame()
    pyxel.init(160, 256, title="Monte Carlo")
    pyxel.mouse(True)
    pyxel.run(game.update, game.draw)

if __name__ == "__main__":
    main()
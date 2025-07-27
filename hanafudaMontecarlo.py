import pyxel
import random

class Card:
    def __init__(self, month, rank):
        self.month = month  # 1-12 (1月-12月)
        self.rank = rank    # 1-4 (各月の1-4枚目)
        self.face_up = False
    
    def get_display_rank(self):
        return str(self.rank)
    
    def get_month_name(self):
        month_names = ["", "1月", "2月", "3月", "4月", "5月", "6月", 
                      "7月", "8月", "9月", "10月", "11月", "12月"]
        return month_names[self.month]
    
    def get_image_coords(self):
        # 花札の画像座標を計算
        if self.month <= 6:
            # イメージバンク0 (1-6月)
            bank = 0
            month_in_bank = self.month
        else:
            # イメージバンク1 (7-12月)
            bank = 1
            month_in_bank = self.month - 6
        
        # 座標計算：奇数月は左側(x=0,64), 偶数月は右側(x=128,192)
        if month_in_bank % 2 == 1:  # 奇数月 (1,3,5月 または 7,9,11月)
            base_x = (self.rank - 1) * 32  # 0, 32, 64, 96
        else:  # 偶数月 (2,4,6月 または 8,10,12月)
            base_x = 128 + (self.rank - 1) * 32  # 128, 160, 192, 224
        
        # Y座標：月ペアごとに53px間隔
        y = ((month_in_bank - 1) // 2) * 53  # 1,2月→0, 3,4月→53, 5,6月→106
        
        return bank, base_x, y

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
        self.start_y = 20
        
        self.init_game()
    
    def init_game(self):
        # 花札デッキを作成（48枚：12か月×4枚）
        deck = []
        for month in range(1, 13):  # 1月-12月
            for rank in range(1, 5):  # 各月4枚
                deck.append(Card(month, rank))
        
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
        
        # 同じ月のカード同士なら取れる
        if card1.month == card2.month:
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
            pyxel.play(0, 4)
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
        pyxel.play(0, 0)
    
    def update(self):
        if self.game_over:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
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
        if card and card.face_up:
            # 花札画像の描画
            bank, img_x, img_y = card.get_image_coords()
            
            # デバッグ情報を表示
            #pyxel.text(x, y-10, f"{card.month}-{card.rank}", 7)
            
            # 花札画像を描画（透明色指定なし）
            try:
                pyxel.blt(x, y, bank, img_x, img_y, 32, 53, None, None, 0.64)
            except:
                # 画像読み込みエラーの場合、代替表示
                pyxel.rect(x, y, 32, 53, 8)
                pyxel.text(x+10, y+20, f"{card.month}", 0)
                pyxel.text(x+10, y+30, f"{card.rank}", 0)
            
            # 選択時のハイライト枠
            if selected:
                pyxel.rectb(x+4, y+8, 20+4, 34+3, 8)
                pyxel.rectb(x+4, y+8, 20+4, 34+3, 8)
        else:
            # 空のスペースまたは裏向きカード
            pyxel.rect(x, y, self.card_width, self.card_height, 5)
            pyxel.rectb(x, y, self.card_width, self.card_height, 0)
    
    def draw(self):
        pyxel.cls(15)  # 白背景
        
        # タイトル
        pyxel.text(8, 8, "Hanafuda Monte Carlo", 0)
        pyxel.text(8, 18, f"Score: {self.score}", 0)
        
        # 山札の枚数表示
        pyxel.text(118, 235, f"Deck: {len(self.deck)}", 0)
        
        # 山札の描画（右上）
        if len(self.deck) > 0:
            # 山札は裏面として固定画像または単色で表示
            pyxel.rect(130, 205, 20, 25, 1)
            pyxel.rectb(130, 205, 20, 25, 0)
            pyxel.text(137, 213, "?", 7)
            
            # デバッグ：山札の先頭カード情報
            if len(self.deck) > 0:
                top_card = self.deck[-1]
                #pyxel.text(105, 50, f"Next:{top_card.month}-{top_card.rank}", 7)
        
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
            pyxel.text(40, 155, "Click to restart", 7)
        
        # OKボタン描画
        if not self.game_over:
            pyxel.rect(60, 205, 40, 20, 11)
            pyxel.rectb(60, 205, 40, 20, 0)
            pyxel.text(76, 213, "OK", 0)
        
        # 操作説明
        if not self.game_over:
            pyxel.text(8, 230, "Adjacent cards only", 0)
            pyxel.text(8, 240, "Same month pairs", 0)
            pyxel.text(8, 250, "Click OK to compact", 0)

def main():
    game = MonteCarloGame()
    pyxel.init(160, 256, title="Hanafuda Monte Carlo")
    pyxel.load("my_resource.pyxres")  # 花札リソースを読み込み
    pyxel.mouse(True)
    pyxel.run(game.update, game.draw)

if __name__ == "__main__":
    main()
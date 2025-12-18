"""
Logique du jeu Puissance 4
"""

class Connect4Game:
    def __init__(self, player1_id, player2_id):
        self.rows = 6
        self.cols = 7
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.current_player = 1
        self.winner = None
        self.game_over = False
    
    def get_board_state(self):
        """Retourne l'état actuel du plateau"""
        return {
            "board": self.board,
            "current_player": self.current_player,
            "winner": self.winner,
            "game_over": self.game_over
        }
    
    def play_move(self, column):
        """Joue un coup dans la colonne spécifiée"""
        if self.game_over:
            return False, "La partie est terminée"
        
        if column < 0 or column >= self.cols:
            return False, "Colonne invalide"
        
        # Trouve la première case libre dans la colonne
        for row in range(self.rows - 1, -1, -1):
            if self.board[row][column] == 0:
                self.board[row][column] = self.current_player
                
                # Vérifie la victoire
                if self._check_win(row, column):
                    self.winner = self.current_player
                    self.game_over = True
                    return True, f"Joueur {self.current_player} a gagné!"
                
                # Vérifie le match nul
                if self._is_board_full():
                    self.game_over = True
                    return True, "Match nul!"
                
                # Change de joueur
                self.current_player = 3 - self.current_player  # Alterne entre 1 et 2
                return True, "Coup joué"
        
        return False, "Colonne pleine"
    
    def _is_board_full(self):
        """Vérifie si le plateau est plein"""
        return all(self.board[0][col] != 0 for col in range(self.cols))
    
    def _check_win(self, row, col):
        """Vérifie si le dernier coup est gagnant"""
        player = self.board[row][col]
        
        # Directions: horizontal, vertical, diagonale /, diagonale \
        directions = [
            [(0, 1), (0, -1)],   # Horizontal
            [(1, 0), (-1, 0)],   # Vertical
            [(1, 1), (-1, -1)],  # Diagonale \
            [(1, -1), (-1, 1)]   # Diagonale /
        ]
        
        for direction_pair in directions:
            count = 1  # Compte le pion actuel
            
            # Vérifie dans les deux directions
            for dr, dc in direction_pair:
                r, c = row + dr, col + dc
                while 0 <= r < self.rows and 0 <= c < self.cols and self.board[r][c] == player:
                    count += 1
                    r += dr
                    c += dc
            
            if count >= 4:
                return True
        
        return False
    
    def get_current_player_id(self):
        """Retourne l'ID du joueur actuel"""
        return self.player1_id if self.current_player == 1 else self.player2_id
    
    def display_board(self):
        """Affiche le plateau (pour debug)"""
        symbols = {0: '.', 1: 'X', 2: 'O'}
        print("\n  " + " ".join(str(i) for i in range(self.cols)))
        for row in self.board:
            print("  " + " ".join(symbols[cell] for cell in row))
        print()
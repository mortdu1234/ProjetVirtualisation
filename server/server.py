"""
Serveur de jeu Puissance 4
"""
import socket
import threading
import json
from game import Connect4Game
from shared.protocol import Protocol


class GameServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.server_socket = None
        self.players = {}  # {player_id: {"socket": socket, "name": name, "in_game": False}}
        self.games = {}  # {game_id: Connect4Game}
        self.player_counter = 0
        self.game_counter = 0
        self.lock = threading.Lock()
    
    def start(self):
        """Démarre le serveur"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        print(f"🎮 Serveur Puissance 4 démarré sur {self.host}:{self.port}")
        
        while True:
            try:
                client_socket, address = self.server_socket.accept()
                print(f"📡 Nouvelle connexion depuis {address}")
                
                # Crée un thread pour gérer ce client
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
            except Exception as e:
                print(f"Erreur serveur: {e}")
    
    def handle_client(self, client_socket, address):
        """Gère la communication avec un client"""
        player_id = None
        
        try:
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                msg_type, msg_data = Protocol.decode(data)
                
                if msg_type == Protocol.REGISTER:
                    player_id = self.register_player(client_socket, msg_data)
                
                elif msg_type == Protocol.LIST_PLAYERS:
                    self.send_player_list(player_id)
                
                elif msg_type == Protocol.CHALLENGE:
                    self.handle_challenge(player_id, msg_data)
                
                elif msg_type == Protocol.CHALLENGE_ACCEPTED:
                    self.start_game(msg_data["challenger_id"], player_id)
                
                elif msg_type == Protocol.CHALLENGE_REFUSED:
                    self.handle_challenge_refused(msg_data["challenger_id"], player_id)
                
                elif msg_type == Protocol.PLAY_MOVE:
                    self.handle_move(player_id, msg_data)
                
                elif msg_type == Protocol.DISCONNECT:
                    break
        
        except Exception as e:
            print(f"Erreur avec le client {address}: {e}")
        
        finally:
            if player_id:
                self.disconnect_player(player_id)
            client_socket.close()
    
    def register_player(self, client_socket, data):
        """Enregistre un nouveau joueur"""
        with self.lock:
            self.player_counter += 1
            player_id = f"player_{self.player_counter}"
            player_name = data.get("name", player_id)
            
            self.players[player_id] = {
                "socket": client_socket,
                "name": player_name,
                "in_game": False
            }
            
            # Envoie la confirmation
            response = Protocol.encode(Protocol.REGISTER_OK, {"player_id": player_id})
            client_socket.send(response)
            
            print(f"✅ Joueur enregistré: {player_name} ({player_id})")
            return player_id
    
    def send_player_list(self, player_id):
        """Envoie la liste des joueurs disponibles"""
        with self.lock:
            available_players = [
                {"id": pid, "name": pdata["name"]}
                for pid, pdata in self.players.items()
                if not pdata["in_game"] and pid != player_id
            ]
            
            response = Protocol.encode(Protocol.LIST_PLAYERS, {"players": available_players})
            self.players[player_id]["socket"].send(response)
    
    def handle_challenge(self, challenger_id, data):
        """Gère une demande de défi"""
        opponent_id = data.get("opponent_id")
        
        with self.lock:
            if opponent_id in self.players and not self.players[opponent_id]["in_game"]:
                challenger_name = self.players[challenger_id]["name"]
                
                # Envoie la demande à l'adversaire
                challenge_msg = Protocol.encode(
                    Protocol.CHALLENGE_RECEIVED,
                    {"challenger_id": challenger_id, "challenger_name": challenger_name}
                )
                self.players[opponent_id]["socket"].send(challenge_msg)
            else:
                error_msg = Protocol.encode(Protocol.ERROR, {"message": "Joueur non disponible"})
                self.players[challenger_id]["socket"].send(error_msg)
    
    def handle_challenge_refused(self, challenger_id, refuser_id):
        """Gère un refus de défi"""
        with self.lock:
            if challenger_id in self.players:
                refuser_name = self.players[refuser_id]["name"]
                msg = Protocol.encode(
                    Protocol.CHALLENGE_REFUSED,
                    {"message": f"{refuser_name} a refusé le défi"}
                )
                self.players[challenger_id]["socket"].send(msg)
    
    def start_game(self, player1_id, player2_id):
        """Démarre une partie entre deux joueurs"""
        with self.lock:
            self.game_counter += 1
            game_id = f"game_{self.game_counter}"
            
            # Crée la partie
            game = Connect4Game(player1_id, player2_id)
            self.games[game_id] = game
            
            # Marque les joueurs comme en jeu
            self.players[player1_id]["in_game"] = True
            self.players[player1_id]["game_id"] = game_id
            self.players[player2_id]["in_game"] = True
            self.players[player2_id]["game_id"] = game_id
            
            # Notifie les joueurs
            game_start_msg = Protocol.encode(
                Protocol.GAME_START,
                {
                    "game_id": game_id,
                    "player1": self.players[player1_id]["name"],
                    "player2": self.players[player2_id]["name"],
                    "your_number": 1
                }
            )
            self.players[player1_id]["socket"].send(game_start_msg)
            
            game_start_msg = Protocol.encode(
                Protocol.GAME_START,
                {
                    "game_id": game_id,
                    "player1": self.players[player1_id]["name"],
                    "player2": self.players[player2_id]["name"],
                    "your_number": 2
                }
            )
            self.players[player2_id]["socket"].send(game_start_msg)
            
            print(f"🎲 Partie {game_id} démarrée: {self.players[player1_id]['name']} vs {self.players[player2_id]['name']}")
            
            # Envoie l'état initial
            self.send_game_update(game_id)
    
    def handle_move(self, player_id, data):
        """Gère un coup joué"""
        game_id = self.players[player_id].get("game_id")
        if not game_id or game_id not in self.games:
            return
        
        game = self.games[game_id]
        
        # Vérifie que c'est le tour du joueur
        if game.get_current_player_id() != player_id:
            error_msg = Protocol.encode(Protocol.ERROR, {"message": "Ce n'est pas votre tour"})
            self.players[player_id]["socket"].send(error_msg)
            return
        
        column = data.get("column")
        success, message = game.play_move(column)
        
        if success:
            self.send_game_update(game_id)
            
            if game.game_over:
                self.end_game(game_id)
        else:
            error_msg = Protocol.encode(Protocol.ERROR, {"message": message})
            self.players[player_id]["socket"].send(error_msg)
    
    def send_game_update(self, game_id):
        """Envoie l'état du jeu aux deux joueurs"""
        game = self.games[game_id]
        state = game.get_board_state()
        
        update_msg = Protocol.encode(Protocol.GAME_UPDATE, state)
        
        self.players[game.player1_id]["socket"].send(update_msg)
        self.players[game.player2_id]["socket"].send(update_msg)
    
    def end_game(self, game_id):
        """Termine une partie"""
        game = self.games[game_id]
        
        winner_name = None
        if game.winner:
            winner_id = game.player1_id if game.winner == 1 else game.player2_id
            winner_name = self.players[winner_id]["name"]
        
        game_over_msg = Protocol.encode(
            Protocol.GAME_OVER,
            {"winner": winner_name}
        )
        
        self.players[game.player1_id]["socket"].send(game_over_msg)
        self.players[game.player2_id]["socket"].send(game_over_msg)
        
        # Marque les joueurs comme disponibles
        self.players[game.player1_id]["in_game"] = False
        self.players[game.player2_id]["in_game"] = False
        del self.players[game.player1_id]["game_id"]
        del self.players[game.player2_id]["game_id"]
        
        print(f"🏁 Partie {game_id} terminée. Gagnant: {winner_name or 'Match nul'}")
    
    def disconnect_player(self, player_id):
        """Déconnecte un joueur"""
        with self.lock:
            if player_id in self.players:
                player_name = self.players[player_id]["name"]
                print(f"👋 {player_name} s'est déconnecté")
                
                # Si le joueur était en jeu, termine la partie
                if self.players[player_id]["in_game"]:
                    game_id = self.players[player_id].get("game_id")
                    if game_id and game_id in self.games:
                        game = self.games[game_id]
                        opponent_id = game.player2_id if game.player1_id == player_id else game.player1_id
                        
                        if opponent_id in self.players:
                            disconnect_msg = Protocol.encode(
                                Protocol.GAME_OVER,
                                {"winner": self.players[opponent_id]["name"], "reason": "Adversaire déconnecté"}
                            )
                            self.players[opponent_id]["socket"].send(disconnect_msg)
                            self.players[opponent_id]["in_game"] = False
                            if "game_id" in self.players[opponent_id]:
                                del self.players[opponent_id]["game_id"]
                        
                        del self.games[game_id]
                
                del self.players[player_id]

if __name__ == "__main__":
    server = GameServer(host='0.0.0.0', port=5555)
    server.start()
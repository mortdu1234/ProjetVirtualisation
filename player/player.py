"""
Client joueur pour Puissance 4
"""
import socket
import threading
import json
import sys

from shared.protocol import Protocol

class Player:
    def __init__(self, server_host='localhost', server_port=5555):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        self.player_id = None
        self.player_name = None
        self.in_game = False
        self.my_player_number = None
        self.current_board = None
        self.current_player = None
        self.pending_challenger = None
        self.running = True
    
    def connect(self, name):
        """Se connecte au serveur"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            print(f"✅ Connecté au serveur {self.server_host}:{self.server_port}")
            
            # S'enregistre
            self.player_name = name
            register_msg = Protocol.encode(Protocol.REGISTER, {"name": name})
            self.socket.send(register_msg)
            
            # Lance le thread d'écoute
            listen_thread = threading.Thread(target=self.listen_server)
            listen_thread.daemon = True
            listen_thread.start()
            
            return True
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return False
    
    def listen_server(self):
        """Écoute les messages du serveur"""
        while self.running:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break
                
                msg_type, msg_data = Protocol.decode(data)
                self.handle_server_message(msg_type, msg_data)
            
            except Exception as e:
                if self.running:
                    print(f"❌ Erreur de réception: {e}")
                break
    
    def handle_server_message(self, msg_type, msg_data):
        """Gère les messages reçus du serveur"""
        if msg_type == Protocol.REGISTER_OK:
            self.player_id = msg_data["player_id"]
            print(f"🎮 Enregistré avec l'ID: {self.player_id}")
        
        elif msg_type == Protocol.LIST_PLAYERS:
            self.display_player_list(msg_data["players"])
        
        elif msg_type == Protocol.CHALLENGE_RECEIVED:
            self.pending_challenger = msg_data
            print(f"\n🎯 {msg_data['challenger_name']} vous défie!")
            print("Tapez 'accept' pour accepter ou 'refuse' pour refuser")
        
        elif msg_type == Protocol.CHALLENGE_REFUSED:
            print(f"\n❌ {msg_data['message']}")
        
        elif msg_type == Protocol.GAME_START:
            self.in_game = True
            self.my_player_number = msg_data["your_number"]
            print(f"\n🎲 Partie démarrée!")
            print(f"   Joueur 1 (X): {msg_data['player1']}")
            print(f"   Joueur 2 (O): {msg_data['player2']}")
            print(f"   Vous êtes le joueur {self.my_player_number}")
        
        elif msg_type == Protocol.GAME_UPDATE:
            self.current_board = msg_data["board"]
            self.current_player = msg_data["current_player"]
            self.display_board()
            
            if not msg_data["game_over"]:
                if self.current_player == self.my_player_number:
                    print("🔵 C'est votre tour! Choisissez une colonne (0-6):")
                else:
                    print("⏳ En attente du coup adverse...")
        
        elif msg_type == Protocol.GAME_OVER:
            self.in_game = False
            winner = msg_data.get("winner")
            reason = msg_data.get("reason", "")
            
            if winner:
                if reason:
                    print(f"\n🏆 {winner} gagne! ({reason})")
                else:
                    print(f"\n🏆 {winner} gagne!")
            else:
                print("\n🤝 Match nul!")
            
            print("\nTapez 'list' pour voir les joueurs disponibles")
        
        elif msg_type == Protocol.ERROR:
            print(f"⚠️  {msg_data['message']}")
    
    def display_player_list(self, players):
        """Affiche la liste des joueurs"""
        print("\n👥 Joueurs disponibles:")
        if not players:
            print("   Aucun joueur disponible")
        else:
            for i, player in enumerate(players, 1):
                print(f"   {i}. {player['name']} (ID: {player['id']})")
        print("\nTapez 'challenge <numéro>' pour défier un joueur")
    
    def display_board(self):
        """Affiche le plateau de jeu"""
        symbols = {0: '·', 1: '🔴', 2: '🟡'}
        print("\n  0 1 2 3 4 5 6")
        for row in self.current_board:
            print("  " + " ".join(symbols[cell] for cell in row))
        print()
    
    def request_player_list(self):
        """Demande la liste des joueurs"""
        msg = Protocol.encode(Protocol.LIST_PLAYERS)
        self.socket.send(msg)
    
    def challenge_player(self, opponent_id):
        """Défie un joueur"""
        msg = Protocol.encode(Protocol.CHALLENGE, {"opponent_id": opponent_id})
        self.socket.send(msg)
        print(f"⏳ Défi envoyé, en attente de réponse...")
    
    def accept_challenge(self):
        """Accepte un défi"""
        if self.pending_challenger:
            msg = Protocol.encode(
                Protocol.CHALLENGE_ACCEPTED,
                {"challenger_id": self.pending_challenger["challenger_id"]}
            )
            self.socket.send(msg)
            self.pending_challenger = None
    
    def refuse_challenge(self):
        """Refuse un défi"""
        if self.pending_challenger:
            msg = Protocol.encode(
                Protocol.CHALLENGE_REFUSED,
                {"challenger_id": self.pending_challenger["challenger_id"]}
            )
            self.socket.send(msg)
            self.pending_challenger = None
            print("❌ Défi refusé")
    
    def play_move(self, column):
        """Joue un coup"""
        if not self.in_game:
            print("⚠️  Vous n'êtes pas en jeu")
            return
        
        if self.current_player != self.my_player_number:
            print("⚠️  Ce n'est pas votre tour")
            return
        
        msg = Protocol.encode(Protocol.PLAY_MOVE, {"column": column})
        self.socket.send(msg)
    
    def disconnect(self):
        """Se déconnecte du serveur"""
        self.running = False
        if self.socket:
            try:
                msg = Protocol.encode(Protocol.DISCONNECT)
                self.socket.send(msg)
                self.socket.close()
            except:
                pass
        print("👋 Déconnecté")
    
    def run(self):
        """Boucle principale du joueur"""
        print("\n" + "="*50)
        print("🎮 PUISSANCE 4 - CLIENT")
        print("="*50)
        print("\nCommandes disponibles:")
        print("  list           - Afficher les joueurs disponibles")
        print("  challenge <id> - Défier un joueur")
        print("  accept         - Accepter un défi")
        print("  refuse         - Refuser un défi")
        print("  0-6            - Jouer dans une colonne (en jeu)")
        print("  quit           - Quitter")
        print()
        
        while self.running:
            try:
                user_input = input("> ").strip().lower()
                
                if not user_input:
                    continue
                
                if user_input == "quit":
                    self.disconnect()
                    break
                
                elif user_input == "list":
                    self.request_player_list()
                
                elif user_input.startswith("challenge "):
                    opponent_id = user_input.split()[1]
                    self.challenge_player(opponent_id)
                
                elif user_input == "accept":
                    self.accept_challenge()
                
                elif user_input == "refuse":
                    self.refuse_challenge()
                
                elif user_input.isdigit():
                    column = int(user_input)
                    if 0 <= column <= 6:
                        self.play_move(column)
                    else:
                        print("⚠️  Colonne invalide (0-6)")
                
                else:
                    print("⚠️  Commande inconnue. Tapez 'help' pour l'aide")
            
            except KeyboardInterrupt:
                print("\n")
                self.disconnect()
                break
            except Exception as e:
                print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    server_host = input("Adresse du serveur [localhost]: ").strip() or "localhost"
    server_port = input("Port du serveur [5555]: ").strip() or "5555"
    player_name = input("Votre nom: ").strip() or "Joueur"
    
    player = Player(server_host, int(server_port))
    
    if player.connect(player_name):
        player.run()
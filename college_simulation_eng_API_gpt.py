import random
import os

from openai import OpenAI
from dotenv import load_dotenv
load_dotenv(dotenv_path="C:\\zzqy\\college_simulator\\.env")
import os

import time


# === BEHAVIOR TREE LOGIC FOR WEREWOLF ===
class BehaviorNode:
    def run(self, game):
        pass

class SelectorNode(BehaviorNode):
    def __init__(self, children):
        self.children = children
    def run(self, game):
        for child in self.children:
            if child.run(game):
                return True
        return False

class SequenceNode(BehaviorNode):
    def __init__(self, children):
        self.children = children
    def run(self, game):
        for child in self.children:
            if not child.run(game):
                return False
        return True

class AttackSmartest(BehaviorNode):
    def run(self, game):
        available = [i for i in game.npcs if i != game.werewolf and i not in game.eliminated_npcs]
        if not available:
            return False
        target = max(available, key=lambda x: game.npcs[x]["intelligence"])
        game.eliminated_npcs.append(target)
        print(f"\nCAMPUS ANNOUNCEMENT: {game.npcs[target]['name']} was attacked last night and taken to the hospital.")
        return True

class LeaveClue(BehaviorNode):
    def run(self, game):
        if random.random() < 0.5:
            npc = game.npcs[game.werewolf]
            print(f"\nInvestigators note that the attack occurred near {npc['name']}'s dormitory.")
            game.player["clues"] += 0.5
            return True
        return False


class CollegeWerewolfGame:

    def generate_npc_reply(self, npc, context):
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        trait = npc.get("trait", "neutral")
        suspicious = npc.get("suspicious", 0)
        friendship = npc.get("friendship", 10)

        profile = f"You are a {trait} college student"
        if suspicious >= 60:
            profile += ", who is acting very suspicious."
        elif suspicious >= 30:
            profile += ", who is mildly suspicious."
        else:
            profile += ", who appears normal."

        if friendship >= 60:
            profile += " You are close friends with the player."
        elif friendship >= 30:
            profile += " You are somewhat friendly with the player."
        else:
            profile += " You are distant and reserved toward the player."

        if context == "chat":
            topic = "Respond to a casual friendly chat."
        elif context == "events":
            topic = "Respond briefly to a question about recent strange events on campus."
        elif context == "intro":
            topic = "Introduce the college mystery in 1-2 short, engaging sentences."
        else:
            topic = "Say something appropriate."

        prompt = f"{profile} {topic} Keep your answer under 2 sentences."

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=60
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return "[AI error: " + str(e) + "]"

    def __init__(self):
        # Basic game state
        self.day = 1
        self.max_days = 7
        self.game_over = False
        self.wrong_accusations = 0  # Track wrong accusations
        
        # Player attributes
        self.player = {
            "name": "",
            "gpa": 3.0,
            "intelligence": 50,
            "stamina": 50,
            "social": 50,
            "clues": 0
        }
        
        # NPC list
        self.npcs = {}
        self.werewolf = None
        self.eliminated_npcs = []
        
    def clear_screen(self):
        """Clear the screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def print_header(self):
        """Print game header"""
        self.clear_screen()
        print("\n" + "="*60)
        print(f"  COLLEGE SIMULATOR: WEREWOLF MODE - Day {self.day}")
        print("=" * 60)
        
    def print_stats(self):
        """Print player stats"""
        print(f"\nName: {self.player['name']} | GPA: {self.player['gpa']:.2f}")
        print(f"Intelligence: {self.player['intelligence']} | Stamina: {self.player['stamina']} | Social: {self.player['social']}")
        print(f"Clues collected: {self.player['clues']} | Wrong accusations: {self.wrong_accusations}/2")
        print("-" * 60)
        
    def initialize_game(self):
        """Initialize the game"""
        self.print_header()
        print("\nWelcome to College Simulator: Werewolf Mode!")
        print("One of your classmates is secretly a werewolf, attacking students every night.")
        print("Can you maintain your grades while finding out who it is?\n")
        print(self.generate_npc_reply({
            "trait": "mysterious",
            "suspicious": 0,
            "friendship": 50,
            "name": "Narrator"
        }, "intro"))
        
        # Character creation
        self.player["name"] = input("Enter your name: ")
        
        # Generate NPCs
        self.generate_npcs()
        
        # Assign werewolf
        self.assign_werewolf()
        
        print(f"\nSetup complete! The semester begins... There are {len(self.npcs)} students in your class.")
        self.build_werewolf_behavior()
        input("\nPress Enter to continue...")
        

    def build_werewolf_behavior(self):
        """根据局势构建行为树"""
        if len(self.eliminated_npcs) < 3:
            self.werewolf_behavior = SequenceNode([
                AttackSmartest(),
                LeaveClue()
            ])
        else:
            self.werewolf_behavior = SelectorNode([
                LeaveClue(),
                AttackSmartest()
            ])

    def generate_npcs(self):
        """Generate NPCs"""
        first_names = ["Alex", "Jamie", "Morgan", "Taylor", "Jordan", "Casey", "Riley", "Avery", "Quinn", "Skyler"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
        traits = ["studious", "athletic", "artistic", "shy", "outgoing", "nerdy", "popular", "mysterious", "friendly", "competitive"]
        
        # Generate 10 NPCs
        for i in range(10):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            # Ensure unique names
            while any(npc["name"] == name for npc in self.npcs.values()):
                name = f"{random.choice(first_names)} {random.choice(last_names)}"
                
            self.npcs[i] = {
                "name": name,
                "trait": random.choice(traits),
                "intelligence": random.randint(30, 90),
                "social": random.randint(30, 90),
                "friendship": 10,
                "suspicious": random.randint(0, 30)
            }
    
    def assign_werewolf(self):
        """Randomly assign one NPC as the werewolf"""
        self.werewolf = random.choice(list(self.npcs.keys()))
        self.npcs[self.werewolf]["is_werewolf"] = True
        
        # Generate clues about the werewolf
        werewolf_traits = ["always stays up late", "avoids silver jewelry", "gets irritable during full moons", 
                          "has unusual strength", "skips class on full moon days", "has peculiar eating habits",
                          "is often heard growling", "has unusually sharp canine teeth"]
        
        self.npcs[self.werewolf]["clue"] = random.choice(werewolf_traits)
    
    def main_menu(self):
        """Main menu"""
        self.print_header()
        self.print_stats()
        
        # Display current NPCs
        print("\nCurrent classmates:")
        for npc_id, npc in self.npcs.items():
            if npc_id not in self.eliminated_npcs:
                print(f"- {npc['name']} ({npc['trait']})")
        
        # If any students have been eliminated, show them
        if self.eliminated_npcs:
            print("\nEliminated students:")
            for npc_id in self.eliminated_npcs:
                print(f"- {self.npcs[npc_id]['name']}")
        
        print("\nWhat would you like to do?")
        print("1. Attend class (GPA+, Intelligence+, Stamina-)")
        print("2. Study (Intelligence+, Stamina-)")
        print("3. Socialize (Social+, Stamina-)")
        print("4. Investigate (Clues+, Stamina-)")
        print("5. Rest (Stamina+)")
        print("6. View classmate information")
        print("7. Accuse someone of being the werewolf")
        print("0. Quit game")
        
        choice = input("\nEnter your choice: ")
        self.process_choice(choice)
    
    def process_choice(self, choice):
        """Process player choice"""
        
        if choice == "0":
            self.end_game("player_quit")
            return
            
        elif choice == "1":
            self.attend_class()
        elif choice == "2":
            self.study()
        elif choice == "3":
            self.socialize()
        elif choice == "4":
            self.investigate()
        elif choice == "5":
            self.rest()
        elif choice == "6":
            self.view_npcs()
            return
        elif choice == "7":
            self.accuse_werewolf()
            return
        else:
            print("\nInvalid choice, please try again.")
            time.sleep(1)
            return
            
        # Werewolf attacks at the end of each day
        self.end_day()
    
    def attend_class(self):
        """Attend class"""
        self.print_header()
        
        # Effects
        intelligence_gain = random.randint(3, 7)
        stamina_loss = random.randint(10, 15)
        gpa_increase = 0.1
        
        self.player["intelligence"] = min(100, self.player["intelligence"] + intelligence_gain)
        self.player["stamina"] = max(0, self.player["stamina"] - stamina_loss)
        self.player["gpa"] = min(4.0, self.player["gpa"] + gpa_increase)
        
        print(f"\nYou attend class attentively and answer questions.")
        print(f"Intelligence: +{intelligence_gain}, GPA: +{gpa_increase:.2f}")
        print(f"Stamina: -{stamina_loss}")
        
        # Random NPC encounter
        self.random_npc_encounter()
        
        input("\nPress Enter to continue...")
    
    def study(self):
        """Study"""
        self.print_header()
        
        # Effects
        intelligence_gain = random.randint(5, 10)
        stamina_loss = random.randint(15, 20)
        
        self.player["intelligence"] = min(100, self.player["intelligence"] + intelligence_gain)
        self.player["stamina"] = max(0, self.player["stamina"] - stamina_loss)
        
        print(f"\nYou spend time studying in the library.")
        print(f"Intelligence: +{intelligence_gain}")
        print(f"Stamina: -{stamina_loss}")
        
        input("\nPress Enter to continue...")
    
    def socialize(self):
        """Socialize"""
        self.print_header()
        
        # Effects
        social_gain = random.randint(10, 15)
        stamina_loss = random.randint(5, 10)
        
        self.player["social"] = min(100, self.player["social"] + social_gain)
        self.player["stamina"] = max(0, self.player["stamina"] - stamina_loss)
        
        print(f"\nYou chat with classmates and make friends.")
        print(f"Social: +{social_gain}")
        print(f"Stamina: -{stamina_loss}")
        
        # Multiple NPC interactions
        for _ in range(2):
            self.random_npc_encounter()
        
        input("\nPress Enter to continue...")
    
    def investigate(self):
        """Investigate"""
        self.print_header()
        
        # Effects
        stamina_loss = random.randint(15, 25)
        self.player["stamina"] = max(0, self.player["stamina"] - stamina_loss)
        
        print(f"\nYou spend time investigating suspicious activities on campus.")
        print(f"Stamina: -{stamina_loss}")
        
        # Chance to discover clues
        if random.random() < 0.7:  # 70% chance
            self.discover_clue()
        else:
            print("You didn't find any conclusive evidence.")
            
        input("\nPress Enter to continue...")
    
    def rest(self):
        """Rest"""
        self.print_header()
        
        # Effects
        stamina_gain = random.randint(30, 50)
        self.player["stamina"] = min(100, self.player["stamina"] + stamina_gain)
        
        print(f"\nYou take time to rest and recover your energy.")
        print(f"Stamina: +{stamina_gain}")
        
        input("\nPress Enter to continue...")
    
    def discover_clue(self):
        """Discover clues about the werewolf"""
        werewolf_npc = self.npcs[self.werewolf]
        
        # Different types of clues
        clue_types = [
            f"You notice that {werewolf_npc['name']} {werewolf_npc['clue']}.",
            f"A student mentions seeing {werewolf_npc['name']} acting strangely during the last full moon.",
            f"You find a note about {werewolf_npc['name']}'s unusual behavior in the library.",
            f"You overhear that {werewolf_npc['name']} has been asking about your investigation.",
        ]
        
        # Select a random clue
        clue = random.choice(clue_types)
        print(f"\n🔍 CLUE DISCOVERED: {clue}")
        
        # Increase clue count
        self.player["clues"] += 1
        
        # If player has enough clues, they can confirm the werewolf's identity
        if self.player["clues"] >= 3:
            print(f"\n🔍 With this clue, you're now confident about the werewolf's identity!")
            print(f"You're certain that {werewolf_npc['name']} is the werewolf.")
    
    def random_npc_encounter(self):
        """Random encounter with an NPC"""
        # Only consider NPCs that haven't been eliminated
        available_npcs = [npc_id for npc_id in self.npcs if npc_id not in self.eliminated_npcs]
        if not available_npcs:
            return
            
        npc_id = random.choice(available_npcs)
        npc = self.npcs[npc_id]
        
        print(f"\nYou encounter {npc['name']} ({npc['trait']}).")
        
        # Interaction options
        print("\nHow would you like to interact?")
        print("1. Friendly chat")
        print("2. Ask about recent events")
        print("3. Ignore them")
        
        choice = input("\nChoose an option: ")
        print(self.generate_npc_reply(npc, 'chat') if choice == '1' else self.generate_npc_reply(npc, 'events') if choice == '2' else '')
        
        if choice == "1":
            # Friendly chat
            friendship_gain = random.randint(5, 10)
            npc["friendship"] += friendship_gain
            social_gain = random.randint(2, 5)
            self.player["social"] = min(100, self.player["social"] + social_gain)
            
            print(f"You have a pleasant conversation with {npc['name']}.")
            print(f"Friendship: +{friendship_gain}, Social: +{social_gain}")
            
        elif choice == "2":
            # Ask about events
            print(f"You ask {npc['name']} about the recent strange incidents.")
            
            # If they're the werewolf
            if npc_id == self.werewolf:
                if random.random() < 0.3:  # 30% chance
                    print(f"\n{npc['name']} seems unusually defensive and quickly changes the subject.")
                    
                    # Increase suspicion for this NPC
                    npc["suspicious"] += 20
                    
                    if npc["suspicious"] >= 50:
                        self.player["clues"] += 1
                        print(f"You notice something suspicious... Clue +1")
            else:
                # Might provide a clue about the real werewolf
                if random.random() < 0.3:  # 30% chance
                    werewolf_npc = self.npcs[self.werewolf]
                    print(f"\n{npc['name']} mentions seeing {werewolf_npc['name']} acting strangely recently.")
                    self.player["clues"] += 0.5
                    print("This might be a useful lead.")
        
        elif choice == "3":
            # Ignore them
            print(f"You ignore {npc['name']} and continue with your business.")
    

    def werewolf_attack(self):
        """狼人攻击行为由行为树控制"""
        self.print_header()
        print("\n🐺 WEREWOLF ATTACK 🐺")
        if hasattr(self, "werewolf_behavior"):
            self.werewolf_behavior.run(self)
        else:
            print("The werewolf hesitates and does nothing...")
        input("\nPress Enter to continue...")
        """Werewolf attacks an NPC"""
        self.print_header()
        print("\n🐺 WEREWOLF ATTACK 🐺")
        
        # Exclude already eliminated NPCs
        available_targets = [npc_id for npc_id in self.npcs if npc_id != self.werewolf and npc_id not in self.eliminated_npcs]
        
        if not available_targets:
            print("\nThere are no more targets left!")
            return
            
        # Choose a target (preferring high intelligence or low social students)
        if random.random() < 0.7:  # 70% chance to target high intelligence student
            target = max(available_targets, key=lambda x: self.npcs[x]["intelligence"])
        else:
            target = min(available_targets, key=lambda x: self.npcs[x]["social"])
            
        target_npc = self.npcs[target]
        
        print(f"\nCAMPUS ANNOUNCEMENT: {target_npc['name']} was attacked last night and has been taken to the hospital.")
        print("The administration reminds all students to stay vigilant and avoid going out alone at night.")
        
        # Add target to eliminated list
        self.eliminated_npcs.append(target)
        
        # Each attack leaves some clues
        if random.random() < 0.5:  # 50% chance
            werewolf_npc = self.npcs[self.werewolf]
            print(f"\nInvestigators note that the attack occurred near {werewolf_npc['name']}'s dormitory.")
            self.player["clues"] += 0.5
        
        input("\nPress Enter to continue...")
    
    def accuse_werewolf(self):
        """Accuse someone of being the werewolf"""
        self.print_header()
        
        print("\n" + "-"*20 + " ACCUSE WEREWOLF " + "-"*20)
        print("You decide to reveal who you think the werewolf is. This is a serious decision with potentially severe consequences.")
        
        # Warning messages
        if self.player["clues"] < 1:
            print("\n⚠️ WARNING: You have almost no clues, this accusation could be very dangerous!")
        elif self.player["clues"] < 2:
            print("\n⚠️ WARNING: You have few clues, this accusation is risky!")
        
        # Extra warning if already had one wrong accusation
        if self.wrong_accusations == 1:
            print("\n⚠️ SEVERE WARNING: You've already made one false accusation. A second will end the game!")
        
        print("\nChoose who you think is the werewolf from your remaining classmates:")
        
        # Show all non-eliminated NPCs
        available_npcs = [npc_id for npc_id in self.npcs if npc_id not in self.eliminated_npcs]
        for i, npc_id in enumerate(available_npcs, 1):
            npc = self.npcs[npc_id]
            suspicious_level = "Normal"
            if npc["suspicious"] >= 30:
                suspicious_level = "Somewhat Suspicious"
            if npc["suspicious"] >= 60:
                suspicious_level = "Very Suspicious"
            print(f"{i}. {npc['name']} ({npc['trait']}) - Suspicion: {suspicious_level}")
            
        print("0. Cancel and return")
        
        choice = input("\nEnter your choice (number): ")
        
        try:
            choice_num = int(choice)
            if choice_num == 0:
                return
            
            if choice_num < 1 or choice_num > len(available_npcs):
                print("\nInvalid choice, please try again.")
                time.sleep(1)
                return
                
            accused_npc_id = available_npcs[choice_num - 1]
            self.process_accusation(accused_npc_id)
                
        except ValueError:
            print("\nPlease enter a valid number.")
            time.sleep(1)
            return
    
    def process_accusation(self, accused_npc_id):
        """Process player's accusation"""
        accused_npc = self.npcs[accused_npc_id]
        
        self.print_header()
        print("\n" + "-"*20 + " ACCUSATION RESULT " + "-"*20)
        print(f"You publicly accuse {accused_npc['name']} of being the campus werewolf.")
        
        # Correct accusation
        if accused_npc_id == self.werewolf:
            print("\n🎉 Your accusation is correct!")
            print(f"{accused_npc['name']} is revealed as the werewolf and captured.")
            print("You've successfully saved the campus and become a hero!")
            input("\nPress Enter to continue...")
            self.end_game("correct_accusation")
            return
        
        # Wrong accusation
        print("\n❌ Your accusation is wrong!")
        print(f"{accused_npc['name']} is clearly shocked and confused by your accusation.")
        
        # Increase wrong accusation count
        self.wrong_accusations += 1
        
        # Second wrong accusation immediately ends the game
        if self.wrong_accusations >= 2:
            print("\nThis is your second false accusation. The administration believes you're causing panic and decides to take disciplinary action.")
            input("\nPress Enter to continue...")
            self.end_game("two_false_accusations")
            return
        
        # First wrong accusation severely decreases attributes
        social_loss = random.randint(30, 50)
        gpa_loss = 1.0
        intelligence_loss = random.randint(10, 20)
        
        self.player["social"] = max(0, self.player["social"] - social_loss)
        self.player["gpa"] = max(0.0, self.player["gpa"] - gpa_loss)
        self.player["intelligence"] = max(0, self.player["intelligence"] - intelligence_loss)
        
        print("\n⚠️ This is your first false accusation! The administration warns you not to spread false allegations.")
        print("Your classmates begin to doubt your judgment, and some think you're maliciously targeting others.")
        print("Your academic standing and social status have been severely impacted.")
        
        print(f"\nSocial: -{social_loss}")
        print(f"GPA: -{gpa_loss:.2f}")
        print(f"Intelligence: -{intelligence_loss}")
        
        # Wait for player to acknowledge this information
        input("\nPress Enter to continue...")
        
        # Then proceed with werewolf attack
        print("\nMeanwhile, the real werewolf takes advantage of the chaos to attack again...")
        self.werewolf_attack()
    
    def view_npcs(self):
        """View all NPCs and relationships"""
        self.print_header()
        print("\n" + "-"*20 + " CLASSMATES " + "-"*20)
        
        for npc_id, npc in self.npcs.items():
            if npc_id in self.eliminated_npcs:
                continue  # Skip eliminated NPCs
                
            friendship_level = "Acquaintance"
            if npc["friendship"] >= 30:
                friendship_level = "Friend"
            if npc["friendship"] >= 60:
                friendship_level = "Close Friend"
                
            suspicious_level = "Normal"
            if npc["suspicious"] >= 30:
                suspicious_level = "Somewhat Suspicious"
            if npc["suspicious"] >= 60:
                suspicious_level = "Very Suspicious"
                
            print(f"\n{npc['name']} ({npc['trait']})")
            print(f"Friendship: {npc['friendship']} ({friendship_level})")
            print(f"Suspicion level: {suspicious_level}")
            
            # If player has enough clues, they might identify the werewolf
            if self.player["clues"] >= 3 and npc_id == self.werewolf and npc["suspicious"] >= 50:
                print("❗ You strongly suspect this person is the werewolf.")
                
        print("\n" + "-"*50)
        input("\nPress Enter to return to the main menu...")
    
    def end_day(self):
        """End the current day"""
        # Werewolf attack
        self.werewolf_attack()
        
        # Increase day count
        self.day += 1
        
        # Slightly recover stamina
        self.player["stamina"] = min(100, self.player["stamina"] + 10)
        
        # Check if game should end
        if self.day > self.max_days:
            self.end_game("time_up")
        elif len(self.eliminated_npcs) >= len(self.npcs) - 2:  # Only player and werewolf left
            self.end_game("too_many_victims")
        elif self.player["clues"] >= 3 and random.random() < 0.3:  # Enough clues and 30% chance
            self.end_game("player_identifies_werewolf")
        elif self.player["stamina"] <= 0:
            self.end_game("exhaustion")
    
    def end_game(self, reason):
        """End the game and show results"""
        self.game_over = True
        self.print_header()
        
        print("\n" + "="*20 + " GAME OVER " + "="*20)
        
        # Determine ending based on reason
        if reason == "player_quit":
            print("\nYou chose to quit the game.")
            
        elif reason == "time_up":
            print(f"\nYou survived {self.day} days at Werewolf University!")
            
            # Ending based on clue count
            if self.player["clues"] >= 3:
                print("\n🏆 You successfully identified the werewolf but haven't taken action yet.")
                print("You need more evidence to expose the truth.")
            else:
                print("\n⚠️ The semester has ended, and you failed to identify the werewolf.")
                print("The werewolf continues to lurk on campus...")
                
        elif reason == "too_many_victims":
            print("\n⚠️ Too many students have been eliminated! The administration decides to temporarily close the school.")
            print("The werewolf's identity remains a mystery...")
            
        elif reason == "player_identifies_werewolf" or reason == "correct_accusation":
            werewolf_npc = self.npcs[self.werewolf]
            print(f"\n🏆 With the evidence you've gathered, you successfully expose {werewolf_npc['name']} as the werewolf!")
            print("The administration takes immediate action, and the werewolf is captured. You're a campus hero!")
            
        elif reason == "false_accusation":
            print("\n❌ You falsely accused an innocent classmate, while the real werewolf remains at large.")
            print("Your reputation is severely damaged, and this incident will follow you even after the semester ends.")
            
        elif reason == "two_false_accusations":
            print("\n💥 You've made two false werewolf accusations!")
            print("The administration believes you're spreading panic and disrupting campus order.")
            print("You're suspended from school, while the real werewolf continues to lurk.")
            
        elif reason == "exhaustion":
            print("\n💤 You're completely exhausted and need to take a medical leave to recover.")
            print("While you're away, the werewolf continues hunting...")
        
        # Reveal the werewolf
        werewolf_npc = self.npcs[self.werewolf]
        print(f"\nThe werewolf was: {werewolf_npc['name']} ({werewolf_npc['trait']})")
        
        # Show final stats
        print("\n" + "-"*20 + " FINAL STATS " + "-"*20)
        print(f"Name: {self.player['name']} | GPA: {self.player['gpa']:.2f}")
        print(f"Intelligence: {self.player['intelligence']} | Stamina: {self.player['stamina']} | Social: {self.player['social']}")
        print(f"Clues collected: {self.player['clues']}")
        
        print("\nThank you for playing College Simulator: Werewolf Mode!")
        print("=" * 50)
        
        input("\nPress Enter to exit...")
        exit()
    
    def run(self):
        """Run the main game loop"""
        self.initialize_game()
        
        while not self.game_over:
            self.main_menu()

# Game entry point
if __name__ == "__main__":
    game = CollegeWerewolfGame()
    game.run()
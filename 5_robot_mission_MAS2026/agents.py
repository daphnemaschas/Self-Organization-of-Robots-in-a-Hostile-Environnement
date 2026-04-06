"""
Group 5
Date: 2026-03-16
Members: Maxence Rossignol, Antoine Yezou, Daphné Maschas

This module defines the robot agents with communication capabilities (Step 2).
"""

import mesa
import random
from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.Message import Message
from communication.message.MessagePerformative import MessagePerformative


class RobotAgent(CommunicatingAgent):
    """Base class for all robot agents."""

    def __init__(self, model, name):
        super().__init__(model, name)
        self.knowledge = {
            'inventory': [],
            'last_percepts': {},
            'single_waste_steps':0,
            'waiting_for_response': False,
            'state': 'WANDERING'
        }
        self.n_steps = 10
    
    def handle_messages(self):
        messages = self.get_new_messages()
        
        for msg in messages:
            perf = msg.get_performative()
            
            if perf == MessagePerformative.CFP:
                self._handle_cfp(msg)
            elif perf == MessagePerformative.PROPOSE:
                self._handle_propose(msg)
            elif perf == MessagePerformative.ACCEPT_PROPOSAL:
                self._handle_accept(msg)
            elif perf == MessagePerformative.INFORM:
                self._handle_inform(msg)

    def _handle_cfp(self, msg):
        self.knowledge['received_cfp'] = True
        self.knowledge['initiator_id'] = msg.get_exp()
        
        content = msg.get_content()
        if isinstance(content, dict) and 'pos' in content:
            self.knowledge['target_pos'] = content['pos']

    def _handle_propose(self, msg):
        self.knowledge['received_propose'] = True
        self.knowledge['participant_id'] = msg.get_exp()

    def _handle_accept(self, msg):
        """Gère la confirmation que notre proposition a été acceptée"""
        self.knowledge['received_accept'] = True

    def _handle_inform(self, msg):
        """Gère la confirmation que l'action est terminée (le déchet a été déposé)"""
        self.knowledge['received_inform'] = True

    def step(self):
        self.step_agent()

    def step_agent(self):
        # 1. Get percepts
        percepts = self.model.do(self, None)
        self.knowledge['last_percepts'] = percepts
        
        # 2. Deliberate
        action = self.deliberate(self.knowledge)
        
        # 3. Act and update
        new_percepts = self.model.do(self, action)
        self.knowledge['last_percepts'] = new_percepts

    def deliberate(self, knowledge):
        raise NotImplementedError

    def get_pos_id(self, percepts, pos, obj_type, detail=None):
        """Helper to find an object's ID in percepts."""
        contents = percepts.get(pos, [])
        found_id = None
        is_correct_type = False
        
        # Percepts are formatted as ["type_Waste", "id_10", "waste_green", ...]
        # We need to find the ID that follows the correct type and detail
        for i, item in enumerate(contents):
            if f"type_{obj_type}" == item:
                # Look ahead for ID
                if i + 1 < len(contents) and contents[i+1].startswith("id_"):
                    potential_id = int(contents[i+1].split("_")[1])
                    # Check detail if provided
                    if detail:
                        if detail in contents:
                            return potential_id
                    else:
                        return potential_id
        return None

class GreenAgent(RobotAgent):
    def __init__(self, model, name):
        super().__init__(model, name)
        self.color = "green"

    def deliberate(self, knowledge):
        total_wastes = self.model.count_waste_on_field(self.model)
        percepts = knowledge['last_percepts']
        inventory = knowledge['inventory']
        state = self.knowledge.get('state', 'WANDERING')

        # Usual research mode
        if state == "WANDERING":
            
            # Update single waste steps
            green_wastes = [w for w in inventory if w.waste_type == "green"]
            if len(green_wastes) == 1:
                self.knowledge['single_waste_steps'] += 1
            else:
                self.knowledge['single_waste_steps'] = 0
            
            # 0. If there is no wastes on the field and it has 1 waste -> calls red
            if total_wastes == 0 and len(green_wastes) == 1:
                print(f'[{self.get_name()}] Hey Red ! I need help') # DEBUG
                self.knowledge['state'] = "WAITING_FOR_RED"
                return ("send_message", MessagePerformative.CFP, "red")
            
            # 0. If single_waste_steps >= n_steps
            if self.knowledge['single_waste_steps'] >= self.n_steps:
                self.knowledge['state'] = "READING_MAILBOX"
                return ("read_messages",)
    
            # 1. If 2 green -> Transform
            if len([w for w in inventory if w.waste_type == "green"]) >= 2:
                return ("transform",)

            # 2. If 1 yellow -> Move to EASTERNMOST border of Z1 and Drop
            yellow_wastes = [w for w in inventory if w.waste_type == "yellow"]
            if yellow_wastes:
                z1_end = self.model.width // 3
                target_x = z1_end - 1
                if self.pos[0] < target_x:
                    # Move East
                    return ("move", (self.pos[0] + 1, self.pos[1]))
                elif self.pos[0] == target_x:
                    # self.model.do(self, ("post_message", {"type": "waste_ready", "waste": "yellow", "pos": self.pos}))
                    return ("drop",)
                else:
                    # Should not happen for GreenAgent, but move West if it does
                    return ("move", (self.pos[0] - 1, self.pos[1]))
            
            if self.knowledge.get('ignore_waste_ticks', 0) > 0:
                self.knowledge['ignore_waste_ticks'] -= 1
                neighbors = [p for p in percepts.keys() if p[0] < (self.model.width // 3)]
                if neighbors: return ("move", random.choice(neighbors))
                return ("move", self.pos)

            # 3. If green waste here -> Pick up
            green_id = self.get_pos_id(percepts, self.pos, "Waste", "waste_green")
            if green_id is not None and len(inventory) < 2:
                return ("pick_up", green_id)

            # 4. Search green waste in percepts
            for pos, contents in percepts.items():
                if "waste_green" in contents:
                    return ("move", pos)
            
            # 5. Patrol/Search within Z1 if needs more green waste
            if len(inventory) < 2:
                for pos, contents in percepts.items():
                    if "waste_green" in contents:
                        return ("move", pos)
                # Stay in Z1
                neighbors = [p for p in percepts.keys() if p[0] < (self.model.width // 3)]
                if neighbors: return ("move", random.choice(neighbors))

        # Other states: communication, waiting,...
        elif state == "WAITING_FOR_RED":
            if self.knowledge.get('received_propose', False):
                # A red agent answered his cry for help, accept his proposal
                print(f'[{self.get_name()}] Please red agent come I am waiting for you !') # DEBUG
                self.knowledge['state'] = "WAITING_INFORM"
                self.knowledge['received_propose'] = False
                return ("send_message", MessagePerformative.ACCEPT_PROPOSAL)
            else:
                # Wait until someone answers
                return ("read_messages",)

        elif state == "READING_MAILBOX":
            if self.knowledge.get('received_cfp'):
                # Received a message from someone asking for help, answers saying he'll come
                print(f'[{self.get_name()}] I can help you !') # DEBUG
                self.knowledge['state'] = "WAITING_CONFIRM"
                self.knowledge['received_cfp'] = False
                return ("send_message", MessagePerformative.PROPOSE)
            else:
                # No one asked for help, he sends a message saying he needs help
                print(f'[{self.get_name()}] Hey ! I need help') # DEBUG
                self.knowledge['state'] = "WAITING_ACCEPT"
                return ("send_message", MessagePerformative.CFP, "green")
        
        elif state == "WAITING_ACCEPT":
            if self.knowledge.get('received_propose'):
                # Someone answered his cry for help, accept his proposal
                print(f'[{self.get_name()}] Please come I am waiting for you !')
                self.knowledge['state'] = "WAITING_INFORM"
                self.knowledge['received_propose'] = False
                return ("send_message", MessagePerformative.ACCEPT_PROPOSAL)
            elif self.knowledge.get('received_cfp'):
                # Résolution de conflit (Deadlock) : un autre agent a demandé de l'aide en même temps
                if self.get_name() < self.knowledge.get('initiator_id', ''):
                    print(f'[{self.get_name()}] I abandon my request to help you instead !')
                    self.knowledge['state'] = "WAITING_CONFIRM"
                    self.knowledge['received_cfp'] = False
                    return ("send_message", MessagePerformative.PROPOSE)
            else:
                # Wait until someone answers
                return ("read_messages",)
        
        elif state == "WAITING_CONFIRM":
            if self.knowledge.get('received_accept'):
                # His proposal was accepted, he now moves towards the target posiion
                print(f'[{self.get_name()}] I read your acceptation, I am on my way to {self.knowledge.get('target_pos')}!') # DEBUG
                self.knowledge['state'] = "MOVING_TO_ROBOT"
                self.knowledge['received_accept'] = False
                return ("move", self.knowledge.get('target_pos', self.pos)) # TODO ?
            else:
                return ("read_messages", self.pos)
            
        elif state == "MOVING_TO_ROBOT":
            if self.pos == self.knowledge.get('target_pos'):
                print(f'[{self.get_name()}] I have arrived !') # DEBUG
                self.knowledge['state'] = "SENDING_INFORM"
                self.knowledge['single_waste_steps'] = 0 
                return ("drop",)
            else:
                print(f'[{self.get_name()}] I am coming to {self.knowledge['target_pos']} !') # DEBUG
                return ("move", self.knowledge['target_pos']) 
        
        elif state == "SENDING_INFORM":
            # Informs the initiator that the waste is here
            print(f'[{self.get_name()}] I inform you that I have arrived !') # DEBUG
            self.knowledge['state'] = "FLEEING" 
            self.knowledge['single_waste_steps'] = 0 
            return ("send_message", MessagePerformative.INFORM)
        
        elif state == "FLEEING":
            # Message has been sent now he flees
            print(f'[{self.get_name()}] Now I am going elsewhere !') # DEBUG
            self.knowledge['state'] = "WANDERING"
            self.knowledge['ignore_waste_ticks'] = 3
            neighbors = [p for p in percepts.keys() if p != self.pos and p[0] < (self.model.width // 3)]
            if neighbors:
                return ("move", random.choice(neighbors))
            return ("move", self.pos)

        elif state == "WAITING_INFORM":
            if self.knowledge.get('received_inform'):
                # The initiator knows that the waste is here
                participant_id = self.knowledge.get('participant_id', '')
                print(f'[{self.get_name()}] I acknowledge that you are here {participant_id}!') # DEBUG
                
                self.knowledge['single_waste_steps'] = 0
                self.knowledge['received_inform'] = False
                
                if "Red" in participant_id:
                    print(f'[{self.get_name()}] Red help ({participant_id}) is here ! I drop my waste and flee.') # DEBUG
                    self.knowledge['state'] = "FLEEING"
                    return ("drop",)
                else:
                    print(f'[{self.get_name()}] Green help ({participant_id}) is here ! Got it!') # DEBUG
                    self.knowledge['state'] = "WANDERING"
                    return ("move", self.pos)
            else:
                return ("read_messages",)
        
        return ("move", self.pos)

class YellowAgent(RobotAgent):
    def __init__(self, model, name, patrol=False):
        super().__init__(model, name)
        self.patrol = patrol
        self.color = "yellow"

    def deliberate(self, knowledge):
        total_wastes = self.model.count_waste_on_field(self.model)
        percepts = knowledge['last_percepts']
        inventory = knowledge['inventory']
        z1_end = self.model.width // 3
        z2_end = 2 * (self.model.width // 3)

        # Count single waste steps
        yellow_wastes = [w for w in inventory if w.waste_type == "yellow"]
        if len(yellow_wastes) == 1:
            self.knowledge['single_waste_steps'] += 1
        else:
            self.knowledge['single_waste_steps'] = 0
        
        # 1. Transformation
        if len([w for w in inventory if w.waste_type == "yellow"]) >= 2:
            return ("transform",)

        # 2. Delivery: Move to EASTERNMOST border of Z2 and Drop
        red_wastes = [w for w in inventory if w.waste_type == "red"]
        if red_wastes:
            target_x = z2_end - 1
            if self.pos[0] < target_x:
                return ("move", (self.pos[0] + 1, self.pos[1]))
            elif self.pos[0] == target_x:
                # self.model.do(self, ("post_message", {"type": "waste_ready", "waste": "red", "pos": self.pos}))
                return ("drop",)
            else:
                return ("move", (self.pos[0] - 1, self.pos[1]))

        # 3. Collection: If yellow waste here
        yellow_id = self.get_pos_id(percepts, self.pos, "Waste", "waste_yellow")
        if yellow_id is not None and len(inventory) < 2:
            return ("pick_up", yellow_id)

        # 4. Search for nearby waste in percepts
        for pos, contents in percepts.items():
            if "waste_yellow" in contents:
                return ("move", pos)

        # 5. Patrol Z1/Z2 border if waiting for more yellow waste if it is a patrolling agent
        if not red_wastes and len(inventory) < 2 and self.patrol:
            target_x = z1_end # First column of Z2
            if self.pos[0] > target_x:
                return ("move", (self.pos[0] - 1, self.pos[1]))
            elif self.pos[0] < target_x:
                return ("move", (self.pos[0] + 1, self.pos[1]))
            else:
                # Patrol vertically along the border
                adj_y = [p for p in percepts.keys() if p[0] == target_x and p != self.pos]
                if adj_y: return ("move", random.choice(adj_y))

        # 6. Default: Random exploration within Z2
        neighbors = [p for p in percepts.keys() if z1_end <= p[0] < z2_end]
        if neighbors: return ("move", random.choice(neighbors))
        return ("move", self.pos)

class RedAgent(RobotAgent):
    def __init__(self,model, name, patrol=False):
        super().__init__(model, name)
        self.patrol = patrol
        self.color = "red"
    
    def deliberate(self, knowledge):
        total_wastes = self.model.count_waste_on_field(self.model)
        percepts = knowledge['last_percepts']
        inventory = knowledge['inventory']
        z2_end = 2 * (self.model.width // 3)

        state = knowledge.get('state', 'WANDERING')

        if state == "WANDERING":
            # 0. If there is no wastes left
            if total_wastes == 0 and not inventory:
                self.knowledge['state'] = "READING_MAILBOX"
                return ("read_messages",)

            # 1. Disposal Logic
            wastes = [w for w in inventory]
            if wastes:
                # Check if disposal zone is in percepts (Highest priority)
                for pos, contents in percepts.items():
                    if "type_WasteDisposalZone" in contents:
                        if self.pos == pos: 
                            knowledge['disposal_phase'] = "down" # Reset for next time
                            return ("drop",)
                        return ("move", pos)
                
                # Step-by-step search pattern
                target_x = self.model.width - 1
                # A. Go to eastern border
                if self.pos[0] < target_x:
                    return ("move", (self.pos[0] + 1, self.pos[1]))
                
                # B. Now at eastern border, perform vertical search
                phase = knowledge.get('disposal_phase', "down")
                if phase == "down":
                    if self.pos[1] > 0:
                        return ("move", (self.pos[0], self.pos[1] - 1))
                    else:
                        knowledge['disposal_phase'] = "up"
                        return ("move", (self.pos[0], self.pos[1] + 1))
                else: # phase == "up"
                    if self.pos[1] < self.model.height - 1:
                        return ("move", (self.pos[0], self.pos[1] + 1))
                    else:
                        knowledge['disposal_phase'] = "down"
                        return ("move", (self.pos[0], self.pos[1] - 1))

            # 2. Collection: If red waste here
            red_id = self.get_pos_id(percepts, self.pos, "Waste", "waste_red")
            if red_id is not None and not red_wastes:
                return ("pick_up", red_id)

            # 3. Search for nearby waste in percepts
            for pos, contents in percepts.items():
                if "waste_red" in contents:
                    return ("move", pos)

            # 4. Patrol Z2/Z3 border (Waiting for Yellow robots) if is needs to patrol
            if not inventory and self.patrol:
                target_x = z2_end # First column of Z3
                if self.pos[0] > target_x:
                    return ("move", (self.pos[0] - 1, self.pos[1]))
                elif self.pos[0] < target_x:
                    return ("move", (self.pos[0] + 1, self.pos[1]))
                else:
                    adj_y = [p for p in percepts.keys() if p[0] == target_x and p != self.pos]
                    if adj_y: return ("move", random.choice(adj_y))

            # 5. Default: Random exploration within Z3
            neighbors = [p for p in percepts.keys() if p[0] >= z2_end]
            if neighbors: return ("move", random.choice(neighbors))
            
            return ("move", self.pos)
    
        elif state == "READING_MAILBOX":
            if self.knowledge.get('received_cfp'):
                print(f'[{self.get_name()}] I can help you !') 
                self.knowledge['state'] = "WAITING_CONFIRM"
                self.knowledge['received_cfp'] = False
                return ("send_message", MessagePerformative.PROPOSE)
            else:
                return ("read_messages",)
        
        elif state == "WAITING_CONFIRM":
            if self.knowledge.get('received_accept'):
                # His proposal was accepted, he now moves towards the target posiion
                print(f'[{self.get_name()}] I read your acceptation, I am on my way to {self.knowledge.get('target_pos')}!') # DEBUG
                self.knowledge['state'] = "MOVING_TO_ROBOT"
                self.knowledge['received_accept'] = False
                return ("move", self.knowledge.get('target_pos', self.pos)) # TODO ?
            else:
                return ("read_messages", self.pos)
        
        elif state == "MOVING_TO_ROBOT":
            target = self.knowledge.get('target_pos')
            if self.pos == target:
                print(f'[{self.get_name()}] I am here!')
                self.knowledge['state'] = "SENDING_INFORM"
                return ("move", self.pos)
            else:
                print(f'[{self.get_name()}] I am coming towards {target}!')
                return ("move", target)
                
        elif state == "SENDING_INFORM":
            print(f'[{self.get_name()}] I have arrived!')
            self.knowledge['state'] = "WAITING_GREEN"
            return ("send_message", MessagePerformative.INFORM)
        
        elif state == "WAITING_GREEN":
            # 2b. Collection: If green waste here
            green_id = self.get_pos_id(percepts, self.pos, "Waste", "waste_green")
            print(f'[{self.get_name()}] I am picking up {green_id}')
            if green_id is not None:
                self.knowledge['state'] = "WANDERING"
                return ("pick_up", green_id)
            return ("move", self.pos)
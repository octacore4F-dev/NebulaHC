from tools import  *
from objects import *
from routines import *

#This file is for strategy

class main(GoslingAgent):

    def run(agent):
       #Precomputing variables
       goal_to_me = agent.me.location - agent.friend_goal.location
       my_goal_to_ball,ball_dist = (agent.ball.location - agent.friend_goal.location).magnitude()
       
       #Checking if Nebula, their opponents, and their teammate are within 2000 UU of the ball
       me_close = (agent.me.location - agent.ball.location).magnitude() < 2000
       oppo_0_close = (agent.foes[0].location - agent.ball.location).magnitude() < 2000
       oppo_1_close = (agent.foes[1].location - agent.ball.location).magnitude() < 2000
       teammate_close = ((agent.friends[(self.index+1)%2].location - agent.ball.location).magnitude() < 2000)
       
       has_boost = agent.me.boost > 30
       
       #Checking if Nebula, their opponents, and their teammate are on their side of the pitch
       me_onside = (agent.me.location.y < -200) if (agent.friend_goal.y < 0) else (agent.me.location.y > 200)
       oppo_0_onside = (agent.foes[0].location.y < -200) if (agent.foe_goal.y < 0) else (agent.foes[0].location.y > 200)
       oppo_1_onside = (agent.foes[1].location.y < -200) if (agent.foe_goal.y < 1) else (agent.foes[1].location.y > 200)
       teammate_onside = (agent.friends[(self.index+1)%2].location.y < -200) if (agent.friend_goal.y < 1) else (agent.friends[(self.index+1)%2].location.y > 200)
       
       #Finding the closest opponent
       closest_oppo = 0
       if (agent.me.location - agent.foes[1].location).magnitude() < (agent.me.location - agent.foes[0].location).magnitude():
          closest_oppo = 1

       #Showing debug information
       if agent.team == 0:
           agent.debug_stack()

       #Main bot logic
       
       return_to_goal = False
       if len(agent.stack) < 1:
           if agent.kickoff_flag:
               agent.push(kickoff())
           elif me_close and not (oppo_0_close or oppo_1_close):
               left_field = Vector3(4200 * -side(agent.team), agent.ball.location.y + (1000 * -side(agent.team)), 0)
               right_field = Vector3(4200 * side(agent.team), agent.ball.location.y + (1000 * side(agent.team)), 0)
               targets = {"goal":(agent.foe_goal,agent.foe_goal), "upfield": (left_field,right_field)}
               shots = find_hits(agent,targets)
               if len(shots["goal"]) > 0:
                   agent.push(shots["goal"][0])
               elif len(shots["upfield"]) > 0 and abs(agent.friend_goal.location.y - agent.ball.location.y) < 8490:
                   agent.push(shots["upfield"][0])
               else:
                   return_to_goal = True
           elif not me_onside and not has_boost:
               boosts = [boost for boost in agent.boosts if boost.large and boost.active and abs(agent.friend_goal.location.y - boost.location.y) - 200 < abs(agent.friend_goal)]
               if len(boosts) > [0]:
                 for boost in boosts:
                   closest = boost
                   if (boost.location - agent.me.location).magnitude() < (closest.location - agent.me.location).magnitude():
                       closest = boost
                   agent.push(goto_boost())
               else:
                   return_to_goal = True
           else:
               agent.push(short_shot(agent.foe_goal.location))

       if return_to_goal == True:
         relative_target = agent.friend_goal.location - agent.me.location
         angles = defaultPD(agent, agent.me.local(relative_target))
         defaultThrottle(agent,2300)
         agent.controller.boost = False if abs(angles[1]) > 0.5 or agent.me.airborne else agent.controller.boost
         agent.controller.handbrake = True if abs(angles[1]) > 2.8 else False

       if (((agent.me.location - agent.foes[0].location).magnitude() < 250) or ((agent.me.location - agent.foes[1].location).magnitude() < 250)) and ball_dist < 750:
           agent.controller.boost = True
           agent.push(goto(agent.foes[closest_oppo].location))

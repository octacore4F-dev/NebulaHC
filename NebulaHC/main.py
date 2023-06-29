from util.tools import  *
from util.objects import *
from util.routines import *

#This file is for strategy

class main(GoslingAgent):

    def run(agent):
       #Precomputing variables
       team8 = 0 if (agent.friends[0].location != agent.me.location) else 1
       goal_to_me = agent.me.location - agent.friend_goal.location
       ball_dist = (agent.ball.location - agent.friend_goal.location).magnitude()
       
       #Checking the time it'll take for each player to get to the ball (very roughly)
       def timetoball(me):
           dist = agent.ball.location - me.location
           for i in range(600):
               dist -= (agent.ball.velocity - (me.velocity + agent.ball.velocity.normalize()*10*i))
               if dist < 100:
                   return i/10
       me_toball = timetoball(agent.me)
       oppo_0_toball = timetoball(agent.foes[0])
       oppo_1_toball = timetoball(agent.foes[1])
       teammate_toball = timetoball(agent.friends[team8])
       
       #Checking if Nebula, their opponents, and their teammate are on their respective team's side of the pitch
       me_onside = (agent.me.location.y < -200) if (agent.friend_goal.y < 0) else (agent.me.location.y > 200)
       oppo_0_onside = (agent.foes[0].location.y < -200) if (agent.foe_goal.y < 0) else (agent.foes[0].location.y > 200)
       oppo_1_onside = (agent.foes[1].location.y < -200) if (agent.foe_goal.y < 1) else (agent.foes[1].location.y > 200)
       teammate_onside = (agent.friends[team8].location.y < -200) if (agent.friend_goal.y < 1) else (agent.friends[team8].location.y > 200)
       
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
               if ((agent.me.location.y - agent.friends[team8].location.y) > 0) or (((agent.me.location.y - agent.friends[team8].location.y) == 0) and (agent.me.location.x > agent.friends[team8].location.x)):
                   agent.push(kickoff())
               else: agent.push(goto(agent.friend_goal.location))
           elif (me_toball + 0.5 < oppo_0_toball) and (me_toball +.5 < oppo_1_toball) and (me_toball < teammate_toball):
               left_field = Vector3(3968, (agent.foe_goal.y/abs(agent.foe_goal.y))*5120, 0)
               right_field = Vector3(-3968, (agent.foe_goal.y/abs(agent.foe_goal.y))*5120, 0)
               targets = {"goal":(agent.foe_goal.left_post,agent.foe_goal.right_post), "upfield": (left_field,right_field), "pass": (agent.friends[team8].location + agent.friends[team8].velocity/2,agent.friends[team8].location + agent.friends[team8].velocity*1.5)}
               shots = find_hits(agent,targets)
               if len(shots["goal"]) > 0:
                   agent.push(shots["goal"][0])
               elif len(shots["pass"]) > 0 and (agent.friends[team8].location - agent.foes[0].location).magnitude() > 2000 and (agent.friends[team8].location - agent.foes[1].location).magnitude() > 2000:
                   agent.push(shots["pass"][0])
               elif len(shots["upfield"]) > 0 and abs(agent.friend_goal.location.y - agent.ball.location.y) < 8490:
                   agent.push(shots["upfield"][0])
               else:
                   return_to_goal = True
           elif me_onside and (agent.me.boost < 30) and (teammate_toball + 0.5 < oppo_0_toball) and (teammate_toball + 0.5 < oppo_1_toball):
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
         agent.push(goto(agent.friend_goal.location))

       if (((agent.me.location - agent.foes[0].location).magnitude() < 250) or ((agent.me.location - agent.foes[1].location).magnitude() < 250)) and ball_dist < 750:
           agent.controller.boost = True
           agent.push(goto(agent.foes[closest_oppo].location + (agent.foes[closest_oppo].velocity/3))

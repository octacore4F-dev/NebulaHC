from util.tools import  *
from util.objects import *
from util.routines import *

#This file is for strategy

class main(GoslingAgent):

    def run(agent):

       goal_to_me = agent.me.location - agent.friend_goal.location
       my_goal_to_ball,ball_dist = (agent.ball.location - agent.friend_goal.location).normalize(True)
       my_dist = my_goal_to_ball - goal_to_me
       close = (agent.me.location - agent.ball.location).magnitude() < 2000
       has_boost = agent.me.boost > 30
       me_onside = (my_dist - 200).magnitude() > ball_dist
       oppo0_onside = abs(agent.foe_goal.location.y - agent.foes[0].location.y) - 200 > abs(agent.foe_goal.location.y - agent.ball.location.y)
       oppo1_onside = abs(agent.foe_goal.location.y - agent.foes[0].location.y) - 200 > abs(agent.foe_goal.location.y - agent.ball.location.y)
       my_point = agent.friend_goal.location + (my_goal_to_ball * my_dist)
       closest_oppo = 0


       if (agent.me.location - agent.foes[1].location).magnitude() < (agent.me.location - agent.foes[0].location).magnitude():
          closest_oppo = 1

       if agent.team == 0:
           agent.debug_stack()

       return_to_goal = False

       if len(agent.stack) < 1:
           if agent.kickoff_flag:
               agent.push(kickoff())
           elif (close and me_onside) or ((oppo0_onside or oppo1_onside) and me_onside):
               targets = {"goal":(agent.foe_goal,agent.foe_goal), "upfield": (left_field,right_field)}
               left_field = Vector3(4200*-side(agent.team),agent.ball.location.y + (1000*-side(agent.team)),0)
               right_field = Vector3(4200* side(agent.team),agent.ball.location.y + (1000* side(agent.team)),0)
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
                   if (boost.location - agent.me.location).magnitude() < (closest.location - agent.me.location).magnitude():
                       closest = boost
                   agent.push(goto_boost())
               else:
                   return_to_goal = True
           else:
               agent.push(short_shot(agent.foe_goal.location))

       if return_to_goal == True:
         relative_target = agent.friend_goal.location - agent.me.locations
         angles = defaultPD(agent, agent.me.local(relative_target))
         defaultThrottle(agent,2300)
         agent.controller.boost = False if abs(angles[1]) > 0.5 or agent.me.airborne else agent.controller.boost
         agent.controller.handbrake = True if abs(angles[1]) > 2.8 else False

       if (((agent.me.location - agent.foes[0].location).magnitude() < 250) or ((agent.me.location - agent.foes[1].location).magnitude() < 250)) and ball_dist < 750:
           agent.controller.boost
           agent.push(goto(agent.foes[closest_oppo].location))
           time.sleep(1.5)

       if (agent.me.boost < 30) and (oppo0_onside or oppo1_onside):
           agent.push(goto_boost())

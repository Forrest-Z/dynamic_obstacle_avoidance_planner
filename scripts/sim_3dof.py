#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Empty
import tf

import math as m

pose = PoseStamped()
velocity = Twist()
stop_flag = False

HZ = 100.0

def velocity_callback(data):
  print "velocity callback"
  global velocity
  velocity = data

def stop_callback(data):
  global stop_flag
  stop_flag = True

def process():
  ROBOT_FRAME = rospy.get_param("/dynamic_avoidance/ROBOT_FRAME")
  VELOCITY_TOPIC_NAME = rospy.get_param("/dynamic_avoidance/VELOCITY_TOPIC_NAME")

  rospy.Subscriber(VELOCITY_TOPIC_NAME, Twist, velocity_callback)
  rospy.Subscriber("/stop", Empty, stop_callback)

  print "=== sim 3dof ==="

  br = tf.TransformBroadcaster()

  pose.pose.orientation.w = 1
  pose.header.frame_id = ROBOT_FRAME

  velocity.linear.x = 0
  velocity.linear.y = 0
  velocity.angular.z = 0

  r = rospy.Rate(HZ)

  while not rospy.is_shutdown():
    if stop_flag:
      velocity.linear.x = 0
      velocity.linear.y = 0

    q_list = [pose.pose.orientation.x, pose.pose.orientation.y, pose.pose.orientation.z, pose.pose.orientation.w]
    (roll, pitch, yaw) = tf.transformations.euler_from_quaternion(q_list)
    q = tf.transformations.quaternion_from_euler(roll, pitch, yaw + velocity.angular.z / HZ)
    pose.pose.orientation.x = q[0]
    pose.pose.orientation.y = q[1]
    pose.pose.orientation.z = q[2]
    pose.pose.orientation.w = q[3]
    pose.pose.position.x += velocity.linear.x * m.cos(yaw) / HZ - velocity.linear.y * m.sin(yaw) / HZ
    pose.pose.position.y += velocity.linear.x * m.sin(yaw) / HZ + velocity.linear.y * m.cos(yaw) / HZ
    br.sendTransform((pose.pose.position.x, pose.pose.position.y, 0), (pose.pose.orientation.x, pose.pose.orientation.y, pose.pose.orientation.z, pose.pose.orientation.w), rospy.Time.now(), ROBOT_FRAME, "odom")
    print pose
    r.sleep()

if __name__=='__main__':
  rospy.init_node('sim_3dof')
  try:
    process()
  except rospy.ROSInterruptException: pass

#!/usr/bin/env bash

set -e

echo "🚀 Starting TurtleBot3 (FINAL STABLE SETUP)..."

# -----------------------------
# ENV
# -----------------------------
export TURTLEBOT3_MODEL=burger
export GZ_SIM_RESOURCE_PATH=/opt/ros/jazzy/share
export GZ_TRANSPORT_IP=127.0.0.1

source /opt/ros/jazzy/setup.bash

# -----------------------------
# START GAZEBO SERVER ONLY
# -----------------------------
echo "🌍 Starting Gazebo (HEADLESS SERVER)..."

gz sim -r -s /opt/ros/jazzy/share/turtlebot3_gazebo/worlds/empty_world.world &

sleep 5

# -----------------------------
# ROBOT STATE PUBLISHER (FIRST)
# -----------------------------
echo "🧭 Starting robot_state_publisher..."

ros2 run robot_state_publisher robot_state_publisher \
  --ros-args \
  -p use_sim_time:=true \
  -p robot_description:="$(xacro /opt/ros/jazzy/share/turtlebot3_description/urdf/turtlebot3_burger.urdf)" \
&

sleep 3

# -----------------------------
# SPAWN ROBOT (CRITICAL FIX)
# -----------------------------
echo "🧱 Spawning TurtleBot3 (URDF-based)..."

ros2 run ros_gz_sim create \
  -name turtlebot3 \
  -topic robot_description

sleep 5

# -----------------------------
# VERIFY CONTROL TOPIC
# -----------------------------
echo "🔍 Checking Gazebo topics..."

gz topic -l | grep turtlebot3 || true

echo ""
echo "👉 MUST SEE:"
echo "   /model/turtlebot3/cmd_vel"
echo ""

# -----------------------------
# BRIDGE (CORRECT)
# -----------------------------
echo "🌉 Starting bridge..."

ros2 run ros_gz_bridge parameter_bridge \
  /model/turtlebot3/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist \
  /scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan \
  /world/default/model/turtlebot3/odometry@nav_msgs/msg/Odometry@gz.msgs.Odometry \
  /clock@rosgraph_msgs/msg/Clock@gz.msgs.Clock \
  --ros-args -r /cmd_vel:=/model/turtlebot3/cmd_vel
  &

sleep 3

# -----------------------------
# EKF (TF FIX)
# -----------------------------
echo "📡 Starting EKF..."

ros2 run robot_localization ekf_node \
  --ros-args \
  -p use_sim_time:=true \
  -p publish_tf:=true \
  -p base_link_frame:=base_link \
  -p odom_frame:=odom \
  -p world_frame:=odom \
  -p odom0:=/world/default/model/turtlebot3/odometry \
&

sleep 2

# -----------------------------
# READY
# -----------------------------
echo ""
echo "✅ SYSTEM READY"
echo ""

echo "👉 TEST MOTION:"
echo "ros2 topic pub /model/turtlebot3/cmd_vel geometry_msgs/msg/Twist '{linear: {x: 0.2}, angular: {z: 0.0}}'"
echo ""

echo "👉 TELEOP:"
echo "ros2 run turtlebot3_teleop teleop_keyboard --ros-args -r cmd_vel:=/model/turtlebot3/cmd_vel"
echo ""

# -----------------------------
# KEEP ALIVE
# -----------------------------
wait
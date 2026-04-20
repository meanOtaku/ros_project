from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node

def generate_launch_description():

    # -----------------------------
    # GAZEBO
    # -----------------------------
    gz_sim = ExecuteProcess(
        cmd=[
            "gz", "sim",
            "-r",
            "-s",
            "/opt/ros/jazzy/share/turtlebot3_gazebo/worlds/empty_world.world"
        ],
        additional_env={
            "QT_QPA_PLATFORM": "minimal",
            "DISPLAY": ""
        },
        output="screen"
    )

    # -----------------------------
    # 🔥 FIXED SDF (SINGLE LINE)
    # -----------------------------
    sdf = """sdf: "<sdf version='1.9'><model name='tb3_fixed'>
<pose>0 0 0.1 0 0 0</pose>

<link name='base_link'>
  <inertial><mass>1.0</mass></inertial>
  <collision name='col'>
    <geometry><box><size>0.3 0.3 0.2</size></box></geometry>
  </collision>
  <visual name='vis'>
    <geometry><box><size>0.3 0.3 0.2</size></box></geometry>
  </visual>
</link>

<link name='left_wheel'><pose>0 0.15 0 0 0 0</pose></link>
<link name='right_wheel'><pose>0 -0.15 0 0 0 0</pose></link>

<joint name='left_joint' type='revolute'>
  <parent>base_link</parent>
  <child>left_wheel</child>
  <axis><xyz>0 1 0</xyz></axis>
</joint>

<joint name='right_joint' type='revolute'>
  <parent>base_link</parent>
  <child>right_wheel</child>
  <axis><xyz>0 1 0</xyz></axis>
</joint>

<!-- 🔥 FIXED -->
<plugin name='diff_drive' filename='gz-sim8-diff-drive-system'>
  <left_joint>left_joint</left_joint>
  <right_joint>right_joint</right_joint>
  <wheel_separation>0.3</wheel_separation>
  <wheel_radius>0.05</wheel_radius>
  <topic>/cmd_vel</topic>
</plugin>

</model></sdf>\""""

    spawn = TimerAction(
        period=3.0,
        actions=[
            ExecuteProcess(
                cmd=[
                    "gz", "service",
                    "-s", "/world/default/create",
                    "--reqtype", "gz.msgs.EntityFactory",
                    "--reptype", "gz.msgs.Boolean",
                    "--timeout", "1000",
                    "--req",
                    "sdf_filename: '/workspace/models/tb3_fixed/model.sdf'"
                ],
                output="screen"
            )
        ]
    )

    # -----------------------------
    # BRIDGE
    # -----------------------------
    bridge = TimerAction(
        period=5.0,
        actions=[
            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                arguments=[
                    "/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist"
                ],
                output="screen"
            )
        ]
    )

    # -----------------------------
    # FOXGLOVE (FIXED PORT)
    # -----------------------------
    foxglove = Node(
        package="foxglove_bridge",
        executable="foxglove_bridge",
        parameters=[{
            "port": 8766   # 🔥 changed from 8765
        }],
        output="screen"
    )

    return LaunchDescription([
        gz_sim,
        spawn,
        bridge,
        foxglove
    ])
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():

    # -----------------------------
    # GAZEBO (FIXED WORLD)
    # -----------------------------
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            '/opt/ros/jazzy/share/ros_gz_sim/launch/gz_sim.launch.py'
        ),
        launch_arguments={
            'gz_args': '-r -s --headless-rendering /opt/ros/jazzy/share/turtlebot3_gazebo/worlds/empty_world.world',
        }.items()
    )

    # -----------------------------
    # UNPAUSE
    # -----------------------------
    unpause = TimerAction(
        period=2.0,
        actions=[
            ExecuteProcess(
                cmd=[
                    'gz', 'service',
                    '-s', '/world/default/control',
                    '--reqtype', 'gz.msgs.WorldControl',
                    '--reptype', 'gz.msgs.Boolean',
                    '--timeout', '2000',
                    '--req', 'pause: false'
                ]
            )
        ]
    )

    # -----------------------------
    # SPAWN CUBE
    # -----------------------------
    spawn = TimerAction(
        period=6.0,
        actions=[
            ExecuteProcess(
                cmd=[
                    "gz", "service",
                    "-s", "/world/default/create",
                    "--reqtype", "gz.msgs.EntityFactory",
                    "--reptype", "gz.msgs.Boolean",
                    "--timeout", "2000",
                    "--req",
                    "sdf_filename: '/workspace/models/cube_bot/model.sdf'"
                ],
                output="screen"
            )
        ]
    )

    # -----------------------------
    # BRIDGE
    # -----------------------------
    bridge = TimerAction(
        period=8.0,
        actions=[
            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                arguments=[
                    # ✅ CONTROL (ROS → GZ)
                    "/model/cube_bot/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist",

                    # clock
                    "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",

                    # TF
                    "/model/cube_bot/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V"
                ],
                parameters=[{"lazy": False}],
                output="screen"
            )
        ]
    )

    # -----------------------------
    # POSE → TF (SCRIPT)
    # -----------------------------
    pose_tf = ExecuteProcess(
        cmd=["python3", "/workspace/pose_to_tf.py"],
        output="screen"
    )

    # -----------------------------
    # FOXGLOVE
    # -----------------------------
    foxglove = Node(
        package="foxglove_bridge",
        executable="foxglove_bridge",
        parameters=[{"port": 8766}],
        output="screen"
    )

    return LaunchDescription([
        gz_sim,
        unpause,
        spawn,
        bridge,
        foxglove
    ])
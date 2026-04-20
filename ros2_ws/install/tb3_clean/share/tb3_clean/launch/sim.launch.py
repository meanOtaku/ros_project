from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node
from launch.substitutions import Command
import glob


def get_plugin_path():
    paths = glob.glob("/usr/lib/*/gz-sim*/plugins")
    return paths[0] if paths else ""


def generate_launch_description():

    plugin_path = get_plugin_path()

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
            "DISPLAY": "",
            "GZ_SIM_SYSTEM_PLUGIN_PATH": plugin_path,
            "LD_LIBRARY_PATH": plugin_path,
        },
        output="screen"
    )

    # -----------------------------
    # ROBOT STATE PUBLISHER (TF)
    # -----------------------------
    rsp = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{
            "use_sim_time": True,
            "robot_description": Command([
                "xacro ",
                "/opt/ros/jazzy/share/turtlebot3_description/urdf/turtlebot3_burger.urdf"
            ])
        }]
    )

    # -----------------------------
    # SPAWN TURTLEBOT3
    # -----------------------------
    spawn = TimerAction(
        period=3.0,
        actions=[
            Node(
                package="ros_gz_sim",
                executable="create",
                arguments=[
                    "-name", "turtlebot3",
                    "-topic", "robot_description"
                ],
                output="screen"
            )
        ]
    )

    # -----------------------------
    # BRIDGE (ALL IMPORTANT TOPICS)
    # -----------------------------
    bridge = TimerAction(
        period=5.0,
        actions=[
            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                arguments=[
                    # control
                    "/model/turtlebot3/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist",

                    # LiDAR
                    "/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan",

                    # odometry
                    "/world/default/model/turtlebot3/odometry@nav_msgs/msg/Odometry@gz.msgs.Odometry",

                    # clock
                    "/clock@rosgraph_msgs/msg/Clock@gz.msgs.Clock"
                ],
                output="screen"
            )
        ]
    )

    # -----------------------------
    # EKF (TF: odom → base_link)
    # -----------------------------
    ekf = Node(
        package="robot_localization",
        executable="ekf_node",
        name="ekf_filter_node",
        parameters=[{
            "use_sim_time": True,
            "publish_tf": True,

            "base_link_frame": "base_link",
            "odom_frame": "odom",
            "world_frame": "odom",

            "odom0": "/world/default/model/turtlebot3/odometry",
        }],
        output="screen"
    )

    # -----------------------------
    # FOXGLOVE
    # -----------------------------
    foxglove = Node(
        package="foxglove_bridge",
        executable="foxglove_bridge",
        output="screen"
    )

    return LaunchDescription([
        gz_sim,
        rsp,
        spawn,
        bridge,
        ekf,
        foxglove
    ])
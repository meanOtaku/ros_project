from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from launch.substitutions import Command

def generate_launch_description():

    gz_sim = ExecuteProcess(
        cmd=[
            "gz", "sim",
            "-r",
            "-s",
            "--iterations", "0",   # run indefinitely
            "/opt/ros/jazzy/share/turtlebot3_gazebo/worlds/empty_world.world"
        ],
        additional_env={
            "QT_QPA_PLATFORM": "minimal",   # 🔥 critical
            "DISPLAY": "",                  # 🔥 no X11
            "GZ_GUI_PLUGIN_PATH": "",       # 🔥 disables GUI plugins
            "GZ_SIM_SYSTEM_PLUGIN_PATH": "" # 🔥 prevents GUI system load
        },
        output="screen"
    )

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

    spawn = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=["-name", "turtlebot3", "-topic", "robot_description"],
        output="screen"
    )

    # ✅ ONLY bridge ROS → GZ (cmd_vel)
    bridge_cmd_vel = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/model/turtlebot3/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist"
        ],
        remappings=[
            ("/model/turtlebot3/cmd_vel", "/cmd_vel")
        ],
        output="screen"
    )

    # Sensors (safe to bridge normally)
    bridge_sensors = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan",
            "/world/default/model/turtlebot3/odometry@nav_msgs/msg/Odometry@gz.msgs.Odometry",
            "/clock@rosgraph_msgs/msg/Clock@gz.msgs.Clock"
        ],
        output="screen"
    )

    ekf = Node(
        package="robot_localization",
        executable="ekf_node",
        parameters=[{
            "use_sim_time": True,
            "publish_tf": True,
            "base_link_frame": "base_link",
            "odom_frame": "odom",
            "world_frame": "odom",
            "odom0": "/world/default/model/turtlebot3/odometry"
        }]
    )

    return LaunchDescription([
        gz_sim,
        rsp,
        spawn,
        bridge_cmd_vel,
        bridge_sensors,
        ekf
    ])

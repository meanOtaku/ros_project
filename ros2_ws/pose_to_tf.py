import rclpy
from rclpy.node import Node
from tf2_msgs.msg import TFMessage
from geometry_msgs.msg import TransformStamped
from ros_gz_interfaces.msg import Pose_V


class PoseToTF(Node):
    def __init__(self):
        super().__init__('pose_to_tf')

        self.sub = self.create_subscription(
            Pose_V,
            '/world/default/dynamic_pose/info',
            self.callback,
            10
        )

        self.pub = self.create_publisher(TFMessage, '/tf', 10)

    def callback(self, msg):
        tf_msg = TFMessage()

        for pose in msg.pose:
            t = TransformStamped()

            t.header.stamp = self.get_clock().now().to_msg()
            t.header.frame_id = 'world'
            t.child_frame_id = pose.name  # model name

            t.transform.translation.x = pose.position.x
            t.transform.translation.y = pose.position.y
            t.transform.translation.z = pose.position.z

            t.transform.rotation = pose.orientation

            tf_msg.transforms.append(t)

        self.pub.publish(tf_msg)


def main():
    rclpy.init()
    node = PoseToTF()
    rclpy.spin(node)
    rclpy.shutdown()
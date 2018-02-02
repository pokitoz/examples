# Copyright 2018 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from example_interfaces.srv import AddTwoInts

import rclpy
from rclpy.callback_groups import ReentrantCallbackGroup

def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node('minimal_client')
    # Node's default callback group is mutually exclusive. This would prevent the client response
    # from being processed until the timer callback finished, but the timer callback in this
    # example is waiting for the client response
    cb_group = ReentrantCallbackGroup()
    cli = node.create_client(AddTwoInts, 'add_two_ints', callback_group=cb_group)
    did_run = False
    did_get_result = False

    async def call_service():
        nonlocal cli, node, did_run, did_get_result
        did_run = True
        try:
            req = AddTwoInts.Request()
            req.a = 41
            req.b = 1
            print("_____Calling client")
            future = cli.call_async(req)
            print ("_____awaiting future")
            result = await future
            print("_____Checking result")
            if future.result() is not None:
                node.get_logger().info(
                    'Result of add_two_ints: for %d + %d = %d' %
                    (req.a, req.b, future.result().sum))
            else:
                node.get_logger().info('Service call failed %r' % (future.exception(),))
        finally:
            print("_____Done with service callbac")
            import traceback
            traceback.print_exc()
            did_get_result = True

    while not cli.wait_for_service(timeout_sec=1.0):
        node.get_logger().info('service not available, waiting again...')

    timer = node.create_timer(0.5, call_service, callback_group=cb_group)

    print("Waiting for callback to get called")
    while rclpy.ok() and not did_run:
        print("About to call spin_once")
        rclpy.spin_once(node)
        print("looping again")

    print("Done waiting for callback to be called")
    if did_run:
        print("callback did run")
        # call timer callback only once
        timer.cancel()

    print ("Waiting for result")
    while rclpy.ok() and not did_get_result:
        rclpy.spin_once(node)

    print("Got result, shutting down")

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

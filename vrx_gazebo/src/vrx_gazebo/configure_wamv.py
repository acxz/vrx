#!/usr/bin/env python3
import rospy
import os

from vrx_gazebo.compliance import SensorCompliance
from vrx_gazebo.compliance import ThrusterCompliance
from vrx_gazebo.compliance import BallShooterCompliance

from vrx_gazebo.utils import create_xacro_file
from vrx_gazebo.utils import add_gazebo_thruster_config


def main():

    rospy.init_node("wamv_generator", anonymous=True)
    # Check if yaml files were given
    received_thruster_yaml = len(rospy.get_param('thruster_yaml')) > 0
    received_sensor_yaml = len(rospy.get_param('sensor_yaml')) > 0
    received_ball_yaml = len(rospy.get_param('ball_shooter_yaml')) > 0

    # Setup thruster xacro
    if received_thruster_yaml:
        thruster_compliant = create_thruster_xacro()

    # Setup sensor xacro
    if received_sensor_yaml:
        sensor_compliant = create_sensor_xacro()

    # Setup ball shooter xacro
    if received_ball_yaml:
        ball_compliant = create_ball_shooter_xacro()

    # Setup command to generate WAM-V urdf file
    wamv_target = rospy.get_param('wamv_target')
    wamv_gazebo = rospy.get_param('wamv_gazebo')

    create_urdf_command = ("rosrun xacro xacro -o " + wamv_target +
                           " '" + wamv_gazebo + "'")

    # Add xacro files if created
    if received_thruster_yaml:
        thruster_yaml = rospy.get_param('thruster_yaml')
        thruster_xacro_target = os.path.splitext(thruster_yaml)[0] + '.xacro'
        create_urdf_command += (" yaml_thruster_generation:=true "
                                "thruster_xacro_file:=" +
                                thruster_xacro_target)
    if received_sensor_yaml:
        sensor_yaml = rospy.get_param('sensor_yaml')
        sensor_xacro_target = os.path.splitext(sensor_yaml)[0] + '.xacro'
        create_urdf_command += (" yaml_sensor_generation:=true "
                                "sensor_xacro_file:=" + sensor_xacro_target)

    if received_ball_yaml:
        ball_yaml = rospy.get_param('ball_shooter_yaml')
        ball_xacro_target = os.path.splitext(ball_yaml)[0] + '.xacro'
        create_urdf_command += (" yaml_ball_shooter_generation:=true "
                                "ball_shooter_xacro_file:=" + ball_xacro_target)

    # Create urdf and print to console
    print('CHECK HERE')
    print(create_urdf_command)
    os.system(create_urdf_command)
    if not (thruster_compliant and sensor_compliant and ball_compliant):
        rospy.logerr('\nThis sensor/thruster/ball shooter configuration is NOT ' +
                     'compliant with the (current) VRX constraints. A urdf file ' +
                     'will be created, but please note that the above errors ' +
                     'must be fixed for this to be a valid configuration ' +
                     'for the VRX competition.\n')

    print('WAM-V urdf file sucessfully generated. File location: ' +
          wamv_target)

def create_thruster_xacro():
    """
    Purpose: Create a thruster xacro file using the given
             rosparameters
    """
    # Get yaml files for thruster number and pose
    thruster_yaml = rospy.get_param('thruster_yaml')
    rospy.loginfo('\nUsing %s as the thruster configuration yaml file\n' %
                  thruster_yaml)

    # Set thruster xacro target
    thruster_xacro_target = os.path.splitext(thruster_yaml)[0] + '.xacro'
    rospy.loginfo('\nTrying to open %s \n' % thruster_xacro_target)

    # Things to start/open the macro
    thruster_boiler_plate_top = ('<?xml version="1.0"?>\n'
                                 '<robot '
                                 'xmlns:xacro="http://ros.org/wiki/xacro" '
                                 'name="wam-v-thrusters">\n'
                                 '  <xacro:include filename='
                                 '"$(find wamv_description)/urdf/thrusters/'
                                 'engine.xacro" />\n')

    # Things to close the macro
    thruster_boiler_plate_bot = ''

    # Check if valid number of thrusters and valid thruster parameters
    comp = ThrusterCompliance()
    thruster_num_test = comp.number_compliance
    thruster_param_test = comp.param_compliance

    # Create thruster xacro with thruster macros
    compliant = create_xacro_file(yaml_file=thruster_yaml,
                                  xacro_target=thruster_xacro_target,
                                  boiler_plate_top=thruster_boiler_plate_top,
                                  boiler_plate_bot=thruster_boiler_plate_bot,
                                  num_test=thruster_num_test,
                                  param_test=thruster_param_test)

    gz_boiler_plate_top = ('  <gazebo>\n'
                           '    <plugin name="wamv_gazebo_thrust" '
                           'filename="libusv_gazebo_thrust_plugin.so">\n'
                           '      <cmdTimeout>1.0</cmdTimeout>\n'
                           '      <robotNamespace>${namespace}</robotNamespace>\n'
                           '      <xacro:include filename="$(find wamv_gazebo)'
                           '/urdf/thruster_layouts/'
                           'wamv_gazebo_thruster_config.xacro" />\n')
    gz_boiler_plate_bot = ('    </plugin>\n'
                           '  </gazebo>\n'
                           '</robot>')

    # Append gazebo thruster config to thruster xacro
    add_gazebo_thruster_config(yaml_file=thruster_yaml,
                               xacro_target=thruster_xacro_target,
                               boiler_plate_top=gz_boiler_plate_top,
                               boiler_plate_bot=gz_boiler_plate_bot,
                               )
    return compliant


def create_sensor_xacro():
    """
    Purpose: Create a sensor xacro file using the given
             rosparameters
    """
    # Get yaml files for sensor number and pose
    sensor_yaml = rospy.get_param('sensor_yaml')
    rospy.loginfo('\nUsing %s as the sensor configuration yaml file\n' %
                  sensor_yaml)

    # Set sensor xacro target
    sensor_xacro_target = os.path.splitext(sensor_yaml)[0] + '.xacro'

    # Things to start/open the macro
    sensor_boiler_plate_top = ('<?xml version="1.0"?>\n'
                               '<robot '
                               'xmlns:xacro="http://ros.org/wiki/xacro" '
                               'name="wam-v-sensors">\n' +
                               '  <xacro:macro name="yaml_sensors">\n')

    # Things to close the macro
    sensor_boiler_plate_bot = '  </xacro:macro>\n</robot>'

    # Check if valid number of sensors and valid sensor parameters
    comp = SensorCompliance()
    sensor_num_test = comp.number_compliance
    sensor_param_test = comp.param_compliance

    # Create sensor xacro with sensor macros
    return create_xacro_file(yaml_file=sensor_yaml,
                             xacro_target=sensor_xacro_target,
                             boiler_plate_top=sensor_boiler_plate_top,
                             boiler_plate_bot=sensor_boiler_plate_bot,
                             num_test=sensor_num_test,
                             param_test=sensor_param_test)


def create_ball_shooter_xacro():
    """
    Purpose: Create a ball shooter xacro file using the given
             rosparameters
    """
    # Get yaml files for ball shooter pose
    ball_shooter_yaml = rospy.get_param('ball_shooter_yaml')
    # rospy.loginfo('\nUsing %s as the ball shooter configuration yaml file\n'
                  # ball_shooter_yaml)

    # Set ball shooter xacro target 
    ball_xacro_target = os.path.splitext(ball_shooter_yaml)[0] + '.xacro'

    # Things to start/open the macro
    ball_boiler_plate_top = ('<?xml version="1.0"?>\n'
                             '<robot '
                             'xmlns:xacro="http://ros.org/wiki/xacro" '
                             'name="wam-v-ball-shooter">\n' +
                             '  <xacro:macro name="yaml_ball_shooter">\n')

    # Things to close the macro 
    ball_boiler_plate_bot = '  </xacro:macro>\n</robot>'

    # Check if valid number of ball shooters valid ball shooter parameters
    comp = BallShooterCompliance()
    ball_num_test = comp.number_compliance
    ball_param_test = comp.param_compliance

    # Create ball shooter xacro with ball shooter macros
    return create_xacro_file(yaml_file=ball_shooter_yaml,
                             xacro_target=ball_xacro_target,
                             boiler_plate_top=ball_boiler_plate_top,
                             boiler_plate_bot=ball_boiler_plate_bot,
                             num_test=ball_num_test,
                             param_test=ball_param_test)
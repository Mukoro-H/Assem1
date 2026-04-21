## Tracked robot
## Giới thiệu
Dự án này là hệ thống mô phỏng hoạt động trong môi trường ROS 2 (Humble), RViz và Gazebo. 
## Tính năng
* *Manipulator:* Cánh tay 2 bậc tự do được điều khiển vị trí thông qua hệ sinh thái ros2_control và position_controllers
* *Sensors:* Tích hợp và hiển thị đồng bộ trên RViz:
  * Lidar 360 độ (2 cụm truoc/sau).
  * Camera RGB gắn ở đầu robot
  * Odometry phản hồi từ bộ mã hóa (Encoder) bánh xe.
# Sau khi tải về đổi tên package thành Assem1

sudo apt update
# Cài đặt Gazebo
sudo apt install gazebo11 libgazebo11-dev -y

# Cài đặt ROS-Gazebo và các Plugins cảm biến
sudo apt install ros-humble-gazebo-ros-pkgs ros-humble-gazebo-plugins -y

# Cài đặt hệ thần kinh ros2_control cho tay máy
sudo apt install ros-humble-ros2-control ros-humble-ros2-controllers ros-humble-gazebo-ros2-control -y

# Cài đặt gói điều khiển bàn phím
sudo apt install ros-humble-teleop-twist-keyboard -y
## Chạy chương trình

### Dọn dẹp và xây dựng không gian làm việc
Tại terminal 1(Chạy Gazebo và RViz):
cd ~/ros2_ws
killall -9 gzserver gzclient rviz2 robot_state_publisher joint_state_publisher spawner
rm -rf build/ install/ log/ ~/.gazebo/log/*
rm -rf build/ install/ log/
colcon build --packages-select Assem1
source install/setup.bash
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:~/ros2_ws/install/Assem1/share
export LIBGL_ALWAYS_SOFTWARE=1
ros2 launch Assem1 gazebo.launch.py

Terminal 2(Điều khiển tay máy và robot):
cd ~/ros2_ws
source install/setup.bash
python3 src/Assem1/teleop_unified.py

Terminal 3(Check dữ liệu Encoder): ros2 topic echo /odom


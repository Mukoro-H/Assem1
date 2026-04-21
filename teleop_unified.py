#!/usr/bin/env python3
import select
import sys
import termios
import tty
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64MultiArray

class UnifiedControl(Node):
    def __init__(self):
        super().__init__('unified_teleop')

        self.pub_vel = self.create_publisher(Twist, 'cmd_vel', 10)
        
        self.pub_arm = self.create_publisher(Float64MultiArray, '/arm_controller/commands', 10)
        
        self.timer = self.create_timer(0.05, self.loop)

        self.vx, self.wz = 0.0, 0.0

        self.dich_pos = 0.0
        self.xoay_pos = 0.0
        
        self.current_display = ""
        self.last_display = None
        
        self.speed = 0.8
        self.turn_speed = 1.5
        
        self.last_key_time = self.get_clock().now()
        self.settings = termios.tcgetattr(sys.stdin)
        
        self.print_static_menu()

    def print_static_menu(self):
        sys.stdout.write("\033[H\033[J") 
        print("="*60)
        print("    HỆ THỐNG ĐIỀU KHIỂN TỔNG HỢP - ROBOT ASSEM1")
        print("="*60)
        print(" XE DI CHUYỂN: 8 (Tiến) | 2 (Lùi) | Q hoặc 4/6 (Xoay)")
        print(" TAY MÁY     : U/I (Nâng/Hạ khớp trượt) | J/K (Xoay tay)")
        print(" DỪNG LẠI    : 5 (Dừng xe) hoặc nhả phím")
        print("-" * 60)
        print("\n")

    def get_key(self):
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.05)
        key = sys.stdin.read(1) if rlist else ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

    def loop(self):
        t = Twist()
        t.linear.x = self.vx
        t.angular.z = self.wz
        self.pub_vel.publish(t)

        arm_msg = Float64MultiArray()
        arm_msg.data = [self.dich_pos, self.xoay_pos]
        self.pub_arm.publish(arm_msg)

        if self.current_display != self.last_display:
            sys.stdout.write(f"\r\033[K>>> {self.current_display}")
            sys.stdout.flush()
            self.last_display = self.current_display

    def update_control(self, key):
        now = self.get_clock().now()
        if key:
            self.last_key_time = now
            k = key.lower()
            
            # ---------- ĐIỀU KHIỂN BÁNH XE ----------
            if k == '8': self.vx, self.wz, msg = self.speed, 0.0, "Nút 8: TIẾN TỚI"
            elif k == '2': self.vx, self.wz, msg = -self.speed, 0.0, "Nút 2: LÙI LẠI"
            elif k in ['4', 'q']: self.vx, self.wz, msg = 0.0, self.turn_speed, "Nút Q/4: XOAY TRÁI"
            elif k in ['6', 'e']: self.vx, self.wz, msg = 0.0, -self.turn_speed, "Nút E/6: XOAY PHẢI"
            elif k == '5': self.vx, self.wz, msg = 0.0, 0.0, "Nút 5: PHANH GẤP"
            
            # ---------- ĐIỀU KHIỂN TAY MÁY ----------
            elif k == 'u': 
                self.dich_pos = min(-0.015, self.dich_pos + 0.003) # Giới hạn max là 0.2m theo URDF
                msg = f"Nút U: Nâng khớp trượt ({self.dich_pos:.3f} m)"
            elif k == 'i': 
                self.dich_pos = max(0, self.dich_pos - 0.003) # Giới hạn min là 0m
                msg = f"Nút I: Hạ khớp trượt ({self.dich_pos:.3f} m)"
            elif k == 'j': 
                self.xoay_pos = min(1, self.xoay_pos + 0.05) # Giới hạn xoay theo URDF
                msg = f"Nút J: Xoay tay trái ({self.xoay_pos:.2f} rad)"
            elif k == 'k': 
                self.xoay_pos = max(-2, self.xoay_pos - 0.05)
                msg = f"Nút K: Xoay tay phải ({self.xoay_pos:.2f} rad)"
            
            else: msg = f"Phím vô tác dụng: [{k}]"
            
            self.current_display = msg
        else:
            if (now - self.last_key_time).nanoseconds * 1e-9 > 0.15:
                self.vx, self.wz = 0.0, 0.0
                self.current_display = "Trạng thái: CHỜ LỆNH (Đã nhả phím)"

def main():
    rclpy.init()
    node = UnifiedControl()
    try:
        while rclpy.ok():
            key = node.get_key()
            if key == '\x03': break # Ctrl+C để thoát
            node.update_control(key)
            rclpy.spin_once(node, timeout_sec=0.01)
    finally:
        node.pub_vel.publish(Twist()) # Phanh xe khi tắt
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, node.settings)
        print("\n\nĐã tắt hệ thống điều khiển!")
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
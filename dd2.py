from search import *  # Assuming you have a search.py file with necessary algorithms
import tkinter as tk
import tkinter.ttk as ttk
import time
import numpy as np
from PIL import Image, ImageTk



# Graph definition with distances (replace with actual city connections and distances)
romania_map = UndirectedGraph(dict(
    Cà_Mau=dict(Bạc_Liêu=101, Kiên_Giang=162),
    Bạc_Liêu=dict(Sóc_Trăng=100, Kiên_Giang=122),
    Kiên_Giang=dict( Cần_Thơ=89, An_Giang=123),
    Sóc_Trăng=dict(Hậu_Giang=73, Trà_Vinh=89),
    Hậu_Giang=dict(Kiên_Giang=89, Cần_Thơ=68, Vĩnh_Long=96),
    Cần_Thơ=dict(An_Giang=94, Vĩnh_Long=94, Đồng_Tháp=97),
    Trà_Vinh=dict(Bến_Tre=76, Vĩnh_Long=86),
    Vĩnh_Long=dict(Bến_Tre=94, Tiền_Giang=97, Đồng_Tháp=120),
    Bến_Tre=dict(Tiền_Giang=53),
    Tiền_Giang=dict(Long_An=66, TP_Hồ_Chí_Minh=87),
    Đồng_Tháp=dict(Tiền_Giang=151, Long_An=125, An_Giang=65),
    Long_An=dict(TP_Hồ_Chí_Minh=68),
    TP_Hồ_Chí_Minh=dict(Bà_Rịa_Vũng_Tàu=126, Đồng_Nai=111, Bình_Dương=90, Tây_Ninh=151),
    Bà_Rịa_Vũng_Tàu=dict(Đồng_Nai=92),
    Đồng_Nai=dict(Bình_Dương=98, Bình_Phước=147),
    Bình_Dương=dict(Bình_Phước=107, Tây_Ninh=105),
    Tây_Ninh=dict(Bình_Phước=157),
))

# City coordinates (replace with actual city locations for better results)
romania_map_locations = dict(
    Cà_Mau=(245, 640),
    Bạc_Liêu=(332, 587),
    Kiên_Giang=(271, 481),
    Sóc_Trăng=(419, 536),
    Hậu_Giang=(360, 492),
    Cần_Thơ=(341, 426),
    An_Giang=(276, 358),
    Trà_Vinh=(496, 491),
    Vĩnh_Long=(435, 431),
    Đồng_Tháp=(366, 332),
    Bến_Tre=(528, 422),
    Tiền_Giang=(512, 371),
    Long_An=(489, 309),
    TP_Hồ_Chí_Minh=(556, 296),
    Bà_Rịa_Vũng_Tàu=(676, 334),
    Đồng_Nai=(655, 244),
    Bình_Dương=(564, 206),
    Tây_Ninh=(463, 177),
    Bình_Phước=(603, 106)
)


# Create the main application window
class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.start = 'Cà_Mau'  # Default start city
        self.dest = 'Cà_Mau'   # Default destination city
        self.path_location = []

        self.title('Map Search')
        self.cvs_map = tk.Canvas(self, width=751, height=740,
                                 relief=tk.SUNKEN, border=1)
        
             # Chèn ảnh bản đồ dưới các đường vẽ
        self.load_map_image()
        
        self.ve_ban_do()
        lbl_frm_menu = tk.LabelFrame(self)
        lst_city = list(romania_map.graph_dict.keys())

        lbl_start = ttk.Label(lbl_frm_menu, text='Start')
        self.cbo_start = ttk.Combobox(lbl_frm_menu, values=lst_city)
        self.cbo_start.set('Cà_Mau')
        self.cbo_start.bind("<<ComboboxSelected>>", self.cbo_start_click)

        lbl_start.grid(row=0, column=0, padx=5, pady=0, sticky=tk.W)
        self.cbo_start.grid(row=1, column=0, padx=5, pady=5)

        lbl_dest = ttk.Label(lbl_frm_menu, text='Dest')
        self.cbo_dest = ttk.Combobox(lbl_frm_menu, values=lst_city)
        self.cbo_dest.set('Cà_Mau')
        self.cbo_dest.bind("<<ComboboxSelected>>", self.cbo_dest_click)

        btn_direction = ttk.Button(lbl_frm_menu, text='Direction', command=self.btn_direction_click)
        btn_run = ttk.Button(lbl_frm_menu, text='Run', command=self.btn_run_click)

        lbl_dest.grid(row=2, column=0, padx=5, pady=0, sticky=tk.W)
        self.cbo_dest.grid(row=3, column=0, padx=5, pady=5)
        btn_direction.grid(row=4, column=0, padx=5, pady=5)
        btn_run.grid(row=5, column=0, padx=5, pady=5)

        self.cvs_map.grid(row=0, column=0, padx=5, pady=5)
        lbl_frm_menu.grid(row=0, column=1, padx=5, pady=7, sticky=tk.N)

    def get_star_points(self, x, y, outer_radius, inner_radius):
        """Tính toán các điểm của ngôi sao (5 cánh)"""
        points = []
        for i in range(5):
              # Tính các điểm ngoài của ngôi sao
            angle = i * 2 * np.pi / 5
            x_outer = x + outer_radius * np.cos(angle)
            y_outer = y - outer_radius * np.sin(angle)
            points.append((x_outer, y_outer))
                
                # Tính các điểm trong của ngôi sao
            angle += np.pi / 5  # Bước đến điểm trong của ngôi sao
            x_inner = x + inner_radius * np.cos(angle)
            y_inner = y - inner_radius * np.sin(angle)
            points.append((x_inner, y_inner))
                
        return points

    def ve_ban_do(self):
        """Vẽ các thành phố và các đường nối giữa chúng trên bản đồ"""
        for city in romania_map.graph_dict:
            x0 = romania_map_locations[city][0] -100
            y0 = romania_map_locations[city][1]
            # self.cvs_map.create_rectangle(x0-4, y0-4, x0+4, y0+4,
            #                               fill='blue', outline='blue')
            star_points = self.get_star_points(x0, y0, 8, 4)
            self.cvs_map.create_polygon(star_points, fill='yellow', outline='yellow')


            for neighbor in romania_map.graph_dict[city]:
                x1 = romania_map_locations[neighbor][0] -100
                y1 = romania_map_locations[neighbor][1]
                self.cvs_map.create_line(x0, y0, x1, y1)
    def load_map_image(self):
        """Tải và hiển thị ảnh bản đồ trên canvas"""
        # Mở bức ảnh từ file
        map_image = Image.open("miennam.png")  # Đảm bảo đường dẫn đúng
        
        self.map_image_tk = ImageTk.PhotoImage(map_image)  # Chuyển ảnh thành định dạng Tkinter có thể sử dụng
         # Thu nhỏ ảnh (ví dụ thu nhỏ xuống 50% kích thước ban đầu)
        map_image = map_image.resize((int(map_image.width * 0.9), int(map_image.height * 0.9)))

        # Chuyển đổi ảnh PIL thành ảnh có thể vẽ được trong Tkinter
        self.tk_map_image = ImageTk.PhotoImage(map_image)

        # Vẽ ảnh lên canvas, di chuyển ảnh sang trái bằng cách điều chỉnh tọa độ
        self.cvs_map.create_image(-50, 40, image=self.tk_map_image, anchor=tk.NW)  # Di chuyển sang trái bằng cách thay đổi tọa độ x
        
    #     # Chèn ảnh vào canvas, ảnh sẽ nằm dưới các thành phố và đường vẽ
    #     # self.cvs_map.create_image(0, 0, image=self.map_image_tk, anchor=tk.NW)
    
    
    def cbo_start_click(self, *args):
        self.start = self.cbo_start.get()

    def cbo_dest_click(self, *args):
        self.dest = self.cbo_dest.get()

    def btn_direction_click(self):
        """Vẽ đường đi từ điểm bắt đầu đến đích"""
        self.cvs_map.delete(tk.ALL)
        self.load_map_image()
        self.ve_ban_do()

        romania_problem = GraphProblem(self.start, self.dest, romania_map)
        c = astar_search(romania_problem)
        lst_path = c.path()
        self.path_location = []
        for data in lst_path:
            city = data.state
            x = romania_map_locations[city][0] -100
            y = romania_map_locations[city][1]
            self.path_location.append((x, y))

        self.cvs_map.create_line(self.path_location, fill='red')

    
    def btn_run_click(self):
        """Hiển thị đường đi theo dạng chuyển động"""
        bg_color = self.cvs_map['background']
        N = 21
        d = 100
        L = len(self.path_location)
        
        # Đảm bảo rằng bạn không gặp lỗi không có giá trị cho x1, y1
        if L < 2:
            return  # Không đủ điểm để vẽ đường đi

        for i in range(0, L-1):
            x0, y0 = self.path_location[i]
            x1, y1 = self.path_location[i+1]  # Tính toán x1, y1 trong vòng lặp

            d1 = np.sqrt((x1 - x0)**2 + (y1 - y0)**2)
            N1 = int(N * d1 / d)
            dt = 1.0 / (N1 - 1)
            
            for j in range(0, N1):
                t = j * dt
                x = x0 + (x1 - x0) * t
                y = y0 + (y1 - y0) * t

                self.cvs_map.delete(tk.ALL)
                self.load_map_image()
                self.ve_ban_do()
                self.cvs_map.create_line(self.path_location, fill='red')

                # Vẽ mũi tên tại các tọa độ chuyển động
                self.ve_mui_ten(y1 - y0, x1 - x0, x, y, '#FF0000')

                time.sleep(0.05)
                self.cvs_map.update()

                # Xóa mũi tên cũ sau khi vẽ
                self.ve_mui_ten(y1 - y0, x1 - x0, x, y, bg_color)

                # Vẽ mũi tên cuối cùng
                x0, y0 = self.path_location[-2]
                x1, y1 = self.path_location[-1]
                self.ve_mui_ten(y1 - y0, x1 - x0, x1, y1, '#FF0000')

    

    def ve_mui_ten(self, b, a, tx, ty, color):
        """Vẽ mũi tên chỉ hướng trên bản đồ"""
        p_mui_ten = [(0, 0, 1), (-20, 10, 1), (-15, 0, 1), (-20, -10, 1)]
        p_mui_ten_ma_tran = [np.array([[0], [0], [1]], np.float32),
                             np.array([[-20], [10], [1]], np.float32),
                             np.array([[-15], [0], [1]], np.float32),
                             np.array([[-20], [-10], [1]], np.float32)]

        M1 = np.array([[1, 0, tx], [0, 1, ty], [0, 0, 1]], np.float32)
        theta = np.arctan2(b, a)
        M2 = np.array([[np.cos(theta), -np.sin(theta), 0],
                       [np.sin(theta), np.cos(theta), 0],
                       [0, 0, 1]], np.float32)

        M = np.matmul(M1, M2)

        q_mui_ten = []
        for p in p_mui_ten_ma_tran:
            q = np.matmul(M, p)
            q_mui_ten.append((q[0, 0], q[1, 0]))

        self.cvs_map.create_polygon(q_mui_ten, fill=color, outline=color)


if __name__ == "__main__":
    app = App()
    app.mainloop()

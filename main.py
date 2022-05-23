import pygame
import random


# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (50, 51, 50)
ORANGE = (205, 162, 46)

rooms_quantity = 0
field_high = 0
field_width = 0
max_percent_difference = 0
min_high = 0
max_high = 0
min_width = 0
max_width = 0
min_relation = 0
max_relation = 0
pixel_high = 0
pixel_width = 0
INF = 10 ** 21


# read config from config_file.txt
def set_config():
    with open("config_file.txt", 'r') as config_file:
        config_arr = config_file.readlines()
    for line in config_arr:
        arr = line.split()
        if arr == []:
            continue
        a, b = arr[0], arr[1]
        if a == "ROOMS_QUANTITY":
            global rooms_quantity
            rooms_quantity = int(b)
        elif a == "FIELD_HIGH":
            global field_high
            field_high = int(b)
        elif a == "FIELD_WIDTH":
            global field_width
            field_width = int(b)
        elif a == "MAX_PERCENT_DIFFERENCE":
            global max_percent_difference
            max_percent_difference = int(b)
        elif a == "MIN_HIGH":
            global min_high
            min_high = int(b)
        elif a == "MAX_HIGH":
            global max_high
            max_high = int(b)
        elif a == "MIN_WIDTH":
            global min_width
            min_width = int(b)
        elif a == "MAX_WIDTH":
            global max_width
            max_width = int(b)
        elif a == "MIN_RELATION":
            global min_relation
            min_relation = float(b)
        elif a == "MAX_RELATION":
            global max_relation
            max_relation = float(b)
        elif a == "PIXEL_HIGH":
            global pixel_high
            pixel_high = int(b)
        elif a == "PIXEL_WIDTH":
            global pixel_width
            pixel_width = int(b)
        else:
            pass


# debug function
def print_config():
    print(rooms_quantity)
    print(field_high)
    print(field_width)
    print(max_percent_difference)
    print(min_high)
    print(max_high)
    print(min_width)
    print(max_width)
    print(min_relation)
    print(max_relation)
    print(pixel_width)
    print(pixel_high)


class Pixel:

    def __init__(self, pixel_type,
                 pixel_x, pixel_y):
        self.pixel_type = pixel_type
        self.x = pixel_x
        self.y = pixel_y

    def draw_pixel(self, screen):
        if self.pixel_type == "floor":
            COLOR = ORANGE
        elif self.pixel_type == "wall":
            COLOR = GRAY
        elif self.pixel_type == "decoration":
            COLOR = BLUE
        else:
            COLOR = GRAY

        pygame.draw.rect(screen, COLOR,
                         ((self.x * pixel_width), (self.y * pixel_high),
                          pixel_width, pixel_high))

    def change_type(self, new_type):
        self.pixel_type = new_type


class Plane:

    def __init__(self, high, width, x, y):
        self.high = high
        self.width = width
        self.x = x
        self.y = y
        self.room_width = 0
        self.room_high = 1
        self.room_x = 0
        self.room_y = 0

    def generate_room(self):
        cut_x = 2
        cut_y = 2
        if self.width - max_width > 3:
            cut_x = (self.width - max_high) // 2
        if self.high - max_high > 3:
            cut_y = (self.high - max_high) // 2

        self.x = self.x + cut_x
        self.width = self.width - 2 * cut_x
        self.y = self.y + cut_y
        self.high = self.high - 2 * cut_y

        min_w = min(self.width, min_width)
        min_h = min(self.high, min_high)
        max_w = min(self.width, max_width)
        max_h = min(self.high, max_high)

        emergency_stop = 0
        while ((self.room_width / self.room_high) < min_relation or
               (self.room_width / self.room_high) > max_relation):
            emergency_stop += 1
            if emergency_stop > 10 ** 3:
                self.room_high = 0
                self.room_width = 0
                self.room_y = 0
                self.room_x = 0
                break
            self.room_width = random.randint(min_w, max_w)
            self.room_high = random.randint(min_h, max_h)
            if self.room_high == 0:
                self.room_high = 0
                self.room_width = 0
                self.room_y = 0
                self.room_x = 0
                break

            self.room_x = random.randint(self.x, (self.x + self.width - self.room_width))
            self.room_y = random.randint(self.y, (self.y + self.high - self.room_high))

        self.y = self.y + cut_y
        self.high = self.high + 2 * cut_y
        self.x = self.x + cut_x
        self.width = self.width + 2 * cut_x

    def pixel_plane(self):
        array = []
        for i in range(self.room_x, self.room_x + self.room_width):
            for j in range(self.room_y, self.room_y + self.room_high):
                p = Pixel("floor", i, j)
                if (i > self.room_x) and (i < self.room_x + self.room_width - 1):
                    if (j > self.room_y) and (j < self.room_y + self.room_high - 1):
                        chance = random.randint(1, 100)
                        if chance > 99:
                            p.change_type("decoration")
                array.append(p)
        return array


def binary_splitting():
    all_n = 1
    planes = [Plane(field_high, field_width, 0, 0)]
    while True:
        n_now = all_n
        for q in range(n_now):
            plane = planes[0]
            red_line = random.randint(50 - max_percent_difference // 2, 50 + max_percent_difference // 2)

            if plane.high <= plane.width:
                a = plane.width
                a = a * red_line // 100
                planes.append(Plane(plane.high, a, plane.x, plane.y))
                planes.append(Plane(plane.high, plane.width - a, plane.x + a, plane.y))
            else:
                b = plane.high
                b = b * red_line // 100
                planes.append(Plane(b, plane.width, plane.x, plane.y))
                planes.append(Plane(plane.high - b, plane.width, plane.x, plane.y + b))

            planes = planes[1:]
            all_n += 1
            if all_n == rooms_quantity:
                return planes


def find_distance(p1, p2):
    distance = ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** 0.5
    return distance


def connect(a, b):
    arr_ = []
    if a.x < b.x:
        remember_h = 0
        for h in range(b.x - a.x):
            p = Pixel("floor", a.x + h, a.y)
            arr_.append(p)
            remember_h = h
        if a.y < b.y:
            for w in range(b.y - a.y + 1):
                p = Pixel("floor", a.x + remember_h, a.y + w)
                arr_.append(p)
        if a.y > b.y:
            for w in range(a.y - b.y + 1):
                p = Pixel("floor", a.x + remember_h, a.y - w)
                arr_.append(p)

    if a.x > b.x:
        remember_h = 0
        for h in range(a.x - b.x):
            p = Pixel("floor", a.x - h, a.y)
            arr_.append(p)
            remember_h = h
        if a.y < b.y:
            for w in range(b.y - a.y + 1):
                p = Pixel("floor", a.x - remember_h, a.y + w)
                arr_.append(p)
        if a.y > b.y:
            for w in range(a.y - b.y + 1):
                p = Pixel("floor", a.x - remember_h, a.y - w)
                arr_.append(p)

    # pygame.draw.line(screen, ORANGE,
    #                  [(a.x * pixel_width), (a.y * pixel_high)],
    #                  [(b.x * pixel_width), (b.y * pixel_high)])
    return arr_


def make_hallways(array):
    centres_array = []
    for pl in array:
        p = Pixel("center", pl.room_x + pl.room_width // 2,
                  pl.room_y + pl.room_high // 2)
        centres_array.append(p)

    adjacency_matrix = [[0 for i in range(len(centres_array))] for j in range(len(centres_array))]

    for p1 in range(len(centres_array)):
        up_neighbour = -1
        down_neighbour = -1
        left_neighbour = -1
        right_neighbour = -1
        up_dis = INF
        down_dis = INF
        left_dis = INF
        right_dis = INF
        for p2 in range(len(centres_array)):
            distance = find_distance(centres_array[p1], centres_array[p2])
            if (distance < up_dis) and (centres_array[p1].y < centres_array[p2].y):
                up_dis = distance
                up_neighbour = p2
            if (distance < down_dis) and (centres_array[p1].y > centres_array[p2].y):
                down_dis = distance
                down_neighbour = p2
            if (distance < right_dis) and (centres_array[p1].x < centres_array[p2].x):
                right_dis = distance
                right_neighbour = p2
            if (distance < left_dis) and (centres_array[p1].x > centres_array[p2].x):
                left_dis = distance
                left_neighbour = p2
        if up_neighbour != -1:
            if adjacency_matrix[up_neighbour][p1] != 1:
                adjacency_matrix[p1][up_neighbour] = 1
            # adjacency_matrix[up_neighbour][p1] = 1
        elif down_neighbour != -1:
            if adjacency_matrix[down_neighbour][p1] != 1:
                adjacency_matrix[p1][down_neighbour] = 1
            # adjacency_matrix[down_neighbour][p1] = 1
        elif right_neighbour != -1:
            if adjacency_matrix[right_neighbour][p1] != 1:
                adjacency_matrix[p1][right_neighbour] = 1
            # adjacency_matrix[right_neighbour][p1] = 1
        elif left_neighbour != -1:
            if adjacency_matrix[left_neighbour][p1] != 1:
                adjacency_matrix[p1][left_neighbour] = 1
            # adjacency_matrix[left_neighbour][p1] = 1

    # for i in range(len(centres_array)):
    #     is_del = 0
    #     for j in range(len(centres_array)):
    #         is_del += adjacency_matrix[i][j]
    #     if is_del == 0:
    #         black_list.append(i)

    res = []
    for i in range(len(centres_array)):
        for j in range(len(centres_array)):
            if adjacency_matrix[i][j] == 1:
                if (centres_array[i].x != 0 or centres_array[i].y != 0) and (centres_array[j].x != 0 or centres_array[j].y != 0):
                    res_ = connect(centres_array[i], centres_array[j])
                    for v in range(len(res_)):
                        res.append(res_[v])
    return res


if __name__ == '__main__':
    set_config()

    WIDTH = field_width * pixel_width
    HIGH = field_high * pixel_high
    FPS = 30

    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HIGH))
    screen.fill(GRAY)
    pygame.display.set_caption("Dungeon_visualization_ver2")
    clock = pygame.time.Clock()

    field = binary_splitting()
    for i in range(len(field)):
        field[i].generate_room()
    pixel_arr = []
    for i in range(len(field)):
        arr = field[i].pixel_plane()
        for j in range(len(arr)):
            pixel_arr.append(arr[j])
    halls = make_hallways(field)
    for i in range(len(halls)):
        pixel_arr.append(halls[i])

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            for i in range(len(pixel_arr)):
                pixel_arr[i].draw_pixel(screen)
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F5:
                    screen.fill(GRAY)
                    field = binary_splitting()
                    for i in range(len(field)):
                        field[i].generate_room()
                    halls = make_hallways(field)
                    pixel_arr = []
                    for i in range(len(field)):
                        arr = field[i].pixel_plane()
                        for j in range(len(arr)):
                            pixel_arr.append(arr[j])
                    for i in range(len(halls)):
                        pixel_arr.append(halls[i])
                elif event.key == pygame.K_ESCAPE:
                    running = False
            pygame.display.flip()
            pygame.display.update()

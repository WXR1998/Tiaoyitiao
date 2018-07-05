import os
import time
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import random
import math

FILENAME = 'autojump.png'
time_coeff = 1.392
PLAYER_COLOR = np.array([56, 57, 98, 255])
HEIGHT = 1920
WIDTH = 1080
HEIGHT_BIAS = -19
WIDTH_BIAS = -6

def get_screenshot(filename = FILENAME):
    if filename[-4:] != '.png':
        filename += '.png'
    os.system(
        'cd ../dependency/platform-tools-windows/ && adb.exe shell screencap -p /sdcard/{}'.format(filename))
    os.system(
        'cd ../dependency/platform-tools-windows/ && adb.exe pull /sdcard/{} ../../src/'.format(filename))

def press_screen(distance):
    press_time = int(distance * time_coeff)
    x, y = random.randint(500, WIDTH - 200), random.randint(1200, HEIGHT - 400)
    os.system('cd ../dependency/platform-tools-windows/ && adb.exe shell input swipe {} {} {} {} '.
            format(x, y, x + random.randint(-10, 10), y + random.randint(-20, 20)) + str(press_time))

def color_distance(cola, colb = [0, 0, 0, 0]):
    return abs(int(cola[0]) - int(colb[0])) + abs(int(cola[1]) - int(colb[1])) + abs(int(cola[2]) - int(colb[2]))

def distance(posa, posb):
    return int(math.sqrt((posa[0] - posb[0]) ** 2 + (posa[1] - posb[1]) ** 2))

def get_player_pos(im):
    cur_x = 0
    cur_y = 0
    for i in range(800, 1300):
        for j in range(100, 1000):
            if color_distance(im[i][j], PLAYER_COLOR) < 10:
                cur_x = i
                cur_y = j
    return cur_x + HEIGHT_BIAS, cur_y + WIDTH_BIAS

#delete
def set_color(im, pos, color = [255, 0, 255], ran = 2):
    '''
    将pos处设置成color色
    '''
    if len(color) == 3:
        color.append(255)
    for i in range(-ran, ran+1):
        for j in range(-ran, ran+1):
            im[pos[0] + i][pos[1] + j] = color

def get_right_corner(im, pos):
    '''
    pos位置为背景 沿着它走可以获得背景最右点
    '''
    def right(p):
        return (p[0], p[1] + 1)
    def down(p):
        return (p[0] + 1, p[1])
    def rightdown(p):
        return (p[0] + 1, p[1] + 1)
    def leftdown(p):
        return (p[0] + 1, p[1] - 1)
    def get_color(p):
        return im[p[0]][p[1]]
    def is_background(nowcolor, newcolor):
        '''
        由于背景色渐变 根据当前点的颜色判断新点的颜色是否属于背景色
        '''
        if color_distance(nowcolor, newcolor) < 3:
            return True

    now = pos[:]
    downwalking_count = 0
    while True:
        try:
            if is_background(get_color(now), get_color(leftdown(now))) and now != pos:
                return now
            elif is_background(get_color(now), get_color(down(now))):
                downwalking_count += 1
                if downwalking_count >= 3:
                    return now
                else:
                    now = down(now)
            elif is_background(get_color(now), get_color(rightdown(now))):
                downwalking_count = 0
                now = rightdown(now)
            elif is_background(get_color(now), get_color(right(now))):
                downwalking_count = 0
                now = right(now)
            else:
                return now
        except:
            return now

def get_center_pos(im, onleft):
    if onleft == False:
        jrange = range(200, 540)
        jranger = range(540, 200, -1)
    else:
        jrange = range(541, 880)
        jranger = range(880, 541, -1)
    flag = False
    for i in range(600, 1000):
        for j in jrange:
            if color_distance(im[i][j].astype(np.int16) - im[i - 1][j].astype(np.int16)) > 30:
                top_color = im[i][j]
                top_pos = (i, j)
                background_pos = (i - 1, j)
                flag = True
                break
        if flag:
            break
    flag = False
    for i in range(600, 1000):
        for j in jranger:
            if color_distance(im[i][j].astype(np.int16) - im[i - 1][j].astype(np.int16)) > 30:
                top_posr = (i, j)
                flag = True
                break
        if flag:
            break
    top_pos = (top_pos[0], (top_pos[1] + top_posr[1]) // 2)
    right_corner_pos = get_right_corner(im, background_pos)
    return right_corner_pos[0], top_pos[1]

#delete
def replace_color(im, color, dis = 10):
    '''
    将所有color色全部变成白色
    '''
    cur_x = 0
    cur_y = 0
    for i in range(900, 1300):
        for j in range(200, 900):
            if color_distance(im[i][j], color) < dis:
                im[i][j] = [255, 255, 255, 255]

#delete
def show_image(im):
    img = Image.fromarray(im)

    plt.figure("Screen Shot")
    plt.imshow(img)
    plt.axis('on')
    plt.show()

def jumper():
    get_screenshot()
    im = np.array(Image.open(FILENAME))
    player_pos = get_player_pos(im)
    target_pos = get_center_pos(im, player_pos[1] < 540)
    return int(distance(player_pos, target_pos) * time_coeff)

def main():
    steps = 0
    while True:
        steps += 1
        print('[Step ' + str(steps) + ']')
        get_screenshot(str(steps) + '.png')
        im = np.array(Image.open(str(steps) + '.png'))
        height, width, channel = im.shape
        player_pos = get_player_pos(im)
        #set_color(im, player_pos)
        target_pos = get_center_pos(im, player_pos[1] < 540)
        #set_color(im, target_pos)
        #set_color(im, player_pos)
        #show_image(im)
        #break
        press_screen(distance(player_pos, target_pos))
        #break
        time.sleep(random.randint(1500, 2000) / 1000)

if __name__ == '__main__':
    main()

import os, time, random, math
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

time_coeff = 1.392
PCOL = np.array([56, 57, 98, 255])
CENTER_COLOR = np.array([245, 245, 245, 255])

def get_screenshot(filename = 'autojump.png'):
    os.system(
        'cd ../dependency/platform-tools-windows/ && adb.exe shell screencap -p /sdcard/{}'.format(filename))
    os.system(
        'cd ../dependency/platform-tools-windows/ && adb.exe pull /sdcard/{} ../../src/'.format(filename))

def press_screen(dis):
    press_time = int(dis * time_coeff)
    os.system('cd ../dependency/platform-tools-windows/ && adb.exe shell input swipe 500 1600 500 1602 ' + str(press_time))

def cdis(a, b = [0, 0, 0, 0]):
    return  abs(int(a[0]) - int(b[0])) + \
            abs(int(a[1]) - int(b[1])) + \
            abs(int(a[2]) - int(b[2]))

def dis(a, b):
    ans = int(math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2))
    if ans > 250:
        ans = ans * 0.934 + 32.33
    return ans

def get_ppos(im):
    cur_x = 0
    cur_y = 0
    for i in range(800, 1300):
        for j in range(100, 1080 - 100):
            if cdis(im[i][j], PCOL) < 10:
                cur_x = i
                cur_y = j
    return cur_x - 20, cur_y - 5

def set_pos_color(im, pos, col = [255, 0, 255]):
    if len(col) == 3:
        col.append(255)
    for i in range(-2, 3):
        for j in range(-2, 3):
            im[pos[0] + i][pos[1] + j] = col

def show_image(im):
    img = Image.fromarray(im)

    plt.figure("Screen Shot")
    plt.imshow(img)
    plt.axis('on')
    plt.show()

DIR = ((1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0))

def get_cpos(im, onleft):
    def down(pos, d):
        return [pos[0] + d, pos[1]]
    def right(pos, d):
        return [pos[0], pos[1] + d]
    SWEEPER_WIDTH = 10
    def activate(p, q):
        if p > 10 and q > 15:
            return 255
        return 0
    def filter(im):
        ans = np.zeros(im.shape[:2], np.uint8)
        for i in range(im.shape[0]):
            for j in range(im.shape[1]):
                if im[i][j] != 255:
                    continue
                dir_cnt = 0
                for dir in DIR:
                    ti = i + dir[0]
                    tj = j + dir[1]
                    if ti >= 0 and ti < im.shape[0] and tj >= 0 and tj < im.shape[1]:
                        if im[ti][tj] == 255:
                            dir_cnt += 1
                if dir_cnt >= 5:
                    ans[i][j] = 255
        return ans

    if onleft == False:
        jrange = range(200, 540)
        jranger = range(540, 200, -1)
    else:
        jrange = range(541, 880)
        jranger = range(880, 541, -1)
    flag = False
    for i in range(600, 1000):
        for j in jrange:
            if cdis(im[i][j].astype(np.int16) - im[i - 1][j].astype(np.int16)) > 30:
                top_color = im[i][j]
                toppos = [i, j]
                flag = True
                break
        if flag:
            break
    flag = False
    for i in range(600, 1000):
        for j in jranger:
            if cdis(im[i][j].astype(np.int16) - im[i - 1][j].astype(np.int16)) > 30:
                topposr = [i, j]
                flag = True
                break
        if flag:
            break
    toppos[1] = (toppos[1] + topposr[1]) // 2

    for i in range(toppos[0], toppos[0] + 200):
        if cdis(im[i][toppos[1]], CENTER_COLOR) == 0:
            return (i + 10, toppos[1])
    #for i in range(toppos[0], toppos[0] + 200):
    #    print(i, im[i][toppos[1]])
    #set_pos_color(im, down(toppos, 917 - toppos[0]))
    #show_image(im)

    imx = im[toppos[0] : toppos[0] + 450, toppos[1] - min(300, toppos[1]) : toppos[1] + min(300, 1080 - toppos[1])].astype(np.int16)
    imy = np.zeros(imx.shape[:2], np.uint8)
    for i in range(imx.shape[0]):
        for j in range(imx.shape[1]):
            dir_cnt = 0
            col = np.zeros(4)
            for dir in DIR:
                ti = i + dir[0]
                tj = j + dir[1]
                if ti >= 0 and ti < imx.shape[0] and tj >= 0 and tj < imx.shape[1]:
                    dir_cnt += 1
                    col += imx[ti][tj]
            if dir_cnt == 0:
                continue
            tmp = col / dir_cnt - imx[i][j]
            if imx[i][j][0] > 220 and imx[i][j][1] > 220 and imx[i][j][2] > 220:
                imy[i][j] = 0
            else:
                imy[i][j] = activate(max(abs(tmp[0]), abs(tmp[1]), abs(tmp[2])), abs(tmp[0]) + abs(tmp[1]) + abs(tmp[2]))
    imz = filter(imy)
    tpy = min(300, toppos[1])
    for i in range(imz.shape[0]):
        flag = False
        for j in range(-SWEEPER_WIDTH + tpy, SWEEPER_WIDTH + 1 + tpy):
            if imz[i][j] == 255 and i > 30:
                flag = True
        if flag:
            center = i // 2
            break
    try:
        imz[center][tpy] = 125
    except:
        print('center missing')
        center = 80

    return toppos[0] + center, toppos[1] - min(300, toppos[1]) + tpy

def jumper():
    get_screenshot()
    im = np.array(Image.open('autojump.png'))
    height, width, channel = im.shape
    ppos = get_ppos(im)
    cpos = get_cpos(im, ppos[1] < 540)
    return int(dis(ppos, cpos) * time_coeff)

def main():
    cnt = 0
    while True:
        cnt += 1
        get_screenshot()
        get_screenshot(str(cnt) + '.png')
        im = np.array(Image.open('autojump.png'))
        height, width, channel = im.shape
        ppos = get_ppos(im)
        #set_color(im, ppos)
        cpos = get_cpos(im, ppos[1] < 540)
        #set_color(im, cpos)
        press_screen(dis(ppos, cpos))
        time.sleep(2)

if __name__ == '__main__':
    main()

import cv2
import glob
import re
import numpy as np
import csv


def extract_numbers_from_string(s):
    # 正規表現を用いて、"画像"と".png"の間にある数字部分を抽出
    num_str = re.search("画像(\d+)", s).group(1)
    return int(num_str)


def imread(filename, g=1, flags=cv2.IMREAD_COLOR, dtype=np.uint8):
    try:
        n = np.fromfile(filename, dtype)
        img = cv2.imdecode(n, flags)
        if g == 0:
            img_g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            return img_g
        elif g < 0:
            img_g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, img_bi = cv2.threshold(img_g, 100, 255, cv2.THRESH_BINARY)
            return img_bi
        else:
            return img
    except Exception as e:
        print(e)
        return None


def export_result(res):
    res = res.T
    headers = [str(i * 100) for i in range(res.shape[1])]

    with open("result.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in res:
            writer.writerow(row)


class Manager:
    def __init__(self):
        img_paths = glob.glob("0-6300/*.png")
        self.img_paths_sorted = sorted(img_paths, key=extract_numbers_from_string)
        self.res = np.zeros((len(self.img_paths_sorted), 100), dtype=np.uint8)
        self.img = imread(self.img_paths_sorted[0])
        self.h = self.img.shape[0] // 10
        self.w = self.img.shape[1] // 10
        self.interval = 10
        self.page = 0
        self.row = 0
        self.col = 0
        cv2.namedWindow("image", cv2.WINDOW_NORMAL)

    def move_page(self, direction):
        if direction < 0:
            self.page = max(0, self.page + direction)
        else:
            self.page = min(len(self.img_paths_sorted) - 1, self.page + direction)
        self.img = imread(self.img_paths_sorted[self.page])
        self.row = 0
        self.col = 0
        print(f"index: {self.page * 100 + self.row * 10}")

    def move_row(self, direction):
        if direction < 0:
            self.row = max(0, self.row + direction)
        else:
            self.row = min(9, self.row + direction)
        self.col = 0
        print(f"index: {self.page * 100 + self.row * 10}")

    def run(self):
        while True:
            img_crop = self.img[self.row * self.h:(self.row + 1) * self.h]
            cv2.rectangle(img_crop, (self.col * self.w, 0), ((self.col + 1) * self.w, self.h), (0, 0, 255), 3)
            cv2.imshow("image", img_crop)
            key = cv2.waitKey(self.interval)
            if key == ord("q") or key == 27:
                export_result(self.res)
                cv2.destroyAllWindows()
                break
            elif key == ord("a"):
                self.move_page(-1)
            elif key == ord("d"):
                self.move_page(1)
            elif key == ord("w"):
                self.move_row(-1)
            elif key == ord("s"):
                self.move_row(1)
            # 1~5の数字キーが押されたら、その数字をresに記録
            elif ord("1") <= key <= ord("5"):
                score = key - ord("0")
                self.res[self.page, self.row * 10 + self.col] = score
                cv2.putText(img_crop, str(score), ((self.col + 1) * self.w - self.w * 2 // 3, self.h - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                self.col += 1
                if self.col >= 10:
                    self.row += 1
                    self.col = 0
                    if self.row >= 10:
                        self.page += 1
                        if self.page == len(self.img_paths_sorted):
                            export_result(self.res)
                            cv2.destroyAllWindows()
                            break
                        self.img = imread(self.img_paths_sorted[self.page])
                        self.row = 0
                    print(f"index: {self.page * 100 + self.row * 10}")
            # backspaceキーが押されたら、resの値を0に戻す
            elif key == 8:
                self.res[self.page, self.row * 10 + self.col] = 0
                self.col -= 1
                if self.col < 0:
                    self.row -= 1
                    self.col = 9
                    if self.row < 0:
                        self.page -= 1
                        if self.page < 0:
                            self.page = 0
                            self.row = 0
                            self.col = 0
                        else:
                            self.img = imread(self.img_paths_sorted[self.page])
                            self.row = 9
                    print(f"index: {self.page * 100 + self.row * 10}")


def main():
    manager = Manager()
    manager.run()


if __name__ == "__main__":
    main()

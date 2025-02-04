import imgaug as ia
from imgaug import augmenters as iaa
import numpy as np
import cv2
import os
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage

GENERATE_COUNT  = 1 #증폭 이미지 배수 (5배수로)
# 이미지와 라벨 파일 경로 설정
image_folder = "C:/miniproj_yolov5/3.develop/datasets/images/"
images_dest_folder = "C:/miniproj_yolov5/3.develop/datasets/images_new/"
labels_dest_folder = "C:/miniproj_yolov5/3.develop/datasets/images_new/"

def read_yolo_format(file_path, image_shape):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    boxes = []
    for line in lines:
        class_id, x_center, y_center, width, height = map(float, line.split())
        x1 = int((x_center - width / 2) * image_shape[1])
        y1 = int((y_center - height / 2) * image_shape[0])
        x2 = int((x_center + width / 2) * image_shape[1])
        y2 = int((y_center + height / 2) * image_shape[0])
        boxes.append(BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2, label=class_id))
    return BoundingBoxesOnImage(boxes, shape=image_shape)

# 증폭 정책 설정
seq = iaa.Sequential([
    # iaa.SomeOf((0, 8), [
    #     iaa.Affine(rotate=(-25, 25), scale=(0.8, 1.2)),
    #     iaa.Fliplr(0.5),
    #     iaa.Sometimes(
    #         0.5,
    #         iaa.GaussianBlur(sigma=(0, 0.5))),
    #     iaa.AdditiveGaussianNoise(loc=0, scale=(0.0, 0.05*255), per_channel=0.5),
    #     iaa.Multiply((0.8, 1.2)),
    #     iaa.LinearContrast((0.8, 1.3)),
    #     iaa.Crop(percent=(0, 0.1)),
    #     iaa.Pad(percent=(0, 0.1), pad_mode="edge"),
    #     iaa.Affine(
    #     scale={"x": (0.8, 1.2), "y": (0.8, 1.2)},
    #     translate_percent={"x": (-0.2, 0.2), "y": (-0.2, 0.2)},
    #     rotate=(-25, 25),
    #     shear=(-8, 8)
    #     )
    # ], random_order=True)
])

# 이미지 파일 목록 가져오기
image_files = [f for f in os.listdir(image_folder) if f.endswith('.jpg')]

# 증폭 및 저장
for image_file in image_files:
    # 이미지와 라벨 파일 경로
    image_path = os.path.join(image_folder, image_file)
    label_path = os.path.join(image_folder, image_file.replace('.jpg', '.txt'))

    # 이미지와 라벨 읽기
    image = cv2.imread(image_path)
    image_bbs = read_yolo_format(label_path, image.shape)
    
    for i in range(GENERATE_COUNT):

        # 이미지 증폭
        image_aug, bbs_aug = seq(image=image, bounding_boxes=image_bbs)
        image_aug = bbs_aug.draw_on_image(image_aug, size=2) # 바운드박스를 이미지 내에 그림(테스트용)
        
        new_image_file = f"{image_file.split('.')[0]}_{i+1}.jpg"
        new_label_file = f"{image_file.replace('.jpg', '')}_{i+1}.txt"

        # 증폭된 이미지와 라벨 저장
        cv2.imwrite(os.path.join(images_dest_folder, new_image_file), image_aug)
        with open(os.path.join(labels_dest_folder, new_label_file), 'w') as file:
            for bb in bbs_aug.bounding_boxes:
                x_center = (bb.x1 + bb.x2) / 2 / image_aug.shape[1]
                y_center = (bb.y1 + bb.y2) / 2 / image_aug.shape[0]
                width = (bb.x2 - bb.x1) / image_aug.shape[1]
                height = (bb.y2 - bb.y1) / image_aug.shape[0]
                file.write(f"{int(bb.label)} {x_center} {y_center} {width} {height}\n")
print("파일 저장 완료")
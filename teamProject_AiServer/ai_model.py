'''
도면 이미지에서 객체를 추출하는 부분!
도면의 이미지를 넣어주면, 도면의 객체를 분류하고 각각 분류된 좌표값을 JSON 형식으로 보내준다.

__init__() : 모델을 불러온다

def get_image(self) : 이미지의 경로를 폴더단위로 넘겼을 때 test_image_list[]에 정렬하여 저장

def predict_image(self): 이미지 파일로 PREDICT 수행, 좌표값을 받는다

def get_point(self): 받은 좌표값을 필터링 하여 Blender에게 넘겨줄 수 있는 딕셔너리 형식으로 추출


class get_polygon: 사용자가 모델의 경로와, 이미지의 경로를 넣어주면 최종적인 json 파일 형식으로 추출 가능

'''

import ultralytics
from ultralytics import YOLO
from glob import glob
import numpy as np
import json
import torch

import cv2
import pytesseract
from pytesseract import Output
from PIL import Image
import asyncio
from concurrent.futures import ThreadPoolExecutor

pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'


# input(모델 경로) return 모델
def model_load(model_path):

    ultralytics.checks()
    model = YOLO(model_path)

    return model


# input(모델 경로, 이미지 경로) -> 좌표 리스트
def get_img_pointList(model_path, img_path):
    model = model_load(model_path)

    result = model.predict(source=img_path, save=True)
    seg_point = result[0].masks.xy

    seg_point_list = []
    for point in seg_point:
        if isinstance(point, torch.Tensor):
            point = point.cpu().detach().numpy()
        seg_point_list.append(point.tolist())

    return seg_point_list


# input(좌표 리스트) -> 좌표 딕셔너리
def list_to_dict(seg_point_list):
    seg_point_dict = {}

    for i in range(0, len(seg_point_list) - 1):
        np.set_printoptions(precision=2)
        poligon = seg_point_list[i]
        seg_point_dict["polygon{}".format(i)] = poligon

    return seg_point_dict


# input(좌표 딕셔너리) -> JSON 파일
def dict_to_json(json_output_path, seg_point_dict):
    with open(json_output_path, 'w') as json_file:
        json.dump(seg_point_dict, json_file)

    return json_output_path


# 좌표를 넘겨주면 이미지에서 핸당하는 부분으 추출하여 전달
def extract_region_from_coordinates(original_image, coordinates):
    # 좌표를 numpy 배열로 변환
    coordinates_np = np.array(coordinates, dtype=np.int32)

    # 좌표를 감싸는 최소 사각형을 얻기
    rect = cv2.boundingRect(coordinates_np)

    # 이미지에서 해당 부분을 추출
    extracted_region = original_image[rect[1]:rect[1] + rect[3], rect[0]:rect[0] + rect[2]]

    return extracted_region


# 마스크 부분의 text 얻어내기
def ocr_text(list, img_path):
    original_image = cv2.imread(img_path)  # 원본 이미지 로드
    coordinates = list

    # 이미지 부분 추출
    extracted_region = extract_region_from_coordinates(original_image, coordinates)

    # 한국어가 없을 때 영어가 있는지 확인
    result = pytesseract.image_to_string(extracted_region, lang='kor+eng')

    return result


def get_img_textDict(seg_point_list, img_paht):
    ouput_txt = {}
    temp = {}
    for i in range(len(seg_point_list) - 1):
        text = ocr_text(seg_point_list[i], img_paht)
        temp["name"] = text
        temp["info"] = {}
        ouput_txt["polygon{}".format(i)] = temp

    return ouput_txt


model_path = "a"
image_path = "b"

point_json_path = "c"
text_json_path = "d"


# json 저장 경로 반환
def predict(model_path, image_path, point_json_path, text_json_path):
    # 모델 추출 좌표 리스트
    seg_point_list = get_img_pointList(model_path, image_path)

    # 모델 추출 좌표 딕셔너리
    seg_point_dict = list_to_dict(seg_point_list)

    seg_text_dict = get_img_textDict(seg_point_list, image_path)

    # json 저장 경로
    json_point_path = dict_to_json(point_json_path, seg_point_dict)

    json_text_path = dict_to_json(text_json_path, seg_text_dict)

    json_path = [json_point_path, json_text_path]

    return json_path
async def async_pointdata(model_dir, image, point_json_path, text_json_path):
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, predict, model_dir, image, point_json_path, text_json_path)
    return result


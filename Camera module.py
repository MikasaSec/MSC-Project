import face_recognition

import cv2
from datetime import datetime, timedelta
import numpy as np
import platform
import pickle


USING_RPI_CAMERA_MODULE = True

# 已知的人脸编码列表和关于每个人脸的元数据的匹配列表。
known_face_encodings = []
known_face_metadata = []


def save_known_faces():
    with open("known_faces.dat", "wb") as face_data_file:
        face_data = [known_face_encodings, known_face_metadata]
        pickle.dump(face_data, face_data_file)
        print("Known faces backed up to disk.")


def load_known_faces():
    global known_face_encodings, known_face_metadata

    try:
        with open("known_faces.dat", "rb") as face_data_file:
            known_face_encodings, known_face_metadata = pickle.load(face_data_file)
            print("Known faces loaded.")
    except FileNotFoundError as e:
        print("No previous face data found - starting with a blank known face list.")
        pass


def get_jetson_gstreamer_source(capture_width=1280, capture_height=720, display_width=1280, display_height=720, framerate=30, flip_method=0):
    """
    返回一个与OpenCV兼容的视频源描述，该描述使用gstreamer从Jetson Nano上的RPI摄像头捕捉视频。 有问题！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
    """
    return (
            f'nvarguscamerasrc ! video/x-raw(memory:NVMM), ' +
            f'width=(int){capture_width}, height=(int){capture_height}, ' +
            f'format=(string)NV12, framerate=(fraction){framerate}/1 ! ' +
            f'nvvidconv flip-method={flip_method} ! ' +
            f'video/x-raw, width=(int){display_width}, height=(int){display_height}, format=(string)BGRx ! ' +
            'videoconvert ! video/x-raw, format=(string)BGR ! appsink'
            )


def register_new_face(face_encoding, face_image):
    """
    在我们已知的面孔名单中增加一个新的人
    """
    # 将人脸编码添加到已知人脸列表中
    known_face_encodings.append(face_encoding)
    # 添加一个匹配的字典条目。
    # 我们可以用它来记录一个人访问过多少次，我们最后一次见到他们是什么时候
    known_face_metadata.append({
        "first_seen": datetime.now(),
        "first_seen_this_interaction": datetime.now(),
        "last_seen": datetime.now(),
        "seen_count": 1,
        "seen_frames": 1,
        "face_image": face_image,
    })


def lookup_known_face(face_encoding):
    """
    看看这是否是我们的脸谱列表中已有的脸谱
    """
    metadata = None

    # 如果我们的已知面孔列表是空的，就什么也不返回，因为我们不可能看到这张脸。
    if len(known_face_encodings) == 0:
        return metadata

    # 计算未知面孔与我们已知面孔列表中的每张面孔之间的距离。
    # 这将为每张已知的脸返回一个介于0.0和1.0之间的浮点数字。这个数字越小、
    # 就说明该脸与未知脸的相似度越高。
    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

    # Get the known face that had the lowest distance (i.e. most similar) from the unknown face.
    best_match_index = np.argmin(face_distances)

    # 如果距离最低的那张脸的距离低于0.6，我们就认为它是脸部匹配。
    # 0.6来自于人脸识别模型的训练方式。它被训练来确保
    # 彼此之间的距离总是小于0.6。
    # 在这里，我们将阈值放宽了一点，变成了0.65，因为不太可能有两个非常相似的
    # 人会同时出现在门前。
    if face_distances[best_match_index] < 0.65:
        # If we have a match, look up the metadata we've saved for it (like the first time we saw it, etc)
        metadata = known_face_metadata[best_match_index]

        # Update the metadata for the face so we can keep track of how recently we have seen this face.
        metadata["last_seen"] = datetime.now()
        metadata["seen_frames"] += 1

        # 我们也会保留一个总的 "见过次数"，跟踪这个人上门的次数。
        # 但我们可以说，如果我们在过去5分钟内见过这个人，这仍然是同一个
        # 访问，而不是新的访问。但是如果他们离开一段时间后又回来了，那就是一次新的访问。
        if datetime.now() - metadata["first_seen_this_interaction"] > timedelta(minutes=5):
            metadata["first_seen_this_interaction"] = datetime.now()
            metadata["seen_count"] += 1

    return metadata



import numpy as np
from PIL import Image
import torch
from feature_extraction.super_feature_extraction_utils.emotion_recognition.vgg import VGG
import feature_extraction.super_feature_extraction_utils.emotion_recognition.transforms as transforms
import cv2 as cv

cut_size = 44

transform_test = transforms.Compose([
    transforms.TenCrop(cut_size),
    transforms.Lambda(lambda crops: torch.stack([transforms.ToTensor()(crop) for crop in crops])),
])

net = VGG('VGG19')
checkpoint = torch.load('feature_extraction/super_feature_extraction_utils/emotion_recognition/PrivateTest_model.t7', map_location=torch.device('cpu'))
net.load_state_dict(checkpoint['net'])

def classify_emotion(img):
    g_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    g_img = cv.resize(g_img, (48, 48)).astype(np.uint8)
    new_img = g_img[:, :, np.newaxis]
    new_img = np.concatenate((new_img, new_img, new_img), axis=2)
    new_img = Image.fromarray(new_img)
    inputs = transform_test(new_img)
    ncrops, c, h, w = np.shape(inputs)

    inputs = inputs.view(-1, c, h, w)
    with torch.no_grad():
        outputs = net(inputs)

    outputs_avg = outputs.view(ncrops, -1).mean(0)

    _, predicted = torch.max(outputs_avg.data, 0)

    return predicted

# """
# 查看tiff图
# """
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from torchvision import transforms
from torchvision.transforms.functional import to_pil_image

image = Image.open("C:/Users/dell/Desktop/nii_rgb_image2.tiff")
print(np.array(image).shape)
# print("Image mode:", image.mode)
# image = image.convert("RGB")
# print("Image mode:", image.mode)
# # print(np.array(image).shape)
# transforms_image = transforms.Compose([
#     transforms.Resize((1024,1024)),
#     transforms.ToTensor()   # [H, W, C] -> [C, H, W], 并归一化到[0,1]
#         ])
# image = transforms_image(image)  # [0,1],[C,H,W] float32
# image_pil = to_pil_image(image)  # 注意必须是 [C, H, W] 且在 [0, 1]
# # 保存
# image_pil.save("C:/Users/dell/Desktop/input_image.tiff")

# image.save("C:/Users/dell/Desktop/try_image.tiff")
# plt.imshow(img, cmap="gray")
# plt.axis('off')
# plt.title("TIFF_RGB Image")
# plt.show()

# """
# RGB
# """
# from PIL import Image
# import numpy as np
# import torch
# from torchvision import transforms
#
# # 加载三张灰度图（.tiff 格式）
# img1 = Image.open("C:/Users/dell/Desktop/newdataset/images/p_0/34.tiff")  # L = grayscale
# img2 = Image.open("C:/Users/dell/Desktop/newdataset/images/p_0/34.tiff")
# img3 = Image.open("C:/Users/dell/Desktop/newdataset/images/p_0/34.tiff")
#
# # Resize（可选）+ ToTensor（转为 [C, H, W]，但灰度图仍是 [1, H, W]）
# transform = transforms.Compose([
#     transforms.Resize((1024, 1024)),
#     transforms.ToTensor()  # 转为 [1, H, W]，值归一化到[0,1]
# ])
#
# t1 = transform(img1).squeeze(0)  # 去掉 channel 维，变为 [H, W]
# t2 = transform(img2).squeeze(0)
# t3 = transform(img3).squeeze(0)
#
# # 堆叠成 [3, H, W]
# stacked = torch.stack([t1, t2, t3], dim=0)  # shape: [3, 1024, 1024]
# # 转为 NumPy（[3, H, W]）→ [H, W, 3]，并反归一化
# stacked_np = (stacked.numpy().transpose(1, 2, 0) * 255).astype(np.uint8)
#
# # 保存为 TIFF
# Image.fromarray(stacked_np).save("C:/Users/dell/Desktop/stacked3.tiff")


# # tiff调窗宽窗位
# from PIL import Image
# import numpy as np
# def window_image(img, window_center, window_width):
#     img = img.astype(np.float32)
#     img = (img - (window_center - window_width / 2)) / window_width
#     img = np.clip(img, 0, 1)
#     img = (img * 255).astype(np.uint8)
#     return img
# image = Image.open("C:/Users/dell/Desktop/rgb.tiff")
# img_np= np.array(image)
# window_center = 40
# window_width = 350
# img_windowed = window_image(img_np, window_center, window_width)
#
# # 4. 保存结果
# Image.fromarray(img_windowed).save("C:/Users/dell/Desktop/rgbnew.tiff")
#

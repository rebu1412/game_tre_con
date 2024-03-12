import cv2
import numpy as np
import os

# Đường dẫn đến thư mục chứa ảnh
folder_path = 'C:/Users/Computer/Downloads/Z2/'

# Tải tất cả tệp ảnh trong thư mục
image_files = [f for f in os.listdir(folder_path) if f.endswith('.jpg') or f.endswith('.png')]

images = []

for image_file in image_files:
    image = cv2.imread(os.path.join(folder_path, image_file))
    if image is not None:
        images.append(image)

# Tạo một bản sao của danh sách ảnh gốc để xoay và ghép
rotated_images = images.copy()

# Duyệt qua từng ảnh để xoay nếu cần
for i, image in enumerate(images):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=100)

    if lines is not None:
        for rho, theta in lines[:, 0]:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * (a))
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * (a))

            # Tính góc giữa đoạn thẳng và trục ngang
            angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))

            # Nếu góc xoay lớn hơn ngưỡng (vd: 5 độ), thì xoay lại ảnh
            if abs(angle) > 5:
                center = (image.shape[1] // 2, image.shape[0] // 2)
                rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated = cv2.warpAffine(image, rot_mat, (image.shape[1], image.shape[0]))
                rotated_images[i] = rotated

# Ghép các ảnh đã xoay lại
stitcher = cv2.createStitcher() if cv2.__version__.startswith('3') else cv2.Stitcher_create()
status, result = stitcher.stitch(rotated_images)

if status == cv2.Stitcher_OK:
    output_path = 'stitched_image.jpg'
    cv2.imwrite(output_path, result)
    print(f"Stitched image saved as {output_path}")
    cv2.imshow('Stitched Image', result)  # Hiển thị ảnh ra màn hình
    cv2.waitKey(0)  # Đợi cho đến khi người dùng đóng cửa sổ ảnh
    cv2.destroyAllWindows()  # Đóng cửa sổ ảnh khi người dùng đã hoàn thành
else:
    print("Image stitching failed")

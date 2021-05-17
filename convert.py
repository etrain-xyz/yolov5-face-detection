from os.path import join, basename, exists
import cv2
import argparse
import yaml
import os

def yolo_format(bbox, img_w, img_h):
	x = int(bbox[0])
	y = int(bbox[1])
	w = int(bbox[2])
	h = int(bbox[3])
	x_center = (x + (w / 2)) / img_w
	y_center = (y + (h / 2)) / img_h
	w_box = w / img_w
	h_box = h / img_h
	return " ".join(["0", str(x_center), str(y_center), str(w_box), str(h_box)])

def convert(config, type):
	src_dir = config[type]["wider_images_path"]
	annotation_txt = config[type]["wider_annotations_path"]
	dst_dir = config[type]["yolo_path"]
	file = open(annotation_txt, 'r')
	lines = file.readlines()
	file.close()

	if not exists(dst_dir):
		os.makedirs(dst_dir)

	dict = {}
	current_row = None
	# Strips the newline character
	for line in lines:
		row = line.strip()
		if ".jpg" in row:
			current_row = row
			dict[current_row] = []
		if current_row is not None and ".jpg" not in row:
			dict[current_row].append(row)

	for image_name in dict:
		img_path = join(src_dir, "images", image_name)
		img = cv2.imread(img_path)
		img_h, img_w, _ = img.shape
		rows = []
		for i in range(1, len(dict[image_name])):
			fields = dict[image_name][i].split(" ")
			bbox = fields[0:4]
			row = yolo_format(bbox, img_w, img_h)
			rows.append(row)
		content = "\n".join(rows)
		file_name = basename(image_name).split(".")[0] + ".txt"
		file = open(join(dst_dir, file_name), "w")
		file.write(content)
		file.close()
		cv2.imwrite(join(dst_dir, basename(image_name)), img)


if __name__ == "__main__":
	with open(r'./config.yaml') as file:
		config = yaml.load(file, Loader=yaml.FullLoader)

	parser = argparse.ArgumentParser(description="Choose dataset")
	parser.add_argument(
		"--data_type",
		type=str,
		default="val",
		help="source directory")
	args = parser.parse_args()
	type = args.data_type
	convert(config, type)
import fitz  # PyMuPDF
from PIL import Image
import re
import io
import json
import os

def is_title(block):
    """
    判断是否为标题，这里简单以字体大小作为判断标准。
    可能需要根据实际情况调整阈值。
    """
    return block["lines"][0]["spans"][0]["size"] > 16  # 假设字体大于18的是标题

def extract_text_and_images(pdf_path, output_dir="img"):
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    image_count = 0
    book_blocks = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text_page = page.get_text("dict")
        blocks = text_page["blocks"]
        for block in blocks:
            book_blocks.append(block)

    segments = []
    segment = []
    for block in book_blocks:
        segment.append(block)
        if block["type"] == 1:
            segments.append(segment)
            segment = []

    dsegs =[]
    for segment in segments:
        segment.reverse()
        
        xref = None;

        desc_blocks = [];
        title_blocks = [];
        
        desc_end = False;
        title_end = False;
        for block in segment:
            if block["type"] == 1:
                xref = block
            elif block["type"] == 0:
                if is_title(block):
                    if not desc_end:
                        desc_end = True
                else:
                    if desc_end:
                        title_end = True
                if desc_end:
                    if not title_end:
                        title_blocks.append(block)
                else:
                    desc_blocks.append(block)
        desc_blocks.reverse()
        title_blocks.reverse()
        dseg = {
            "image_name":None,
            "category":"",
            "formal":"",
            "name":"",
            "desc":"",
            "img":xref
        }
        for block in title_blocks:
            for line in block["lines"]:
                for span in line["spans"]:
                    dseg["name"] += span["text"]
        for block in desc_blocks:
            for line in block["lines"]:
                for span in line["spans"]:
                    dseg["desc"] += span["text"]
        find_strs = re.findall(r"^[a-zA-Z ]*", dseg["desc"])
        if find_strs:
            dseg["formal"] = find_strs[0]

        if re.match(r"^[0-9]", dseg["name"]):
            cats = re.split(r" +", dseg["name"])
            dseg["image_name"] = cats[0]
            dseg["name"] = cats[1]
            dseg["category"] = cats[2]
            dsegs.append(dseg)
    save_section(output_dir, dsegs)
    doc.close()

def save_section(output_dir, segments):
    fishes = []
    for seg in segments:

        image_info = seg["img"]
        image_bytes = image_info["image"]
        image_ext = image_info["ext"]
        
        image_name = seg["image_name"]
        img_filename = f"img_{image_name}.{image_ext}"
        fishes.append({
            "category":seg["category"],
            "formal":seg["formal"],
            "name":seg["name"],
            "desc":seg["desc"],
            "img":"%s/%s"%(output_dir, img_filename)
        })
        
        # 打开并保存图像
        image = Image.open(io.BytesIO(image_bytes))
        image.save(os.path.join(output_dir, img_filename))
    with open("fishes.json", "w", encoding="utf-8") as f:
        json.dump(fishes, f, indent=2)

# 使用示例
extract_text_and_images("dsyl.pdf")

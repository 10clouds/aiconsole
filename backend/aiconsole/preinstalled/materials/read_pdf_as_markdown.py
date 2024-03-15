"""
Use the function read_pdf_as_markdown to read the content of a PDF file.
"""

import base64
import os
import re

import fitz
import openai

from aiconsole_toolkit.settings import get_settings


def split_pages_to_chunks(pdf_pages: list[fitz.Page], chunk_size: int, overlap: int):
    chunks = []
    for i in range(0, len(pdf_pages), chunk_size - overlap):
        chunks.append(pdf_pages[i : i + chunk_size])
    return chunks


def pdf_pages_to_pixmaps(pdf_pages: list[fitz.Page]):
    zoom_factor = 3  # quality of the image
    mat = fitz.Matrix(zoom_factor, zoom_factor)
    result = []

    for page in pdf_pages:
        pix = page.get_pixmap(matrix=mat)
        result.append(pix)

    return result


def pixmap_to_base64(pixmap: fitz.Pixmap):
    pixmap_bytes = pixmap.tobytes()
    base64_bytes = base64.b64encode(pixmap_bytes)
    base64_string = base64_bytes.decode("utf-8")
    return base64_string


def extract_urls_and_labels_from_pdf(pdf_pages: list[fitz.Page]):
    links_info = []

    for page in pdf_pages:
        links = page.get_links()
        for link in links:
            if link["kind"] == fitz.LINK_URI:
                uri = link["uri"]
                # The rectangle area of the link
                link_rect = fitz.Rect(link["from"])
                # Extract text within this rectangle
                link_text = page.get_text("text", clip=link_rect)
                links_info.append({"uri": uri, "text": link_text.strip()})

    return links_info


def extract_images_from_pdf(pdf_pages: list[fitz.Page], pdf: fitz.Document):
    images_info = []
    for page in pdf_pages:
        image_list = page.get_images(full=True)
        for idx, img in enumerate(image_list):
            xref = img[0]
            base_image = pdf.extract_image(xref)
            image_bytes = base_image["image"]
            image_name = f"page_{page.number}_img_{idx}"
            image_path = os.path.join("images", image_name)
            os.makedirs(os.path.join("images"), exist_ok=True)
            with open(image_path, "wb") as f:
                f.write(image_bytes)
            images_info.append({"path": image_path})
    return images_info


def insert_links_to_md(md: str, links_info: list[dict]):
    for link in links_info:
        matched_as_link = re.search(re.escape("[" + link["text"] + "]()"), md)
        if matched_as_link:
            md = md.replace(matched_as_link.group(), f"[{link['text']}]({link['uri']})")
        else:
            matched_as_text = re.search(re.escape(link["text"]), md)
            if matched_as_text:
                md = md.replace(matched_as_text.group(), f"[{link['text']}]({link['uri']})")

    # in the end check if links (not images) with empty url are present and remove them leaving only text
    md = re.sub(r"([^!]|^)(\[(.*?)\]\(\))", lambda match: f"{match.group(1)}{match.group(3)}", md)

    return md


def insert_images_to_md(md: str, images_info: list[dict]):
    result = md
    for image in images_info:
        result = re.sub(r"!\[(.*?)\]\(\)", lambda match: f"![{match.group(1)}]({image['path']})", result, 1)

    return result


system_prompt = "You are a PDF-to-Markdown converter. When user sends you screenshots of pages of a PDF document you should return a markdown text representation of the PDF. You don't return markdown code in ```markdown...``` code block. You don't comment or introduce any of PDF content, you only return the Markdown code and NOTHING else, just plain Markdown without prefixing it with ```. When PDF page contains besides hypertext also images, you should paste long and detailed text description of the image in the alt text and leave url empty like ![Image that shows ...](). You don't treat graphical symbols (like icons) as images - image are e.g. photos, screenshots etc. - only them you paste as ![alt text](). You paste ![alt text]() exactly in the place in the text where it appears in PDF screenshot. When you see that some text looks like a link (e.g. blue underlined text), you should paste it as a link leaving the url empty like [text](). You should never try to summarize the PDF content, trying to go word by word and sentence by sentence as far as possible."


def pdf_pages_screenshots_to_markdown(screenshots: list[str], prev_responses: list[str]):
    base64_images = screenshots
    openai_key = get_settings().openai_api_key
    client = openai.OpenAI(api_key=openai_key)

    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": [
                    *[
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_images}"}}
                        for base64_images in base64_images
                    ],
                ],
            },
            *[{"role": "assistant", "content": response_content} for response_content in prev_responses],
        ],
        max_tokens=4096,
    )

    response_content = response.choices[0].message.content

    if not response_content:
        print("No response content from OpenAI")
        return ""

    if response_content.startswith("```markdown") and response_content.endswith("```"):
        response_content = response_content[10:-3].strip()
    elif response_content.startswith("```") and response_content.endswith("```"):
        response_content = response_content[3:-3].strip()

    if response_content:
        response_content += "\n"

    return response_content


def read_pdf_as_markdown(pdf_path):
    pdf = fitz.open(pdf_path)
    pages = [pdf[i] for i in range(pdf.page_count)]
    chunks = split_pages_to_chunks(pages, chunk_size=3, overlap=1)

    md = ""

    md_chunks = []

    for chunk in chunks:
        pixmaps = pdf_pages_to_pixmaps(chunk)
        base64_images = [pixmap_to_base64(pixmap) for pixmap in pixmaps]
        md_chunk = pdf_pages_screenshots_to_markdown(base64_images, md_chunks[-1:] if md_chunks else [])
        md_chunks.append(md_chunk)

        links_info = extract_urls_and_labels_from_pdf(chunk)
        images_info = extract_images_from_pdf(chunk, pdf)
        md_chunk_with_links = insert_links_to_md(md_chunk, links_info)
        md_chunk_with_links_and_images = insert_images_to_md(md_chunk_with_links, images_info)
        print(md_chunk_with_links_and_images)
        md += md_chunk_with_links_and_images
        # save current md to temp file
        with open(os.path.join("running.md"), "w") as f:
            f.write(md)

    return md

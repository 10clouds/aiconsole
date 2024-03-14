"""
Use the function read_pdf_as_markdown to read the content of a PDF file.
"""

import base64
import re

import fitz
import openai

from aiconsole_toolkit.settings import get_settings


def pdf_pages_to_pixmaps(pdf_path):
    doc = fitz.open(pdf_path)
    zoom_factor = 3
    mat = fitz.Matrix(zoom_factor, zoom_factor)
    result = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(matrix=mat)
        result.append(pix)

    return result


def pixmap_to_base64(pixmap: fitz.Pixmap):
    pixmap_bytes = pixmap.tobytes()
    base64_bytes = base64.b64encode(pixmap_bytes)
    base64_string = base64_bytes.decode("utf-8")
    return base64_string


def extract_urls_and_labels_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    links_info = []

    for page in doc:
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


system_prompt = 'You are a PDF-to-Markdown converter. When user sends you screenshots of pages of a PDF document you should return a markdown text representation of the PDF. You don\'t return markdown code in ```markdown...``` code block. Instead before the beginning of markdown code you write "BEGIN_MARKDOWN" and after the end of markdown code you write "END_MARKDOWN". When PDF page contains besides hypertext also images, you should paste long and detailed text description of the image in the alt text and leave url empty like ![Image that shows ...](). When you that some text looks like a link (e.g. blue underlined text), you should paste it as a link leaving the url empty like [text]().'


def read_pdf_as_markdown(pdf_path):
    pixmaps: list[fitz.Pixmap] = pdf_pages_to_pixmaps(pdf_path)
    base64_images = [pixmap_to_base64(pixmap) for pixmap in pixmaps]
    links_info = extract_urls_and_labels_from_pdf(pdf_path)

    openai_key = get_settings().openai_api_key
    client = openai.OpenAI(api_key=openai_key)

    responses = []
    matched = None
    requests_count = 0

    while not matched and requests_count < 10:
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
                *[{"role": "assistant", "content": response_content} for response_content in responses],
            ],
            max_tokens=4096,
        )

        requests_count += 1

        response_content = response.choices[0].message.content
        responses.append(response_content)

        matched = re.search(r"BEGIN_MARKDOWN(.*)END_MARKDOWN", "".join(responses), re.DOTALL)

    md = ""

    if matched:
        md = matched.group(1)
    else:
        md = "".join(responses)

    # Populate markdown links with URIs from links_info
    for link in links_info:
        matched_as_link = re.search(re.escape("[" + link["text"] + "]()"), md)
        if matched_as_link:
            md = md.replace(matched_as_link.group(), f"[{link['text']}]({link['uri']})")
        else:
            matched_as_text = re.search(re.escape(link["text"]), md)
            if matched_as_text:
                md = md.replace(matched_as_text.group(), f"[{link['text']}]({link['uri']})")

    return md

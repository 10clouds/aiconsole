"""
Use the function `pdf_to_markdown` to convert a PDF to markdown.
"""

import base64
import os
import re

import fitz
import openai
from fitz import Document, Page, Pixmap

from aiconsole_toolkit.settings import get_settings


def split_pages_to_chunks(pdf_pages: list[Page], chunk_size: int, overlap: int):
    chunks = []
    for i in range(0, len(pdf_pages), chunk_size - overlap):
        chunks.append(pdf_pages[i : i + chunk_size])
    return chunks


def pdf_pages_to_pixmaps(pdf_pages: list[Page]):
    zoom_factor = 3  # quality of the image
    mat = fitz.Matrix(zoom_factor, zoom_factor)
    result = []

    for page in pdf_pages:
        pix = page.get_pixmap(matrix=mat)
        result.append(pix)

    return result


def pixmap_to_base64(pixmap: Pixmap):
    pixmap_bytes = pixmap.tobytes()
    base64_bytes = base64.b64encode(pixmap_bytes)
    base64_string = base64_bytes.decode("utf-8")
    return base64_string


def extract_urls_and_labels_from_pdf(pdf_pages: list[Page]):
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


def extract_images_from_pdf(pdf_pages: list[Page], pdf: Document, processed_path: str):
    images_info = []
    for page in pdf_pages:
        image_list = page.get_images(full=True)
        for idx, img in enumerate(image_list):
            xref = img[0]
            base_image = pdf.extract_image(xref)
            image_bytes = base_image["image"]
            md_file_name = os.path.basename(processed_path).replace(".md", "").replace(" ", "_")
            image_name = f"{md_file_name}_page_{page.number}_image_{idx}.png"
            image_path = os.path.abspath(os.path.join("images", image_name))
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            md_file_dir = os.path.dirname(processed_path)
            with open(image_path, "wb") as f:
                f.write(image_bytes)
            image_rel_path = os.path.relpath(image_path, start=md_file_dir)
            images_info.append({"path": image_rel_path})
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
        # having stamp/signature image means that the whole page is a scan of paper document - therefore we don't treat it as an image
        result = re.sub(
            r"!\[(?!STAMP/SIGNATURE)(.*?)\]\(\)", lambda match: f"![{match.group(1)}]({image['path']})", result, 1
        )

    return result


def correct_table_format(md_content: str) -> str:
    """
    Corrects the markdown table format by ensuring each row has the same number of columns.
    """
    corrected_md = []
    md_lines = md_content.split("\n")
    table_lines = []
    in_table = False

    for line in md_lines:
        # Check if the line is part of a table
        if re.match(r"\|.*?\|", line):
            in_table = True
            table_lines.append(line)
        else:
            if in_table:
                # Process the collected table lines
                corrected_table = correct_table_columns(table_lines)
                corrected_table = add_header_if_missing(corrected_table)
                corrected_md.extend(corrected_table)
                table_lines = []
            in_table = False
            corrected_md.append(line)

    # Ensure any table at the end of the document is processed
    if in_table:
        corrected_table = correct_table_columns(table_lines)
        corrected_table = add_header_if_missing(corrected_table)
        corrected_md.extend(corrected_table)

    return "\n".join(corrected_md)


def correct_table_columns(table_lines: list) -> list:
    """
    Ensures all rows in the table have the same number of columns.
    """
    column_counts = [line.count("|") - 1 for line in table_lines]
    most_common_count = max(set(column_counts), key=column_counts.count)

    corrected_lines = []
    for line in table_lines:
        current_count = line.count("|") - 1
        if current_count < most_common_count:
            # Add empty cells to match the most common column count
            line += ("| " * (most_common_count - current_count)) + "|"
        corrected_lines.append(line)

    return corrected_lines


def add_header_if_missing(table_lines: list) -> list:
    """
    Adds a header row if the table is missing one.
    """
    if table_lines[1].startswith("|-") or table_lines[1].startswith("| -"):
        return table_lines
    elif table_lines[0].startswith("|-") or table_lines[0].startswith("| -"):
        header = "| " + " | ".join([" " for _ in range(table_lines[1].count("|"))])
        table_lines = [header] + table_lines
        return table_lines
    else:
        header = "| " + " | ".join([" " for _ in range(table_lines[0].count("|"))])
        separator = "|-" + "-|".join(["-" for _ in range(table_lines[0].count("|") - 1)]) + "-|"
        table_lines = [header, separator] + table_lines
        return table_lines


system_prompt = """You are a PDF-to-Markdown converter. When user sends you screenshots of pages of a PDF document you return a markdown text representation of the PDF. You don't return markdown code in ```markdown...``` code block. You don't comment or introduce any of PDF content, you only return the Markdown code and NOTHING else, just plain Markdown without prefixing it with ```. When PDF page contains besides hypertext also images, you paste text description of the image in the alt text and leave url empty like ![Image that shows ...](). You NEVER treat graphical symbols, icons as images and don't paste ![alt text]() clause for them. If the whole page is a scan of paper document - you transcribe the content of it, and don't treat it as an image. If you see a stamp or a signature you paste ![STAMP/SIGANTURE: ...here text transcription](). Images are e.g. photos, screenshots etc. - only these you paste as ![alt text](). You paste ![alt text]() exactly in the place in the text where it appears in PDF screenshot. When you see that some text looks like a link (e.g. blue underlined text), you paste it as a link leaving the url empty like [text](). When you see a table-like element in screenshot you use markdown table syntax. Correct markdown table syntax is when each table row starts with | and ends with |. Each cell in the row is separated by |. Each row has the same number of cells. If the table has headers, the header row is separated from the rest of the table by a row of cells with at least one - in each cell. If the table has no headers, then the header row is a row with empty cells. You never skip header cells. Example of correct markdown table syntax:
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |
Example of correct markdown table syntax with no headers:
| | |
|-|-|
| Cell 1 | Cell 2 |
| Cell 3 | Cell 4 |
Example of incorrect markdown table syntax:
| Header 1 | Header 2 |
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |
The correct version of the table is:
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |
Another example of incorrect markdown table syntax:
| Header 1 | Header 2 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
| Cell 4   | Cell 5   | Cell 6   |
The correct version of the table is:
| Header 1 | Header 2 | |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
The number of cells in the header row and the number of cells in the rest of the table must be the same - it is VERY important. So if you see that the number of cells in the header row or some other row is different, you correct it e.g. by adding an empty cell at the end of the row (or at the beginning - decide based on meaning of headers and how they match the columns). When some text you think should to be a title or subtitle you add some # to it. When something should be bold you use *. When something looks like a checkbox syntax:
- [ ] Option 1
- [x] Option 2
You never try to summarize the PDF content."""


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
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_images}",
                                "detail": "high",
                            },
                        }
                        for base64_images in base64_images
                    ]
                ],
            },
            *[{"role": "assistant", "content": response_content} for response_content in prev_responses],
        ],
        max_tokens=4096,
        temperature=0.0,
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


def get_filename_from_path(path: str):
    return os.path.basename(path)


def pdf_to_markdown(pdf_path):
    pdf = fitz.open(pdf_path)
    pages = [pdf[i] for i in range(pdf.page_count)]
    chunk_size = 2
    overlap = 1
    chunks = split_pages_to_chunks(pages, chunk_size, overlap)

    md = ""

    original_filename = get_filename_from_path(pdf_path)
    processed_filename = original_filename.replace(".pdf", ".md")
    processed_path = os.path.abspath(os.path.join("processed_pdf", processed_filename))

    print(f"Processing {original_filename} consisting of {len(pages)} pages...")
    print("Output will be saved to", processed_path)

    os.makedirs(os.path.dirname(processed_path), exist_ok=True)

    with open(processed_path, "w", encoding="utf-8") as f:
        f.write(md)

    md_chunks = []

    for index, chunk in enumerate(chunks):
        pixmaps = pdf_pages_to_pixmaps(chunk)
        base64_images = [pixmap_to_base64(pixmap) for pixmap in pixmaps]
        first_page_number = 1 if index == 0 else index * (chunk_size - overlap) + 1
        last_page_number = first_page_number + len(chunk) - 1
        print(f"Processing pages {first_page_number}-{last_page_number}...")
        md_chunk = pdf_pages_screenshots_to_markdown(base64_images, md_chunks[-1:] if md_chunks else [])
        md_chunk = correct_table_format(md_chunk)
        md_chunks.append(md_chunk)

        links_info = extract_urls_and_labels_from_pdf(chunk)
        images_info = extract_images_from_pdf(chunk, pdf, processed_path)
        md_chunk_with_links = insert_links_to_md(md_chunk, links_info)
        md_chunk_with_links_and_images = insert_images_to_md(md_chunk_with_links, images_info)
        md += md_chunk_with_links_and_images
        with open(processed_path, "w", encoding="utf-8") as f:
            f.write(md)

    md = correct_table_format(md)

    print(f"Succesfully processed {original_filename} and saved to {processed_path}")

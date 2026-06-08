from io import BytesIO
import os
from typing import Optional

from PIL import Image
import pytesseract
from pypdf import PdfReader

from models.Processed_Assests import (
    ProcessedAssets,
    DocumentAsset,
    ImageAsset,
    VideoAsset,
)


def extract_ocr_from_bytes(
    image_bytes: bytes,
) -> Optional[str]:
    try:
        image = Image.open(
            BytesIO(image_bytes)
        )

        return (
            pytesseract.image_to_string(image)
            .strip()
        )

    except Exception as e:
        print(f"OCR failed: {e}")
        return None


def extract_ocr_from_image(
    image: Image.Image,
) -> Optional[str]:
    try:
        return (
            pytesseract.image_to_string(image)
            .strip()
        )

    except Exception as e:
        print(f"OCR failed: {e}")
        return None


def extract_ocr_from_path(
    image_path: str,
) -> Optional[str]:
    try:
        image = Image.open(image_path)

        return extract_ocr_from_image(
            image
        )

    except Exception as e:
        print(f"OCR failed: {e}")
        return None


def process_image(
    image_path: str,
) -> ProcessedAssets:

    processed = ProcessedAssets()

    if not os.path.exists(
        image_path
    ):
        return processed

    try:
        with open(
            image_path,
            "rb",
        ) as f:
            image_bytes = f.read()

        image_asset = ImageAsset(
            asset_id=os.path.basename(
                image_path
            ),
            image_bytes=image_bytes,
            ocr_text=extract_ocr_from_bytes(
                image_bytes
            ),
        )

        processed.image_assets.append(
            image_asset
        )

        if image_asset.ocr_text:
            processed.texts.append(
                image_asset.ocr_text
            )

    except Exception as e:
        print(
            f"Image processing failed: {e}"
        )

    return processed
    

def process_video(
    video_path: str,
) -> ProcessedAssets:

    processed = ProcessedAssets()

    if not os.path.exists(
        video_path
    ):
        return processed

    video_asset = VideoAsset(
        asset_id=os.path.basename(
            video_path
        ),
        transcript=None,
        keyframes=[],
    )

    processed.video_assets.append(
        video_asset
    )

    return processed


def process_pdfs(
    pdf_path: str,
) -> ProcessedAssets:

    processed = ProcessedAssets()

    if not pdf_path or not os.path.exists(
        pdf_path
    ):
        return processed

    if os.path.isdir(pdf_path):
        pdf_files = [
            os.path.join(pdf_path, f)
            for f in os.listdir(pdf_path)
            if f.lower().endswith(".pdf")
        ]
    else:
        pdf_files = [pdf_path]

    for file in pdf_files:
        try:
            reader = PdfReader(file)

            text_parts = []
            page_images = []

            for page_number, page in enumerate(
                reader.pages,
                start=1,
            ):
                page_text = (
                    page.extract_text()
                    or ""
                )

                text_parts.append(
                    page_text
                )

                try:
                    for (
                        img_idx,
                        pdf_image,
                    ) in enumerate(
                        page.images,
                        start=1,
                    ):
                        image_bytes = (
                            pdf_image.data
                        )

                        image_asset = (
                            ImageAsset(
                                asset_id=(
                                    f"{os.path.basename(file)}"
                                    f"_p{page_number}"
                                    f"_img{img_idx}"
                                ),
                                image_bytes=image_bytes,
                                ocr_text=extract_ocr_from_bytes(
                                    image_bytes
                                ),
                                source_document=os.path.basename(
                                    file
                                ),
                                page_number=page_number,
                            )
                        )

                        page_images.append(
                            image_asset
                        )

                        processed.image_assets.append(
                            image_asset
                        )

                except Exception as e:
                    print(
                        f"Image extraction failed: {e}"
                    )

            full_text = "\n".join(
                text_parts
            )

            document_asset = (
                DocumentAsset(
                    asset_id=os.path.basename(
                        file
                    ),
                    content=full_text,
                    page_images=page_images,
                )
            )

            processed.document_assets.append(
                document_asset
            )

            processed.texts.append(
                full_text
            )

        except Exception as e:
            print(
                f"PDF processing failed: {e}"
            )

    return processed

def merge_processed_assets(
    target: ProcessedAssets,
    source: ProcessedAssets,
) -> None:

    target.texts.extend(
        source.texts
    )

    target.document_assets.extend(
        source.document_assets
    )

    target.image_assets.extend(
        source.image_assets
    )

    target.video_assets.extend(
        source.video_assets
    )
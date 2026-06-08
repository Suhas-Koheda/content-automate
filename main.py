from fastapi import FastAPI
from models.Asset import Asset
from models.Processed_Assests import ProcessedAssets
from utils.Ingestor import (
    process_image,
    process_video,
    process_pdfs,
    merge_processed_assets,
)
app = FastAPI()


@app.post("/ingest")
async def ingest_content(
    assets: list[Asset]
):
    processed = ProcessedAssets()

    for asset in assets:
        match asset.type:
            case "image":
                merge_processed_assets(
                    processed,
                    process_image(asset.path)
                )

            case "video":
                merge_processed_assets(
                    processed,
                    process_video(asset.path)
                )

            case "document":
                merge_processed_assets(
                    processed,
                    process_pdfs(asset.path)
                )
            case "text":
                processed.texts.append(
                   asset.content if asset.content is not None else ""
                )
                
        
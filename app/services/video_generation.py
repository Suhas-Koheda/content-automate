import os
import asyncio
from app.llm.model import genai_client, VIDEO_MODEL_FAST
from google.genai import types

async def generate_scene_video(visual_description: str, task_id: str) -> dict:
    """
    Generates a 5-second video storyboard using Veo, with asynchronous non-blocking polling,
    exponential backoff, and delegation of blocking operations to worker threads.
    """
    os.makedirs("ui/generated", exist_ok=True)
    video_filename = f"video_{task_id}.mp4"
    video_path = os.path.join("ui/generated", video_filename)

    try:
        # Start the video generation operation asynchronously
        operation = await asyncio.to_thread(
            genai_client.models.generate_videos,
            model=VIDEO_MODEL_FAST,
            prompt=visual_description,
            config=types.GenerateVideosConfig(
                duration_seconds=5
            )
        )

        # Non-blocking polling loop with exponential backoff
        sleep_time = 8.0
        max_attempts = 15
        attempts = 0

        while attempts < max_attempts:
            # Asynchronous, non-blocking sleep (does not block FastAPI event loop!)
            await asyncio.sleep(sleep_time)

            # Get latest status of the operation
            operation = await asyncio.to_thread(
                genai_client.operations.get,
                name=operation.name
            )

            if operation.done:
                break

            attempts += 1
            # Exponential backoff (max 20 seconds)
            sleep_time = min(sleep_time * 1.5, 20.0)

        if operation.done:
            if operation.response and operation.response.generated_videos:
                video_obj = operation.response.generated_videos[0].video
                # Save the video file
                await asyncio.to_thread(video_obj.save, video_path)
                return {
                    "success": True,
                    "video_url": f"/generated/{video_filename}",
                    "log": "Video asset generated successfully."
                }
            else:
                return {
                    "success": False,
                    "error": "Empty response",
                    "log": "Video generation completed but no video asset was returned."
                }
        else:
            return {
                "success": False,
                "error": "Timeout",
                "log": "Video asset generation timed out."
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "log": f"Failed to generate video asset: {str(e)}"
        }

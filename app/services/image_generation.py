import os
import io
import asyncio
from PIL import Image, ImageDraw, ImageFont
from app.llm.model import genai_client, IMAGE_MODEL_PRO
from google.genai import types

def create_fallback_graphic(slide, image_path: str):
    """
    Programmatically creates a premium, high-contrast, visual slide card 
    containing the title, overlay text, and styling accents based on slide theme
    when Imagen/Gemini image generation models are not available.
    """
    width, height = 800, 800
    img = Image.new("RGB", (width, height), "#0a0b10")
    draw = ImageDraw.Draw(img)
    
    # Analyze keywords to match visual palette
    direction = (slide.visual_direction or "").lower()
    prompt = (slide.image_prompt or "").lower()
    
    if any(k in direction or k in prompt for k in ["industrial", "furnace", "sparks", "molten", "steel", "blast"]):
        # Industrial orange-black gradient
        color_start = (18, 19, 26)
        color_end = (35, 15, 5)
        accent_color = (249, 115, 22) # Orange
    elif any(k in direction or k in prompt for k in ["corporate", "navy", "silver", "beams", "office", "boardroom"]):
        # Corporate navy-silver gradient
        color_start = (10, 15, 30)
        color_end = (20, 25, 45)
        accent_color = (99, 102, 241) # Indigo
    elif any(k in direction or k in prompt for k in ["human", "worker", "portrait", "livelihoods", "people"]):
        # Human warm bronze/amber gradient
        color_start = (20, 15, 10)
        color_end = (45, 30, 20)
        accent_color = (245, 158, 11) # Amber
    elif any(k in direction or k in prompt for k in ["sunrise", "optimistic", "future", "light", "progress"]):
        # Optimistic sunrise gold gradient
        color_start = (15, 15, 25)
        color_end = (60, 40, 20)
        accent_color = (234, 179, 8) # Gold
    else:
        # Default premium Indigo-Purple gradient
        color_start = (15, 10, 30)
        color_end = (40, 10, 60)
        accent_color = (168, 85, 247) # Purple
        
    # Render gradient background
    for y in range(height):
        ratio = y / height
        r = int(color_start[0] * (1 - ratio) + color_end[0] * ratio)
        g = int(color_start[1] * (1 - ratio) + color_end[1] * ratio)
        b = int(color_start[2] * (1 - ratio) + color_end[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
        
    # Draw decorative premium borders and frame elements
    draw.rectangle([(20, 20), (width - 20, height - 20)], outline=(255, 255, 255, 25), width=1)
    # Accent indicator bar on the left
    draw.line([(35, 35), (35, height - 35)], fill=accent_color, width=4)
    
    # Font resolution
    font_bold_path = "/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf"
    font_reg_path = "/usr/share/fonts/opentype/urw-base35/NimbusSans-Regular.otf"
    
    try:
        font_title = ImageFont.truetype(font_bold_path, 34)
        font_body = ImageFont.truetype(font_reg_path, 28)
        font_footer = ImageFont.truetype(font_reg_path, 20)
    except IOError:
        # Graceful fallback to default system fonts
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_footer = ImageFont.load_default()

    # Title rendering
    title_text = f"SLIDE {slide.slide_number}: {slide.title.upper()}"
    draw.text((65, 60), title_text, fill=(255, 255, 255), font=font_title)
    
    # Subheader / Visual theme detail
    draw.text((65, 110), f"Direction: {slide.visual_direction}", fill=(180, 180, 180), font=font_footer)
    
    # Text wrap rendering for Overlay Text
    overlay_text = slide.overlay_text
    words = overlay_text.split()
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        test_line = " ".join(current_line)
        try:
            bbox = draw.textbbox((0, 0), test_line, font=font_body)
            line_w = bbox[2] - bbox[0]
        except AttributeError:
            line_w = len(test_line) * 14
            
        if line_w > width - 150:
            current_line.pop()
            lines.append(" ".join(current_line))
            current_line = [word]
            
    if current_line:
        lines.append(" ".join(current_line))
        
    y_text = 280
    for line in lines:
        draw.text((65, y_text), line, fill=(255, 255, 255), font=font_body)
        y_text += 45
        
    # Brand signature footer
    draw.text((65, height - 70), "CONTENT STUDIO  |  VISUAL LAYOUT REFERENCE", fill=(140, 140, 140), font=font_footer)
    img.save(image_path, "JPEG", quality=90)


async def generate_single_slide_image(slide, task_id: str, template_path: str = None) -> str:
    """
    Generates an image for a slide. If a template image is provided, conditions on it using
    gemini-2.5-flash-image for visual style consistency. Otherwise, uses Imagen 4.0.
    """
    os.makedirs("ui/generated", exist_ok=True)
    image_filename = f"slide_{task_id}_{slide.slide_number}.jpg"
    image_path = os.path.join("ui/generated", image_filename)

    # 1. Try style conditioning first if template path exists
    if template_path and os.path.exists(template_path):
        try:
            ref_image = Image.open(template_path)
            prompt_text = (
                f"Generate a social media slide image matching this prompt: '{slide.image_prompt}'. "
                f"Strictly match the visual style, layout composition, and color scheme of the provided image."
            )
            
            # Run blocking SDK call in a separate worker thread
            response = await asyncio.to_thread(
                genai_client.models.generate_content,
                model="gemini-2.5-flash-image",
                contents=[prompt_text, ref_image],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"]
                )
            )

            img_saved = False
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.inline_data:
                        generated_image = Image.open(io.BytesIO(part.inline_data.data))
                        generated_image.save(image_path)
                        img_saved = True
                        break
            
            if img_saved:
                return f"Successfully generated style-conditioned image for Slide {slide.slide_number}"
            else:
                raise ValueError("No image found in response candidate parts")
                
        except Exception as e:
            # Fall back to standard Imagen
            pass

    # 2. Fall back to standard Imagen text-to-image using IMAGE_MODEL_PRO
    try:
        response = await asyncio.to_thread(
            genai_client.models.generate_images,
            model=IMAGE_MODEL_PRO,
            prompt=slide.image_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/jpeg"
            )
        )
        if response.generated_images:
            response.generated_images[0].image.save(image_path)
            return f"Successfully generated image for Slide {slide.slide_number} (Imagen)"
        else:
            raise ValueError("No images returned by Imagen model")
    except Exception as e:
        # Fall back to programmatic layout card generation on free tier/errors
        try:
            create_fallback_graphic(slide, image_path)
            return f"Generated premium layout reference graphic for Slide {slide.slide_number} (Free Tier fallback)"
        except Exception as fallback_err:
            return f"Failed to generate image for Slide {slide.slide_number}: {str(e)} (Fallback error: {str(fallback_err)})"

async def generate_carousel_images(slides: list, task_id: str, template_path: str = None) -> list:
    """Generates all slide images concurrently in parallel using asyncio.gather."""
    tasks = [
        generate_single_slide_image(slide, task_id, template_path)
        for slide in slides
    ]
    results = await asyncio.gather(*tasks)
    return results

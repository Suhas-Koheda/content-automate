from langchain_core.prompts import ChatPromptTemplate
from models.llm_output import ImageScenes, ImageScript

from .model import writer_model,client
from google import genai
from google.genai import types

import os
import requests
import base64
from PIL import Image
from io import BytesIO


API_BASE_URL = "https://api.cloudflare.com/client/v4/accounts/ef79a237f234ff29828af26d4588e708/ai/run/"
headers = {
    "Authorization": f"Bearer {os.getenv("API_TOKEN")}",
    "Content-Type": "application/json",
}

visual_designer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a Visual Storyboard Generator.

TASK

Convert the provided content into a sequence of scenes for a short-form documentary/news video.

INPUT

You will receive:

* ORIGINAL_USER_CONTENT
* FACT_CHECKED_RESEARCH_REPORT
* FINAL_BLOG_POST
* WRITING_STYLE_REFERENCE (optional)
* PDF_RESEARCH_CONTEXT (optional)
* VISUAL_TEMPLATE_REFERENCE (optional)

OUTPUT SCHEMA

Return ONLY valid JSON matching:

```json
{{
  "scenes": [
    {{
      "scene_no": 1,
      "narration": "string",
      "image_prompt": "string"
    }}
  ]
}}
```

FIELD REQUIREMENTS

scene_no

* Integer
* Sequential
* Starts from 1

narration

* 1-3 short sentences
* Voice-over friendly
* Factually grounded
* Advances the story
* No camera directions
* No visual descriptions
* No markdown

image_prompt

* Detailed visual description for AI image generation
* Describe ONLY what should be visible
* Must contain:

  * subjects
  * environment
  * emotion
  * composition
  * lighting
  * camera framing
* Must NOT contain:

  * narration text
  * dialogue
  * captions
  * quotes
  * logos
  * watermarks
  * typography

SCENE RULES

* Generate between 5 and 10 scenes.
* Scene 1 must be a visual hook.
* Final scene must provide closure or CTA.
* Every scene must introduce new information.
* Every scene must be visually distinct.
* Avoid repetitive compositions.

IMAGE PROMPT RULES

Every image_prompt must naturally include:

* photorealistic
* cinematic
* documentary photography
* realistic humans
* realistic environment
* dramatic lighting
* professional photography
* high detail
* depth of field
* no text
* no captions
* no typography
* no watermark

VISUAL STORYTELLING RULES

Do NOT convert paragraphs directly into images.

Instead visualize:

* conflict
* consequences
* evidence
* scale
* emotion
* human impact
* investigation
* decision making
* cause and effect

QUALITY CHECKS

Before returning:

* Ensure narration and image_prompt are different.
* Ensure image_prompt contains visual directions only.
* Ensure no scene repeats another scene.
* Ensure all scenes contribute to a coherent story.
* Ensure output is valid JSON.
* Return JSON only.

"""
    ),
    (
        "human",
        """
ORIGINAL USER CONTENT:
{source_text}

FACT CHECKED RESEARCH REPORT:
{research_report}

FINAL BLOG POST:
{blog_post}

WRITING STYLE REFERENCE:
{style_sample}

PDF RESEARCH CONTEXT:
{pdf_context}

VISUAL TEMPLATE REFERENCE:
{template_reference}
"""
    )
])


def generate_image_script(
    source_text: str,
    research_report: str,
    blog_post: str,
    style_sample: str = "",
    pdf_context: str = "",
    template_reference: str = "",
) -> ImageScenes:

    messages = visual_designer_prompt.format_messages(
        source_text=source_text,
        research_report=research_report,
        blog_post=blog_post,
        style_sample=style_sample,
        pdf_context=pdf_context,
        template_reference=template_reference,
    )

    # Debug: Check the messages
    print(messages)
    print(type(writer_model))
    print(writer_model)

    structured_model = writer_model.with_structured_output(
        ImageScenes
    )

    scenes: ImageScenes = structured_model.invoke(messages)

    return scenes

def generate_flux_image(prompt):
    response = requests.post(
        f"{API_BASE_URL}@cf/black-forest-labs/flux-1-schnell",
        headers=headers,
        json={
            "prompt": prompt
        }
    )

    return response.json()
  
def generate_images(
    scenes: ImageScenes,
    output_dir: str = "generated_images",
):
    os.makedirs(
        output_dir,
        exist_ok=True,
    )

    generated_files = []

    for scene in scenes.scenes:

        response = generate_flux_image(scene.image_prompt)
        if not response.get("success", True):
            print("Cloudflare error:", response)
            continue

        if "result" not in response or "image" not in response["result"]:
            print("Unexpected response:", response)
            continue
        image_b64 = response["result"]["image"]
        image_bytes = base64.b64decode(image_b64)
        file_path = (
            os.path.join(
                output_dir,
                f"scene_{scene.scene_no}.png",
            )
        )
        with open(file_path, "wb") as f:
            f.write(image_bytes)
        print(f"Saved image for scene {scene.scene_no} at {file_path}")
        generated_files.append(
            file_path
        )

    return generated_files


if __name__ == "__main__":

    scenes = (
        generate_image_script(
            source_text="",
            research_report="",
            blog_post="""
            Indirect Privatisation Haunting Vizag Steel Plant?
Notwithstanding repeated claims by Telugu Desam Party and Bharatiya Janata Party leaders that there is no question of privatising the Visakhapatnam Steel Plant, the latest developments have raised suspicions that the steel plant management is indirectly involving private parties, leading to gradual privatisation.

The latest decision by the steel plant management to invite private participation under the Total Operation and Maintenance Contract (TOMC) system within the plant has triggered apprehensions among workers and trade unions.

The development comes at a time when optimism had begun to grow over the future of the Visakhapatnam Steel Plant following the financial support package announced by the Central government.

Production levels at the plant have reportedly improved in recent months, while workers have been striving to meet operational targets amid expectations that the plant could gradually recover from its prolonged financial crisis.

However, labour groups now allege that the plant management is quietly accelerating the implementation of the TOMC system, a move they claim could result in large sections of the steel plant being handed over to major private contracting companies.

According to workers’ representatives, the TOMC model goes beyond the earlier Total Maintenance Contract (TMC) system that existed in some departments.

Under the proposed framework, both operational and maintenance responsibilities of key plant divisions could be outsourced to private firms.

Employees fear that such a system would significantly reduce opportunities for fresh recruitment and eventually lead to the removal of both permanent and contract workers.

Trade union leaders claim that specific clauses included in the proposed tender conditions have intensified anxiety among workers, as they allegedly permit restructuring that could displace the existing workforce.

Workers have questioned how long they would be forced to continue without job security or labour rights.

The issue has also triggered criticism against the ruling TDP-led coalition government in Andhra Pradesh, with labour representatives accusing the state administration of remaining silent despite growing unrest among steel plant employees.

As part of the ongoing process, the steel plant management has reportedly invited Expressions of Interest (EOIs) for several divisions.

Labour sources claim that the Sinter Plant contract has already been secured by Tata Steel, while details regarding other companies participating in the process have not yet been publicly disclosed by the management.

Workers further allege that several critical divisions — including the Coke Oven, RMHP, Power Plant, Sinter Plant and Blast Furnaces — are already suffering from inadequate maintenance and poor rust clearance, adversely affecting production efficiency and operational capacity.

The financial distress at the plant also remains severe. According to labour representatives, salary-related dues amounting to nearly Rs 860 crore are still pending for employees.

Trade unions argue that the earlier TMC system included provisions secured through labour negotiations, under which 50 percent of recruitment opportunities were reserved for the families of permanent workers and another 50 percent for displaced local residents. They allege that these protections have now been removed under the latest tender framework.

With the proposed Operations and Maintenance Contract system expected to give greater control to large private contractors, workers fear that core operations of the steel plant may gradually move entirely into private hands.

Labour unions are expected to intensify protests in the coming days, demanding transparency from the plant management and assurances regarding employee protection.


""",
        )
    )

    print(scenes)

    files = generate_images(
        scenes
    )

    print(files)
from app.llm.model import creative_llm
from app.llm.prompts.multimedia_prompt import multimedia_prompt
from app.schemas.outputs import video_parser
from app.agents.writer_agent import format_blog
from app.services.video_generation import generate_scene_video

def format_video(video_output) -> str:
    lines = ["# Video Script & Storyboard\n"]
    for scene in video_output.scenes:
        lines.append(f"### Scene {scene.scene_number} ({scene.timing})")
        lines.append(f"**Visual Description:** {scene.visual_description}")
        lines.append(f"**Audio/Voiceover:** *{scene.audio_dialogue}*\n")
        lines.append("---")
    return "\n".join(lines)

async def run_video_agent(state):
    video_chain = multimedia_prompt | creative_llm | video_parser
    result = await video_chain.ainvoke({
        "research_data": format_blog(state["writer"]["blog"]),
        "format_instructions": video_parser.get_format_instructions()
    })
    state["video"]["status"] = "completed"
    state["video"]["script"] = result
    state["logs"].append("Video agent completed")

    # Generate scene video (Veo storyboard)
    if result.scenes:
        state["logs"].append("Initiating video generation asset...")
        first_scene = result.scenes[0]
        res = await generate_scene_video(first_scene.visual_description, state["task_id"])
        state["logs"].append(res["log"])
        if res["success"]:
            state["video"]["video_url"] = res["video_url"]

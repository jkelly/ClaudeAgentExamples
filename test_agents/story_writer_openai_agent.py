"""
Story Writer Agent - OpenAI Version using LiteLLM
Run with: uv run story_writer_openai_agent.py

Configuration:
- Copy .env.example to .env and set OPENAI_API_KEY
- Or set OPENAI_API_KEY environment variable directly
- Uses LiteLLM to directly call OpenAI API

GPT-5 Support:
- Supports GPT-5 reasoning_effort parameter: minimal, low, medium (default), high
- Supports GPT-5 verbosity parameter: low, medium (default), high
- Set OPENAI_MODEL=gpt-5 or gpt-5-mini or gpt-5-nano to use GPT-5
- Set OPENAI_REASONING_EFFORT and OPENAI_VERBOSITY in .env to customize

Requirements:
- litellm>=1.77.5
- openai (installed as litellm dependency)
"""
import asyncio
import os
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import litellm


def load_openai_config():
    """
    Load OpenAI configuration from .env file.

    Reads API keys and model settings from the .env file in the project root.
    Also loads GPT-5 specific parameters like reasoning_effort and verbosity.

    Returns:
        dict: Configuration dictionary containing:
            - api_key: OpenAI API key
            - model: Model name (gpt-4o, gpt-5, etc.)
            - provider: Always "OpenAI"
            - reasoning_effort: GPT-5 reasoning level (minimal/low/medium/high)
            - verbosity: GPT-5 output verbosity (low/medium/high)

    Raises:
        ValueError: If OPENAI_API_KEY is not found in environment
    """
    # Load .env from current directory
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ Loaded configuration from {env_path}")
    else:
        print(f"⚠ No .env file found at {env_path}")
        print(f"  Copy .env.example to .env and set OPENAI_API_KEY")

    # Get OpenAI API key and model
    openai_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o")

    # GPT-5 specific parameters (only used when model is gpt-5/gpt-5-mini/gpt-5-nano)
    # reasoning_effort: Controls how deeply the model thinks
    #   - minimal: Fast responses with minimal reasoning (best for simple tasks)
    #   - low: Quick everyday tasks
    #   - medium: Balanced reasoning (default)
    #   - high: Deep thinking for complex multi-step tasks
    reasoning_effort = os.getenv("OPENAI_REASONING_EFFORT", "medium")

    # verbosity: Controls output length and detail level
    #   - low: Concise responses (~731 tokens)
    #   - medium: Balanced length (default, ~1017 tokens)
    #   - high: Detailed responses (~1263 tokens)
    verbosity = os.getenv("OPENAI_VERBOSITY", "medium")

    if not openai_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")

    print(f"Provider: OpenAI (via LiteLLM)")
    print(f"Model: {model}")

    # Only show GPT-5 params if using a GPT-5 model
    if "gpt-5" in model.lower():
        print(f"Reasoning Effort: {reasoning_effort}")
        print(f"Verbosity: {verbosity}")
    print()

    return {
        "api_key": openai_key,
        "model": model,
        "provider": "OpenAI",
        "reasoning_effort": reasoning_effort,
        "verbosity": verbosity
    }


def setup_litellm(config):
    """
    Configure LiteLLM to call OpenAI API.

    Args:
        config (dict): Configuration dictionary with api_key and model

    Returns:
        str: The model name to use for API calls
    """
    # Set OpenAI API key for LiteLLM to use
    os.environ["OPENAI_API_KEY"] = config["api_key"]

    # Configure LiteLLM settings
    litellm.drop_params = True  # Drop unsupported params instead of erroring
    litellm.set_verbose = False  # Set to True for debugging API calls

    print("✓ LiteLLM configured for OpenAI API")
    print(f"  Model: {config['model']}")
    print()

    return config["model"]


async def call_llm(model: str, messages: list, config: dict):
    """
    Call the LLM with appropriate parameters based on the model type.

    Automatically detects GPT-5 models and uses the appropriate API:
    - GPT-5 models: Uses responses.create API with reasoning_effort and verbosity parameters
    - Other models (GPT-4o, etc.): Uses standard chat.completions.create API via LiteLLM

    Args:
        model (str): Model name (e.g., "gpt-5", "gpt-5-mini", "gpt-4o", etc.)
        messages (list): List of message dictionaries with "role" and "content" keys
        config (dict): Configuration dictionary containing:
            - api_key: OpenAI API key
            - reasoning_effort: GPT-5 reasoning level (ignored for non-GPT-5)
            - verbosity: GPT-5 output verbosity level (ignored for non-GPT-5)

    Returns:
        str: The response text content from the model

    Note:
        GPT-5's responses.create API uses a different format than the standard
        chat completions API. It expects "input" instead of "messages" and returns
        a structured output that may include reasoning steps.
    """
    # Check if this is a GPT-5 model (gpt-5, gpt-5-mini, gpt-5-nano)
    is_gpt5 = "gpt-5" in model.lower()

    if is_gpt5:
        # === GPT-5 PATH: Use responses.create API ===
        # GPT-5 uses a different API endpoint with reasoning and verbosity support
        from openai import OpenAI

        client = OpenAI(api_key=config["api_key"])

        # Convert chat messages to single input string
        # The responses API expects "input" (string) instead of "messages" (array)
        if len(messages) == 1:
            # Single message - use content directly
            input_text = messages[0]["content"]
        else:
            # Multiple messages - combine into conversation format
            # This preserves the conversation history for context
            input_text = "\n\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

        # Call GPT-5 with reasoning and verbosity parameters
        response = await asyncio.to_thread(
            client.responses.create,
            model=model,
            input=input_text,
            reasoning={"effort": config["reasoning_effort"]},  # minimal/low/medium/high
            text={"verbosity": config["verbosity"]}            # low/medium/high
        )

        # === Extract text from GPT-5 response ===
        # Method 1: Try the simple output_text property (most straightforward)
        if hasattr(response, "output_text") and response.output_text:
            return response.output_text

        # Method 2: Parse the output items manually
        # GPT-5 response.output is a list that may contain:
        # - Reasoning items (showing model's thinking process)
        # - Message items (the actual output text)
        # - Tool call items (if tools were used)
        output_text = ""
        if hasattr(response, "output") and response.output:
            for item in response.output:
                # Check if this is a message/content item (contains the actual text)
                if hasattr(item, "type") and item.type == "message":
                    if hasattr(item, "content") and item.content is not None:
                        # Content may have multiple parts (text, images, etc.)
                        for content in item.content:
                            if hasattr(content, "text") and content.text is not None:
                                output_text += content.text
                # Some responses might have direct text property
                elif hasattr(item, "text") and item.text is not None:
                    output_text += item.text

        # Method 3: Fallback for debugging if extraction failed
        if not output_text:
            print(f"Warning: Could not extract text from GPT-5 response. Response structure: {response}")
            return str(response)

        return output_text
    else:
        # === GPT-4o and other models PATH: Use standard chat completion ===
        # Uses LiteLLM's completion function which works with various providers
        response = await asyncio.to_thread(
            litellm.completion,
            model=model,
            messages=messages,
            stream=False  # Get complete response at once (not streaming)
        )

        # Standard response format: response.choices[0].message.content
        return response.choices[0].message.content


async def write_multi_day_story(
    initial_prompt: str,
    num_days: int = 3,
    output_file: str = None,
    story_start_date: str = None
):
    """
    Write a story spanning multiple days with storyboard planning, character development, and specific dates.

    Args:
        initial_prompt: The initial story setup/premise
        num_days: Number of days to write (default: 3)
        output_file: Path to save the story markdown file (default: auto-generated)
        story_start_date: Start date for the story in YYYY-MM-DD format (default: auto-generated)
    """
    print("=== Story Writer Agent (OpenAI via LiteLLM) ===\n")

    # Load OpenAI configuration
    config = load_openai_config()
    model = setup_litellm(config)

    print(f"Writing a {num_days}-day story based on: {initial_prompt}\n")
    print("="*70 + "\n")

    # === Determine story start date ===
    # Either use provided date or generate a semi-random realistic date
    if story_start_date is None:
        # Use hash of prompt to generate consistent but varied dates
        # Hash ensures same prompt always gets same date (reproducible)
        base_date = datetime.now()
        offset_days = (hash(initial_prompt) % 365) - 180  # Random date within ±6 months
        start_date = base_date + timedelta(days=offset_days)
    else:
        # Parse user-provided date string
        start_date = datetime.strptime(story_start_date, "%Y-%m-%d")

    story_start_str = start_date.strftime("%B %d, %Y")
    print(f"📅 Story starts on: {story_start_str}\n")

    # === Prepare output file ===
    if output_file is None:
        # Generate filename with timestamp to avoid overwrites
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"story_openai_{timestamp}.md"

    output_path = Path(output_file)
    story_content = []  # Will accumulate all story sections

    # === Initialize conversation history ===
    # Manually track conversation to maintain context across multiple API calls
    # This allows the model to reference previous days when writing new content
    conversation_history = []

    # === STEP 1: Generate storyboard with character details ===
    print("📋 CREATING STORYBOARD & CHARACTER PROFILES\n")

    # Create prompt for storyboard generation
    # This prompt asks the model to plan the entire story before writing it
    storyboard_prompt = f"""Based on this story premise: "{initial_prompt}"

Create a detailed storyboard and character profiles for a {num_days}-day story starting on {story_start_str}.

Please provide:

1. **Character Profiles**: For each main character, include:
   - Full name
   - Age
   - Birthday (specific date, make it realistic relative to their age)
   - Brief backstory (2-3 sentences covering their background, personality, and what led them to this point)
   - Key personality traits

2. **Story Storyboard**: Create a high-level outline of what will happen across all {num_days} days:
   - Major plot points and events for each day
   - Character development arcs
   - Key conflicts and resolutions
   - How the story builds and progresses day by day
   - Emotional beats and turning points

Format this as a structured plan that we'll follow when writing the full story. Be specific about what happens on which day, using actual dates starting from {story_start_str}."""

    # Add storyboard request to conversation history
    conversation_history.append({"role": "user", "content": storyboard_prompt})

    # Call LLM to generate storyboard
    storyboard_text = await call_llm(model, conversation_history, config)
    print(storyboard_text)
    print("\n" + "="*70 + "\n")

    # Save storyboard to conversation history for context in later calls
    conversation_history.append({"role": "assistant", "content": storyboard_text})

    # === Build story file header with metadata ===
    story_content.append(f"# {initial_prompt}\n\n")
    story_content.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  \n")
    story_content.append(f"*Story Duration: {num_days} days*  \n")
    story_content.append(f"*Story Start Date: {story_start_str}*  \n")
    story_content.append(f"*Provider: {config['provider']} | Model: {config['model']}*\n\n")
    story_content.append("---\n\n")

    # === Add storyboard section to output ===
    story_content.append("## Story Planning\n\n")
    story_content.append(storyboard_text + "\n\n")
    story_content.append("---\n\n")
    story_content.append("## The Story\n\n")

    # === STEP 2: Write each day following the storyboard ===
    # Loop through each day and generate detailed narrative based on storyboard
    for day_num in range(1, num_days + 1):
        # Calculate the actual date for this story day
        current_date = start_date + timedelta(days=day_num - 1)
        date_str = current_date.strftime("%B %d, %Y (%A)")  # e.g., "July 21, 2025 (Monday)"

        # Create prompt for this day's narrative
        # References the storyboard to maintain continuity
        day_prompt = f"""Now write the full narrative for Day {day_num} ({date_str}) following the storyboard plan.

Include:
- Rich, detailed prose with character thoughts and emotions
- Specific times and activities throughout the day (morning, afternoon, evening, night)
- Dialogue that reveals character personalities
- Sensory details and atmospheric descriptions
- How events align with the character backstories and the overall storyboard

Make this engaging literary fiction, not just a summary. Write it as a complete narrative section."""

        print(f"📖 DAY {day_num} - {date_str}\n")
        story_content.append(f"### Day {day_num}: {date_str}\n\n")

        # Add day prompt to conversation
        conversation_history.append({"role": "user", "content": day_prompt})

        # Generate the day's narrative
        day_text = await call_llm(model, conversation_history, config)
        print(day_text)

        # Save the day's narrative to conversation history
        # This allows future days to reference what happened on previous days
        conversation_history.append({"role": "assistant", "content": day_text})

        # Add day's narrative to story content
        story_content.append(day_text + "\n\n")
        print("\n" + "="*70 + "\n")

    # === Write complete story to file ===
    output_path.write_text("".join(story_content), encoding="utf-8")
    print(f"✅ Story complete! Saved to: {output_path.absolute()}\n")

    # Display date range summary
    end_date_str = (start_date + timedelta(days=num_days-1)).strftime('%B %d, %Y')
    print(f"📊 Story spanned from {story_start_str} to {end_date_str}\n")


async def interactive_story_writer():
    """
    Interactive mode - prompts user for story parameters via command line.

    Asks the user to provide:
    - Story premise/setup
    - Number of days for the story to span

    Uses default values if user provides empty input.
    """
    print("=== Interactive Story Writer (OpenAI) ===\n")

    # Get story premise from user
    print("Enter your story premise (e.g., 'A detective solving a mysterious case in Tokyo'):")
    initial_prompt = input("> ").strip()

    if not initial_prompt:
        # Use default if no input provided
        initial_prompt = "A software developer discovers a mysterious bug that seems to change reality"
        print(f"Using default premise: {initial_prompt}")

    # Get number of days from user
    print("\nHow many days should the story span?")
    try:
        num_days = int(input("> ").strip())
    except ValueError:
        # Use default if invalid input
        num_days = 3
        print(f"Using default: {num_days} days")

    print()
    # Generate the story with user-provided parameters
    await write_multi_day_story(initial_prompt, num_days)


if __name__ == "__main__":
    # Main entry point - choose between interactive mode or hardcoded story

    # Option 1: Interactive mode - prompts for user input
    # Uncomment the line below to use interactive mode
    asyncio.run(interactive_story_writer())

    # Option 2: Hardcoded story example - runs immediately with predefined parameters
    # This is useful for testing or automated story generation
    # asyncio.run(write_multi_day_story(
    #     initial_prompt="A 5 year old boy was playing outdoors when he falls and breaks his ankle. He loves to play his xbox and gets to play it while he is healing.",
    #     num_days=7
    # ))

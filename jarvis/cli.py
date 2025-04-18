#!/usr/bin/env python3
"""
Jarvis CLI - A command-line interface for an AI assistant powered by Ollama.

This script implements a CLI for interacting with an AI assistant named Jarvis.
Jarvis can understand user requests, generate and execute code, and attempt to
correct itself when code execution fails.

SECURITY WARNING: This implementation executes code directly, which poses
significant security risks. Future versions will implement proper sandboxing.
"""

import os
import sys
from typing import Dict, List, Tuple, Optional, Any

from jarvis.config import get_config
from jarvis.core.memory import Memory
from jarvis.core.ollama import OllamaClient, format_chat_history
from jarvis.core.executor import execute_code
from jarvis.tools.search import search_web, PerplexicaClient
from jarvis.tools.workspace import get_workspace_state
from jarvis.utils.parsing import extract_code_blocks, extract_search_query, extract_focus_mode, is_search_request

def send_to_ollama(prompt: str, memory: Memory, system_prompt: Optional[str] = None) -> str:
    """Send a prompt to the Ollama API and return the response.
    
    Args:
        prompt: The prompt to send to Ollama.
        memory: The memory object.
        system_prompt: The system prompt to use.
        
    Returns:
        The response from Ollama.
    """
    # Search for relevant memories
    relevant_memories = memory.search_memories(prompt, limit=3)
    memories_str = "\n".join([f"- {entry['memory']}" for entry in relevant_memories])

    # Get workspace state
    workspace_state = get_workspace_state()

    # Create default system prompt if none is provided
    if system_prompt is None:
        system_prompt = f"""You are Jarvis, an AI assistant operating within a dedicated workspace.
Your goal is to help the user by generating Bash commands or Python code snippets.
If you need to run code, generate the complete code block needed for the immediate step.
If you can answer directly without code, do so.
Always output code clearly marked within markdown code blocks (e.g., ```bash ... ``` or ```python ... ```).
Remember that all code you generate will be executed in a specific workspace directory.

If you lack specific information (like the correct command-line arguments for a tool, current installation instructions for a package, or how to fix a specific error code), you should explicitly state your need for information and request a web search using the format:
SEARCH_WEB: "your search query here"

Current Workspace State:
```
{workspace_state}
```

Here are some relevant memories that might help you assist the user better:
{memories_str}
"""

    # Check if Ollama is available
    try:
        # Create an Ollama client
        client = OllamaClient()

        # Prepare the conversation history
        messages = format_chat_history(memory.get_conversation_history())

        # Add the current prompt
        messages.append({"role": "user", "content": prompt})

        # Send the request to Ollama
        response = client.chat(
            messages=messages,
            system=system_prompt,
            temperature=0.7,
            stream=False
        )

        # Extract the response content
        return response["message"]["content"]
    except Exception as e:
        print(f"Error communicating with Ollama: {e}")
        print("Falling back to mock implementation...")

        # Mock implementation for testing when Ollama is not available
        if "temperature" in prompt.lower() and "graph" in prompt.lower():
            return """I'll create a Python script that analyzes temperature data and plots a trend graph. Then I'll search for information about climate change.

```python
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Generate some sample temperature data
days = 365  # One year of data
base_temp = 15  # Base temperature in Celsius
seasonal_amplitude = 10  # Seasonal variation amplitude
warming_trend = 0.005  # Warming trend per day (about 1.8°C per year)
noise_level = 2  # Random daily fluctuations

# Generate dates and temperatures
start_date = datetime(2022, 1, 1)
dates = [start_date + timedelta(days=i) for i in range(days)]

# Calculate temperatures with seasonal variation, warming trend, and noise
temperatures = []
for i in range(days):
    seasonal = seasonal_amplitude * np.sin(2 * np.pi * i / 365)  # Seasonal cycle
    trend = warming_trend * i  # Warming trend
    noise = noise_level * np.random.randn()  # Random fluctuations
    temp = base_temp + seasonal + trend + noise
    temperatures.append(temp)

# Convert dates to a format suitable for plotting
date_strings = [date.strftime('%Y-%m-%d') for date in dates]

# Create the plot
plt.figure(figsize=(12, 6))

# Plot the daily temperatures
plt.plot(date_strings, temperatures, 'b-', alpha=0.5, label='Daily Temperature')

# Calculate and plot the moving average (30-day window)
window_size = 30
moving_avg = np.convolve(temperatures, np.ones(window_size)/window_size, mode='valid')
moving_avg_dates = date_strings[window_size-1:]
plt.plot(moving_avg_dates, moving_avg, 'r-', linewidth=2, label='30-day Moving Average')

# Calculate and plot the trend line
x = np.arange(days)
y = base_temp + warming_trend * x
plt.plot(date_strings, y, 'g--', linewidth=2, label=f'Warming Trend: {warming_trend*365:.2f}°C/year')

# Add labels and title
plt.xlabel('Date')
plt.ylabel('Temperature (°C)')
plt.title('Temperature Analysis with Trend')
plt.legend()

# Format the x-axis to show fewer date labels
plt.xticks(date_strings[::30], rotation=45)  # Show every 30th date
plt.tight_layout()

# Save the plot
plt.savefig('temperature_trend.png')

# Display some statistics
mean_temp = np.mean(temperatures)
min_temp = np.min(temperatures)
max_temp = np.max(temperatures)
temp_range = max_temp - min_temp

print(f"Temperature Statistics:")
print(f"Mean Temperature: {mean_temp:.2f}°C")
print(f"Minimum Temperature: {min_temp:.2f}°C")
print(f"Maximum Temperature: {max_temp:.2f}°C")
print(f"Temperature Range: {temp_range:.2f}°C")
print(f"Estimated Annual Warming Trend: {warming_trend*365:.2f}°C/year")

plt.show()
```

Now, let me search for information about climate change.

SEARCH_WEB: "latest climate change findings and impacts"""
        elif "search" in prompt.lower() and "climate change" in prompt.lower():
            return """Based on the search results, here's a summary of the latest findings on climate change:

### Key Climate Change Findings

1. **Global Temperature Rise**: Earth's average temperature has increased by about 1.1°C since pre-industrial times, with the last decade being the warmest on record.

2. **Causes**: The primary driver of climate change is human activities, particularly the burning of fossil fuels, which releases greenhouse gases like carbon dioxide and methane into the atmosphere.

3. **Current Impacts**:
   - Rising sea levels (about 3.3mm per year)
   - More frequent and intense extreme weather events (hurricanes, floods, droughts)
   - Shifting wildlife populations and habitats
   - Changes in plant flowering and growing seasons
   - Ocean acidification affecting marine ecosystems

4. **Future Projections**: If emissions continue at current rates, global temperatures could rise by 2.7°C to 3.1°C by 2100, far exceeding the Paris Agreement goal of limiting warming to 1.5°C.

5. **Mitigation Strategies**:
   - Transition to renewable energy sources
   - Improve energy efficiency
   - Reduce deforestation and increase reforestation
   - Adopt sustainable agricultural practices
   - Develop carbon capture technologies

6. **Adaptation Measures**:
   - Building resilient infrastructure
   - Improving water management systems
   - Developing drought-resistant crops
   - Creating early warning systems for extreme weather
   - Protecting and restoring natural ecosystems

The scientific consensus is clear that immediate and substantial action is needed to reduce greenhouse gas emissions to avoid the most severe impacts of climate change.

Would you like me to provide more specific information about any of these aspects of climate change?"""
        else:
            return f"I'll help you with: {prompt}\n\nWhat specific information or task would you like me to assist with?"


def handle_code_execution(code: str, language: str, memory: Memory, retries: int = 0) -> Tuple[str, bool]:
    """Handle the execution of code and potential retries.

    Args:
        code: The code to execute.
        language: The language of the code.
        memory: The memory object.
        retries: The number of retries attempted so far.

    Returns:
        A tuple (response_text, success).
    """
    max_retries = get_config("MAX_RETRIES", 2)
    print(f"\nExecuting {language} code...")

    # Execute the code
    stdout, stderr, return_code = execute_code(code, language)

    # Check if execution was successful
    if return_code == 0 and not stderr:
        memory.add_execution_result(code, language, stdout, stderr, True)
        return f"Execution successful:\n\n{stdout}", True

    # If we've reached the maximum number of retries, give up
    if retries >= max_retries:
        memory.add_execution_result(code, language, stdout, stderr, False)
        return f"I've tried {max_retries + 1} times, but I'm still encountering errors:\n\n{stderr}\n\nPlease provide more guidance.", False

    print(f"Execution failed. Analyzing error and retrying ({retries + 1}/{max_retries})...")

    # Prepare a prompt for self-correction
    correction_prompt = f"""I tried to execute the following {language} code:

```{language}
{code}
```

But I encountered this error:

```
{stderr}
```

Please analyze this error. Provide a corrected version of the code, or if you need more information to fix this, request a web search using the format:
SEARCH_WEB: "your search query about the error"
"""

    # Add the failed execution to memory
    memory.add_execution_result(code, language, stdout, stderr, False)

    # Get a corrected version of the code
    correction_response = send_to_ollama(correction_prompt, memory)
    memory.add_assistant_message(correction_response)

    # Check if the response contains a search request
    search_query = extract_search_query(correction_response)
    if search_query:
        # Handle the search request
        search_results = handle_search_request(search_query, memory)

        # Create a new prompt with the search results
        new_prompt = f"""I tried to execute the following {language} code:

```{language}
{code}
```

But I encountered this error:

```
{stderr}
```

You requested a web search for: {search_query}

Here are the search results:

{search_results}

Based on these search results, please provide a corrected version of the code."""

        # Get a new response from Ollama
        correction_response = send_to_ollama(new_prompt, memory)
        memory.add_assistant_message(correction_response)

    # Extract the corrected code
    corrected_code_blocks = extract_code_blocks(correction_response)

    if not corrected_code_blocks:
        return f"I couldn't generate a corrected version of the code. Here's the error I encountered:\n\n{stderr}", False

    # Use the first code block of the correct language
    for corrected_language, corrected_code in corrected_code_blocks:
        if corrected_language.lower() in [language.lower(), "bash", "shell", "sh", "python", "py"]:
            # Recursively try to execute the corrected code
            return handle_code_execution(corrected_code, corrected_language, memory, retries + 1)

    return f"I couldn't generate a corrected version of the code in {language}. Here's the error I encountered:\n\n{stderr}", False


def handle_search_request(query: str, memory: Memory, focus_mode: Optional[str] = None) -> str:
    """Handle a web search request.

    Args:
        query: The search query.
        memory: The memory object.
        focus_mode: The focus mode to use for the search.

    Returns:
        The search results as a formatted string.
    """
    # Use the default focus mode if none is specified
    if focus_mode is None:
        focus_mode = get_config("PERPLEXICA_FOCUS_MODE")

    print(f"\nSearching the web for: {query} (Focus Mode: {focus_mode})")

    try:
        # Create a Perplexica client
        client = PerplexicaClient()

        # Perform the search
        search_results = client.search(
            query=query,
            focus_mode=focus_mode
        )

        if not search_results or "message" not in search_results:
            return "I couldn't find any relevant information. Please try a different search query."

        # Format the results
        formatted_results = client.format_search_results(search_results)

        # Add the search results to memory
        memory.add_execution_result(
            f"SEARCH_WEB: \"{query}\" (Focus Mode: {focus_mode})",
            "web_search",
            formatted_results,
            "",
            True
        )

        return formatted_results
    except Exception as e:
        print(f"Error searching with Perplexica: {e}")
        print("Falling back to mock search results...")

        # Mock search results for testing when Perplexica is not available
        mock_results = f"""### Search Results for: {query}

**Result 1: Understanding {query}**
This is a mock search result for the query: {query}. It contains some information that might be relevant to the user's question.
Source: https://example.com/result1

**Result 2: More about {query}**
Another mock search result with different information about {query}. This could help answer the user's question.
Source: https://example.com/result2

**Result 3: {query} in depth**
A third mock result with additional details about {query}. This provides more context for the user.
Source: https://example.com/result3
"""

        # Add the mock search results to memory
        memory.add_execution_result(
            f"SEARCH_WEB: \"{query}\" (Focus Mode: {focus_mode})",
            "web_search",
            mock_results,
            "",
            True
        )

        return mock_results


def main():
    """Main function to run the Jarvis CLI."""
    workspace_dir = get_config("WORKSPACE_DIR")
    ollama_model = get_config("OLLAMA_MODEL")
    
    print("Jarvis CLI")
    print("==========")
    print(f"Using Ollama model: {ollama_model}")
    print(f"Workspace directory: {workspace_dir}")
    print("Type 'exit' or 'quit' to end the session.")
    print()

    memory = Memory()

    while True:
        try:
            # Get user input
            user_input = input("You: ")

            # Check if the user wants to exit
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            # Add the user input to memory
            memory.add_user_message(user_input)

            # Send the user input to Ollama
            response = send_to_ollama(user_input, memory)

            # Check if the response contains a search request
            search_query = extract_search_query(response)
            if search_query:
                # Extract focus mode from the query if specified
                focus_mode = extract_focus_mode(response)

                # Handle the search request
                search_results = handle_search_request(search_query, memory, focus_mode)

                # Create a new prompt with the search results
                new_prompt = f"""I asked you about: {user_input}

You requested a web search for: {search_query}

Here are the search results:

{search_results}

Based on these search results, please provide a response to my original question."""

                # Get a new response from Ollama
                response = send_to_ollama(new_prompt, memory)

                # Add a memory about the search
                memory.add_memory(f"Searched for '{search_query}' and found relevant information.")

            # Add the response to memory
            memory.add_assistant_message(response)

            # Print the response
            print("\nJarvis:", response.split("```")[0].strip())

            # Extract and execute code blocks
            code_blocks = extract_code_blocks(response)

            if code_blocks:
                for language, code in code_blocks:
                    execution_result, execution_success = handle_code_execution(code, language, memory)
                    print(f"\nExecution Result: {execution_result}")

                    # Add a memory about the code execution
                    if execution_success:
                        memory.add_memory(f"Successfully executed {language} code.")
                    else:
                        memory.add_memory(f"Failed to execute {language} code.")

            print()

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()

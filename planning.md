# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
Searches the mock listing dataset and returns items that match the user's description, size, and price limit. It filters by keyword matching agaist title, description,and style_tags, then by size and max_price.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `description` (str): keyword describing the item the user wants (e.g "vintage graphic tee") which is matched against the title, description, and style_tags
- `size` (str): the user's size (eg: "M") if none, no size is filtered
- `max_price` (float): maximum price the user will pay. If none, price is not filtered.

**What it returns:**
<!-- Describe the return value — what fields does a result contain? -->
A list of listing dicts(possible empty), each containing id, title, description, category, style_tags, size, condition, price, color, brand,platform. List is ordered by number of keyword matches (most relevant first).

**What happens if it fails or returns nothing:**
<!-- What should the agent do if no listings match? -->
Returns an empty list []. The agents detects this, sets an error message like "No listing found for '[description]'in size[size] and under $[max_price]. Try broader keywords, a different size or higher price and stops it does NOT call suggest_outfit with empty input.
---

### Tool 2: suggest_outfit

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
Takes a specific listing item and the user's current wardrobe, then calls the LLM to suggest one or more complete outfit combinations using pieces from the wardrobe paired with the new item. Retursn styling advice as a natural language string.
**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `new_item` (dict): a single listing dict from search_listings(has fields like title, category, style_tags, color, condition etc)
- `wardrobe` (dict): the user's wardrobe in the format {"items":[...]} where each items has id, name, category, colors, style_tags, notes

**What it returns:**
<!-- Describe the return value -->
A non empty string containing one or more outfit suggestions eg"Pair this with your dark wash baggy jeans and clunky white sneakers for a 90s streetwear look. Add the black crossbody for an easy everyday fit"

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the wardrobe is empty or no outfit can be suggested? -->
Two failure modes to handle:
-> Empty Wardrobe(wardrobe["items] is []): don't crash instead prompt the LLM for general styling advice for the items without specific wardrobe pieces. Return something like "No wardrobe items found. Here is how people generally style this piece..."
-> LLM returns empty string: Return a fallback string like "Couldn't generate outfit suggestion - try again"

LLM prompt for this section:
You are a personal stylist. The user just found this thrifted item:
Title: {new_item['title']}
Style tags: {new_item['style_tags']}
Colors: {new_item['colors']}

Their current wardrobe contains:
{formatted list of wardrobe items}

Suggest 1-2 complete outfits using pieces from their wardrobe paired with the new item.
Be specific about which wardrobe pieces to combine. Keep it under 100 words.
---

### Tool 3: create_fit_card

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
Takes the outfit suggestions and the new ite, then calls LLM to generate short, casual , shareabe caption - the kind of things people would be able to post on Instagram or TikTok describing their thrifted fit. Should sound human and fun, not like a product description.
**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `outfit` (str): the outfit suggestion string returned by suggest_outfit
- `new_item` (dict): the listing dict(same one from search_listings) used to pull in real details like price, paltform,title for authentcity

**What it returns:**
<!-- Describe the return value -->
A non empty string, 1-3 sentences, casual social media caption styel. Should vary each time even for same input.

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the outfit data is incomplete? -->
Two failure modes:
-> Empty outfit string(outfit =="" or outfit.strip()==""): return an error string immediately without calling the LLM - "Cannot create fit card: outfit description is missing" 

--> LLM returns rempty string: returning fallback - "Couldn't generate fit card- try again" 
---
LLM prompt for this section:

You are writing a casual Instagram caption for a thrifted outfit.
The person just bought: {new_item['title']} for ${new_item['price']} from {new_item['platform']}
Their outfit: {outfit}

Write 1-3 sentences in a casual, lowercase, social media style.
Be specific about the item and price. Use 1-2 emojis max. 
Do NOT sound like a product description.
### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

---

## Planning Loop
This is the brain of the agent. 
Concept: The planning loop is a function that runs the tools in sequence BUT checks the result after each one before deciding to continue. Think of it like a series of gates:

Gate 1: Did search_listings find anything?
  → No: stop, tell user, return
  → Yes: continue to Gate 2

Gate 2: Did suggest_outfit return something useful?
  → No: stop, tell user, return  
  → Yes: continue to Gate 3

Gate 3: Did create_fit_card return something useful?
  → No: tell user fit card failed but show outfit suggestion
  → Yes: return everything to user

**How does your agent decide which tool to call next?**
<!-- Describe the logic your planning loop uses. What does it look at? What conditions change its behavior? How does it know when it's done? -->
The planning loop runs inside run_agent(query,wardrobe) in agent.py. It follows the exact conditional logic:

Step1: Parse the user's query to extract description, size, and max_price. Call search_listings(description,size, max_price). If results is [] then set session["error"] to a helpful message, set session["fit_card"] and session["outfit_suggestion"] to None, return session immediately. Do NOT proceed. But if the result is not empty set session["selected_item]= result[0] (top result) continue.

Step2: Call suggest_outfit(session["selected_item"],wardrobe). If the result is empty string: set session["error"] to "Outfit Suggestion failed", return session. DO NOT proceed. If the result is non empty string: set session["outfit_suggestion"] = result, continue

Step3: Call create_fit_card(session["outfit_suggestion"], session["selected_item"])
IF results is an error string: set session["error"] to result but KEEP session["outfit_suggestion"]- show the user the outfit suggestion even if the fit card has failed.
If result is non empty: set session["fit_card"] = result, return session



Why results[0]? The search returns a ranked list — most relevant first. The agent picks the top result automatically. In a real product you might let the user choose, but for this project picking the best match keeps the flow clean.

Why keep outfit_suggestion even if create_fit_card fails? Partial success is better than total failure. The user still gets something useful. This is a real design principle in agents — degrade gracefully, don't wipe out everything on one failure.
---

## State Management
The agent maintains the single session dict created at the start of run_agent(). 
It starts as:
session = {
    "query": query,
    "selected_item": None,
    "outfit_suggestion": None,
    "fit_card": None,
    "error": None
}




**How does information from one tool get passed to the next?**
<!-- Describe how your agent stores and accesses state within a session. What data is tracked? How is it passed between tool calls? -->
State flows like this:

After search_listings succeeds: session["selected_item"] is set to results[0]
suggest_outfit receives session["selected_item"] directly as its new_item argument
After suggest_outfit succeeds: session["outfit_suggestion"] is set to the returned string
create_fit_card receives both session["outfit_suggestion"] and session["selected_item"] as arguments
After create_fit_card succeeds: session["fit_card"] is set to the returned string
If any tool fails: session["error"] is set to a descriptive message

The completed session dict is returned from run_agent() and app.py maps each key to its output panel in the Gradio UI.

Why a dict instead of separate variables? A dict is easy to pass around, inspect, and return as one object. When run_agent() returns session, app.py can pull out exactly what it needs for each UI panel — search result, outfit suggestion, fit card — all from one object.

Why initialize everything to None? So app.py can always safely check session["fit_card"] without a KeyError, even if the agent stopped early. None means "this step didn't complete" which is different from an empty string or missing key.
---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | Set session["error"] = "No listings found for '[description]' in size [size] under $[max_price]. Try broader keywords, a different size, or a higher price limit." Return session immediately without calling further tools.|
| suggest_outfit | Wardrobe is empty | Don't crash — call LLM anyway with a modified prompt asking for general styling advice without referencing specific wardrobe pieces. Return general advice string|
| create_fit_card | Outfit input is missing or incomplete |Return error string immediately without calling LLM: "Cannot create fit card: outfit description is missing." Keep session["outfit_suggestion"] intact so user still sees the outfit suggestion. |

---

## Architecture

<!-- Draw a diagram of your agent showing how the components connect:
     User input → Planning Loop → Tools (search_listings, suggest_outfit, create_fit_card)
                                                                          ↕
                                                                   State / Session
     Show what triggers each tool, how state flows between them, and where error paths branch off.
     ASCII art, a Mermaid diagram (https://mermaid.js.org/syntax/flowchart.html), or an embedded
     sketch are all fine. You'll share this diagram with an AI tool when asking it to implement
     the planning loop and each individual tool. -->

---

## AI Tool Plan

<!-- For each part of the implementation below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, your agent diagram)
     - What you expect it to produce
     - How you'll verify the output matches your spec before moving on

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
     search_listings() using load_listings() from the data loader — then test it against 3 queries
     before trusting it" is a plan. -->

**Milestone 3 — Individual tool implementations:**

**Milestone 4 — Planning loop and state management:**

---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
<!-- What does the agent do first? Which tool is called? With what input? -->

**Step 2:**
<!-- What happens next? What was returned from step 1? What tool is called now? -->

**Step 3:**
<!-- Continue until the full interaction is complete -->

**Final output to user:**
<!-- What does the user actually see at the end? -->

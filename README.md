# Setup
1) Install Python 3.10
2) Get an API key from DeepAI
3) Have ChatGPT output a story as JSON list
4) Run the following command:
```bash
CHATGPT_API_KEY=<YOUR-KEY> DEEPAI_API_KEY=<YOUR-KEY> python3 generator.py --prompt "Write a story about teletubbies"
```
5) Note that output.gif exists now

## Simple ChatGPT story prompt
Generate a story about a hyacinth macaw going to college to become a doctor. In each sentence, talk about the hyacinth macaw. Do not include sentences without the phrase "hyacinth macaw". Each sentences in the paragraphs are shorter than 100 characters. Put each paragraph in a JSON list

### Future
Generate a build your novel own adventure
### ChatGPT prompt
Output in JSON a build your own adventure story about worms going to the moon using this JSON schema.  there should be at least 2 sub outcomes that have 1 outcomes. the worms are preppy: {"type":"object","properties":{"title":{"type":"string"},"plot":{"type":"object","properties":{"start":{"type":"object","properties":{"text":{"type":"string"},"choices":{"type":"array","items":{"type":"object","properties":{"text":{"type":"string"},"outcome":{"type":"object","properties":{"text":{"type":"string"},"end":{"type":"boolean"},"choices":{"type":"array","items":{"$ref":"#/properties/plot/properties/start/properties/choices/items"}}},"required":["text","end"]}},"required":["text","outcome"]}}},"required":["text","choices"]}},"required":["start"]}},"required":["title","plot"]}

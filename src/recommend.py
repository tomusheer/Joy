from src.llm_client import LLMClient


QUERY_TYPE_LABELS = {
    "generic": "Broad query",
    "brand": "Brand query",
    "brand_category": "Brand + category query",
    "feature": "Feature-led query",
    "specific": "Specific product query",
}


def build_prompt(query: str) -> str:
    return f"""
You are helping design e-commerce search refinement suggestions.

User search query: "{query}"

Primary goal:
Generate grouped refinement labels that are SAFE TO APPEND directly to the original query
for a new search.

Critical behavior:
When a user clicks a tile, the site will run:
original query + tile label

So every tile must work well as a direct query expansion term.

Return only labels that are likely to work well in real e-commerce search.

Core rules:
- Do NOT recommend unrelated products
- Do NOT recommend discounts, deals, promotions, or best sellers
- Do NOT return abstract marketing phrases
- Do NOT return vague benefit claims unless they are standard searchable product terms
- Prefer labels that are commonly found in:
  - product titles
  - product variant names
  - indexed attributes
  - category labels
  - brand series names
- Keep suggestions product-related only
- Keep output in the same language as the query when possible
- Each label should usually be 1 to 4 words
- Each group should contain 4 to 6 tiles
- Do not repeat the same tile across groups


Safe append-friendly label types:
- Brand
- Product Family
- Category
- Type
- Series
- Model
- Stage
- Pack Size
- Flavor
- Material
- Size
- Compatibility
- Gender
- Age / Stage
- Format
- Occasion
- Fit
- Use Case


Use caution with these:
- Need
- Concern
- Benefit
- Health outcome
- Lifestyle claim

Only use those if they are highly likely to appear as searchable catalog terms.

Brand-query rules:
- If the query is already a brand query, do NOT show a Brand group unless it adds new value
- For brand queries, replace Brand with stronger append-safe groups like:
  Series, Type, Stage, Pack Size, Compatibility, Format, Gender, Flavor, Occasion
- If Brand is hidden because this is a brand query, include a note
- For large multi-category brands, diversify across the brand's major product families instead of focusing on one flagship line
- If the brand spans multiple categories, include at least one group that reflects category breadth, such as Product Family or Category
- Avoid over-representing a single flagship category when the brand clearly sells across multiple categories

Apparel rules:
- For apparel queries like tshirt, jeans, dress, hoodie, shirt, trainers, sneakers:
  prioritize Gender, Type, Fit, Style, Occasion, Material
- Gender is often a strong grouping for broad apparel searches

Baby / formula rules:
- For baby formula or milk brands:
  strongly prefer Stage, Type, Series, Pack Size, Format
- Avoid weak claims like Brain Development or Eye Development unless these are standard
  searchable product terms in titles or attributes

Electronics rules:
- Prefer Brand, Type, Series, Compatibility, Feature
- Features must be concrete and searchable, like USB-C, Bluetooth 5.3, Noise Cancelling

Beauty rules:
- Prefer Brand, Type, Concern, Ingredient, Size
- Only use Concern if it is a standard search behavior on site

Food / grocery rules:
- Prefer Type, Flavor, Pack Size, Dietary Need, Format
- Only use benefit-style labels if clearly searchable in product titles or attributes

Output quality rules:
- Return 4 groups when they are strong and natural
- Return only 3 groups if a 4th would be weak
- Strong query-expansion labels are better than perfect taxonomy logic
- Think about what would retrieve good results if appended to the original query

Return JSON only in this structure:
{{
  "query": "{query}",
  "query_type": "generic|brand|brand_category|feature|specific",
  "notes": [
    "Brand grouping hidden because this is a brand query"
  ],
  "groups": [
    {{
      "header": "Stage",
      "tiles": ["Stage 1", "Stage 2", "Stage 3", "From Birth"]
    }},
    {{
      "header": "Type",
      "tiles": ["Infant Formula", "Follow On", "Toddler Milk", "Organic"]
    }},
    {{
      "header": "Series",
      "tiles": ["Profutura", "Advanced", "Organic", "Pepti"]
    }},
    {{
      "header": "Pack Size",
      "tiles": ["800g", "2x800g", "6 Pack", "900g"]
    }}
  ]
}}

Header guidance:
- Use concise headers like Brand, Type, Series, Stage, Pack Size, Compatibility,
  Gender, Fit, Style, Flavor, Format, Material, Occasion
- Avoid weak headers like Other, More, Benefit unless clearly justified

Final instruction:
Before returning each tile, ask:
"If this label is appended to the original query, is it likely to improve retrieval on an e-commerce site?"
If no, do not include it.
"""


def get_recommendations(query: str):
    client = LLMClient()
    prompt = build_prompt(query)
    result = client.generate_json(prompt)

    if "query_type" in result:
        result["query_type_label"] = QUERY_TYPE_LABELS.get(
            result["query_type"], result["query_type"]
        )

    return result
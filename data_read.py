import pandas as pd
import os
import uuid
from collections import defaultdict
import spacy
nlp = spacy.load('en_core_web_sm')
from collections import Counter
import inflect
p = inflect.engine()

# Load data with openpyxl engine
df = pd.read_excel(
    r"C:\Users\PatrickStewart\OneDrive - Fable Data Ltd\Customer Review Platform\output_data\product_processed.xlsx",
    engine='openpyxl'
)

# Generate a unique review_id
df['review_id'] = df.apply(lambda x: str(uuid.uuid4()), axis=1)

# Split sentiments into a list
df['sentiment_list'] = df['sentiments'].str.split(', ')

# Mapping sentiments to numerical values
sentiment_map = {
    'Positive': 1,
    'Negative': -1,
    'Neutral': 0
}

# Explode the sentiments column
df_exploded_sentiments = df.explode('sentiment_list')
df_exploded_sentiments['sentiment_value'] = df_exploded_sentiments['sentiment_list'].map(sentiment_map)

# Calculate the normalized sentiment score by averaging
df_normalized = df_exploded_sentiments.groupby('review_id')['sentiment_value'].mean().reset_index()

# Correct column renaming
df_normalized.columns = ['review_id', 'normalized_sentiment_score']

# Optional: Merge rating back into the normalized DataFrame
df_normalized = pd.merge(df_normalized, df[['review_id', 'rating','submission_time']], on='review_id', how='left')

# Save the result
df_normalized.to_csv(r'C:\Users\PatrickStewart\OneDrive - Fable Data Ltd\Customer Review Platform\Customer-review-platform\data\whole_review_sentiments.csv', index=False)

### Aspect term generation
# Step 1: Generate Unique Review IDs
# Step 2: Explode aspect_terms and sentiments
df_exploded = df.assign(
    aspect_terms=df["aspect_terms"].str.lower().str.split(", "),
    sentiments=df["sentiments"].str.lower().str.split(", ")
).explode(["aspect_terms", "sentiments"])

# Step 3: Create a separate DataFrame for aspects and sentiments
aspect_df = df_exploded[['review_id', 'aspect_terms', 'sentiments']].dropna().reset_index(drop=True)

# Step 4: Drop aspect and sentiment columns from the original DataFrame
review_df = df.drop(columns=['aspect_terms', 'sentiments'])

# Step 5: Check and create output directory
output_dir = './output_data'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

print("Data transformation complete. Files saved in ./output_data/")

# Step 7: Now with this data 
# Load SpaCy model
# Normalize and Lemmatize Aspect Terms
def normalize(text):
    doc = nlp(text)
    return " ".join([token.lemma_ for token in doc if not token.is_stop])

# Apply normalization
aspect_df['normalized_aspects'] = aspect_df['aspect_terms'].apply(lambda x: normalize(x.lower()))

# Reduce plurality from aspects
aspect_df['normalized_aspects'] = aspect_df['normalized_aspects'].apply(lambda x: p.singular_noun(x) or x)

# Step 7: Let's start with that but combine a bit more
synonym_dict = {
    'hydration': ['moisturize', 'moisturizing', 'moisturizer', 'hydrating', 'quenching', 'replenishing'],
    'lip': ['lips', 'lipstick', 'lip balm', 'lip gloss', 'lip tint', 'lip liner', 'lip plumper', 'lip mask', 'lip sleeping mask', 'lippy', 'lip jelly'],
    'scent': ['fragrance', 'smell', 'aroma', 'perfume', 'eau de toilette', 'eau de parfum', 'scents', 'sweet candy scent', 'berry smell', 'grapefruit', 'smells'],
    'foundation': ['base', 'makeup foundation', 'liquid foundation', 'powder foundation', 'stick foundation'],
    'cleanser': ['face wash', 'facial cleanser', 'cleaning gel', 'foam cleanser', 'cleansing oil', 'micellar water', 'clean balm', 'makeup melt', 'melt'],
    'cream': ['lotion', 'moisturizer', 'ointment', 'balm', 'body butter', 'night cream', 'day cream', 'vasaline', 'aquaphor', 'butter'],
    'blush': ['rouge', 'cheek color', 'blusher', 'cheek tint'],
    'eyeliner': ['kohl', 'eye pencil', 'liquid liner', 'gel liner', 'felt tip liner'],
    'mascara': ['lash enhancer', 'lash lengthener', 'volumizing mascara', 'curling mascara', 'waterproof mascara'],
    'powder': ['face powder', 'setting powder', 'translucent powder', 'compact powder', 'loose powder'],
    'shadow': ['eyeshadow', 'eye shadow', 'eye pigment', 'shadow palette', 'cream eyeshadow'],
    'nail polish': ['nail lacquer', 'nail varnish', 'gel polish', 'top coat', 'base coat'],
    'anti aging': ['anti wrinkle', 'age defying', 'youthful', 'age reversing', 'mature skin'],
    'oil control': ['matte', 'shine free', 'oil free', 'oil absorbing', 'mattifying'],
    'sunscreen': ['sunblock', 'SPF', 'sun protection', 'broad spectrum', 'UV defense', 'jack black spf lip balm'],
    'acne treatment': ['blemish control', 'pimple cream', 'spot treatment', 'acne serum', 'anti acne'],
    'exfoliator': ['scrub', 'peel', 'exfoliant', 'microdermabrasion', 'chemical exfoliant'],
    'toner': ['astringent', 'skin tonic', 'face mist', 'balancing toner'],
    'serum': ['essence', 'ampoule', 'concentrate', 'booster', 'treatment serum'],
    'mask': ['facial mask', 'face mask', 'sheet mask', 'clay mask', 'overnight mask', 'peel off mask', 'sleeping mask', 'lip mask', 'gummy bear mask', 'masque de'],
    'primer': ['makeup base', 'foundation primer', 'pore filler', 'smoothing primer'],
    'highlighter': ['illuminator', 'shimmer', 'glow stick', 'strobing cream'],
    'concealer': ['cover up', 'blemish stick', 'corrector', 'under eye concealer'],
    'bronzer': ['tanning powder', 'sun powder', 'contour powder', 'bronzing gel'],
    'palette': ['makeup palette', 'color palette', 'shadow palette', 'face palette'],
    'gloss': ['lip gloss', 'shine', 'lip lacquer', 'lip topper'],
    'matte': ['non shiny', 'flat finish', 'velvet matte', 'matte lipstick'],
    'peel': ['exfoliant', 'skin peel', 'chemical peel', 'peel off mask'],
    'whitening': ['brightening', 'lightening', 'skin tone corrector', 'fade cream'],
    'pore minimizer': ['pore reducer', 'pore refiner', 'pore tightener'],
    'firming': ['tightening', 'lifting', 'elasticity booster', 'sculpting'],
    'soothing': ['calming', 'relaxing', 'anti redness', 'cooling'],
    'renewal': ['regeneration', 'revitalization', 'skin turnover', 'cell renewal'],
    'clarifying': ['purifying', 'cleansing', 'detoxifying', 'balancing'],
    'detoxifying': ['detox', 'cleansing', 'purging', 'clarifying'],
    'volumizing': ['thickening', 'plumping', 'body boosting', 'fullness enhancer'],
    'straightening': ['smoothing', 'de frizzing', 'sleekening', 'hair relaxing'],
    'curling': ['wave enhancing', 'curl enhancer', 'curl defining', 'curl booster'],
    'coloring': ['dyeing', 'tinting', 'color depositing', 'hair color'],
    'hydrating': ['moisturizing', 'nourishing', 'replenishing', 'water locking'],
    'brightening': ['illuminating', 'lightening', 'radiance boosting', 'glow enhancing'],
    'smoothing': ['softening', 'refining', 'texture improvement', 'polishing'],
    'refreshing': ['revitalizing', 'energizing', 'cooling', 'rejuvenating'],
    'balancing': ['harmonizing', 'stabilizing', 'pH balancing', 'oil control'],
    'nourishing': ['feeding', 'enriching', 'replenishing', 'revitalizing'],
    'repairing': ['restorative', 'healing', 'damage reversing', 'rebuilding'],
    'protecting': ['shielding', 'guarding', 'barrier strengthening', 'defending'],
    'softening': ['smoothing', 'supple', 'velvety', 'silkening'],
    'conditioning': ['treating', 'nurturing', 'moisturizing', 'softening'],
    'defining': ['shaping', 'outlining', 'sculpting', 'contouring'],
    'enhancing': ['improving', 'boosting', 'amplifying', 'accentuating'],
    'lengthening': ['extending', 'elongating', 'stretching', 'length boost'],
    'plumping': ['filling', 'volumizing', 'enhancing fullness', 'plump effect'],
    'radiance': ['glow', 'luminosity', 'brightness', 'sheen'],
    'resurfacing': ['renewing', 'exfoliating', 'smoothing', 'skin turnover'],
    'revitalizing': ['refreshing', 'energizing', 'rejuvenating', 'awakening'],
    'sensitivity': ['gentle', 'mild', 'hypoallergenic', 'calming'],
    'shine': ['gloss', 'luster', 'sheen', 'polish'],
    'strengthening': ['fortifying', 'reinforcing', 'hair repair', 'protein treatment'],
    'tint': ['shade', 'hue', 'color wash', 'stain'],
    'waterproof': ['water resistant', 'smudge proof', 'long lasting', 'sweat proof'],
    'wrinkle': ['line', 'crease', 'fine line', 'expression line'],
    'youthful': ['young', 'age defying', 'anti aging', 'youth boosting'],
    'packaging': ['container', 'tub', 'application', 'applicator', 'spatula'],
    'formula': ['texture', 'feeling'],
    'laneige': ['laniege', 'minis'],
    'price': ['money'],
    'ingredients': ['bht', 'product'],
    'color': ['colour', 'tint', 'shade'],
    'makeup': ['cosmetics'],
    'environment': ['eco friendly'],
}

# Step 8: Apply the grouping to that
# Function to normalize and categorize aspect terms
def categorize_aspect(aspect, synonym_dict):
    for category, synonyms in synonym_dict.items():
        if aspect in synonyms or aspect == category:
            return category
    return 'other'

# Apply the lexicon to categorize aspect terms
aspect_df['normalized_aspects'] = aspect_df['aspect_terms'].apply(lambda x: categorize_aspect(x.lower(), synonym_dict))
# Count the occurrences of each category
aspect_counts = aspect_df.groupby(by=["normalized_aspects", "sentiments"]).size().reset_index(name="Count")
# Display the counts
aspect_counts.to_csv(r'C:\Users\PatrickStewart\OneDrive - Fable Data Ltd\Customer Review Platform\Customer-review-platform\data\aspect_counts.csv')


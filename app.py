import gradio as gr
import pandas as pd
import random
import threading
import time

# --- Load dataset ---
df = pd.read_csv("amazon_eco-friendly_products.csv")

# --- Clean price column ---
def clean_price(price_str):
    try:
        if isinstance(price_str, str) and "$" in price_str:
            return float(price_str.replace("$", "").strip())
        return float(price_str)
    except:
        return None

df["price"] = df["price"].apply(clean_price)
df = df.dropna(subset=["price"])

# --- Environmental quotes ---
quotes = [
    "🌍 Small choices, big changes.",
    "♻️ Every eco-friendly swap plants a seed for tomorrow.",
    "🌱 A bamboo brush today keeps plastic away.",
    "🌿 Be the change you shop for.",
    "🌎 Plastic lasts 500 years, your choice lasts forever.",
    "💧 Save water, save life.",
    "🌞 Renewable is reliable.",
    "🍃 The Earth doesn’t need more stuff, it needs better stuff.",
    "🌏 Consume less, choose wise.",
    "🌲 A greener choice is a cleaner future.",
    "🌍 You don’t need to be perfect, just better than yesterday.",
    "🌱 One toothbrush less, a million smiles more.",
    "♻️ What you buy today builds tomorrow.",
    "🌿 Nature is not a place to visit, it’s home.",
    "🌞 Sustainable is beautiful.",
    "🌊 Every drop counts; save water, save life.",
    "🍀 Eco choices today are gifts for tomorrow.",
    "🌟 Green living is smart living.",
    "💚 Protect the planet, protect yourself.",
    "🌺 A cleaner Earth starts with mindful habits.",
    "🌾 Small eco steps create huge impact.",
    "🌐 Go green, think global, act local.",
    "🔥 Reduce waste, light the path for future generations.",
    "🍎 Eat consciously, live sustainably.",
    "🌸 Nature thrives when you choose wisely.",
    "🌙 Less consumption, more conservation.",
    "💡 Energy saved is a planet saved.",
    "🌻 Plant trees, grow hope.",
    "🌱 Minimalism is sustainability in action.",
    "🌏 Care for the Earth—it’s the only home we have.",
    "♻️ Waste less, live more.",
    "🌿 Green habits, brighter future.",
    "💧 Clean water, clear conscience.",
    "🌞 Sun-powered is future-powered.",
    "🌍 Your choices echo through generations.",
    "🌲 Forests are worth more than gold—protect them.",
    "🍃 Reduce, reuse, rethink.",
    "🌸 Live lightly, tread softly.",
    "🌾 Sustainability is love for the next generation.",
    "💚 Small actions, massive change."
]

# --- Impact messages ---
impacts = {
    "bamboo toothbrush": "By choosing a bamboo brush, you prevent ~4 plastic brushes a year from ending in landfills.",
    "reusable bottle": "One reusable bottle saves ~1,460 plastic bottles a year.",
    "eco bag": "A single reusable bag replaces ~700 plastic bags annually.",
    "solar light": "Solar lights cut down ~90kg CO₂ emissions per year.",
    "compostable plates": "Using compostable plates diverts hundreds of plastic plates from landfills yearly.",
    "beeswax wrap": "Replacing plastic wrap with beeswax saves ~200 feet of plastic wrap per year.",
    "stainless steel straw": "One reusable straw prevents ~500 plastic straws from polluting oceans annually.",
    "reusable coffee cup": "Switching to a reusable cup saves ~400 disposable cups yearly.",
    "LED bulb": "Using LED bulbs reduces ~150kg CO₂ emissions per year compared to incandescent bulbs.",
    "bamboo cutlery": "One set of bamboo cutlery prevents ~100 plastic utensils from entering landfills each year.",
    "recycled notebook": "Using recycled notebooks saves ~12 trees per 100 notebooks produced.",
    "eco-friendly detergent": "Switching to eco detergent reduces harmful chemicals in water, saving aquatic life.",
    "solar charger": "Solar chargers reduce dependency on grid electricity, cutting ~100kg CO₂ annually.",
    "reusable food container": "One container saves ~200 plastic bags and wraps per year.",
    "water-saving showerhead": "Water-saving showerheads save ~30,000 liters of water annually per household.",
    "eco soap": "Using biodegradable soap prevents harmful chemicals from entering rivers and oceans.",
    "bamboo mat": "Bamboo mats reduce plastic and synthetic mat usage, saving the environment.",
    "recycled toilet paper": "One roll of recycled toilet paper saves ~17 trees compared to virgin paper.",
    "energy-efficient appliances": "Switching to energy-efficient appliances reduces electricity consumption significantly.",
    "organic cotton clothing": "Choosing organic cotton avoids ~5,000 liters of water per kg of fabric.",
    "plant-based cleaning products": "Plant-based cleaners reduce chemical pollution in water systems.",
    "reusable sandwich wrap": "One wrap replaces hundreds of single-use plastic sandwich bags yearly.",
    "eco shampoo bar": "Shampoo bars save ~2 plastic bottles per year per person.",
    "bamboo hairbrush": "Using a bamboo hairbrush prevents plastic brush pollution in landfills.",
    "recycled packaging": "Products with recycled packaging save trees and reduce plastic waste.",
    "biodegradable trash bags": "Switching to biodegradable trash bags reduces plastic landfill waste annually.",
    "solar water heater": "Solar water heaters reduce electricity demand and cut CO₂ emissions.",
    "compost bin": "Composting kitchen waste reduces methane emissions from landfills.",
    "eco toothpaste": "Eco toothpaste tubes save ~1 plastic tube per person every month.",
    "reusable menstrual products": "Reusable pads or cups reduce ~240 disposable items per person per year.",
    "energy-saving power strip": "Using smart strips prevents phantom energy waste from electronics.",
    "bamboo kitchenware": "Bamboo utensils replace plastic alternatives, reducing landfill waste.",
    "eco laundry bag": "Using reusable laundry bags reduces microplastic pollution from synthetic clothes.",
    "recycled pens": "One recycled pen saves ~5 plastic pens from going to landfill.",
    "bamboo sunglasses": "Bamboo sunglasses reduce reliance on plastic frames, saving the environment.",
    "solar backpack": "Solar backpacks charge devices sustainably without electricity.",
    "eco yoga mat": "Eco-friendly yoga mats reduce PVC usage and chemical pollution.",
    "compostable cutlery": "Switching prevents hundreds of plastic utensils from polluting landfills.",
    "biodegradable soap wrapper": "Prevents plastic from entering oceans and decomposes naturally.",
    "recycled water bottle": "Recycled bottles save energy and reduce plastic production.",
    "bamboo tissue box": "Bamboo alternatives reduce plastic waste and promote sustainable forestry.",
    "eco dish brush": "Using a bamboo dish brush prevents plastic waste from entering landfills."
}

# --- State ---
shown_products = []
batch_size = 9

# --- Product rendering ---
def render_products(products):
    if products.empty:
        return "<div class='card'>❌ No products found.</div>"

    html = ""
    for _, row in products.iterrows():
        title = row.get("title", "Unknown Product")
        if len(title) > 50:
            title = title[:47] + "..."
        price = f"${row['price']:.2f}" if row.get("price") else "N/A"
        rating = row.get("rating", "N/A")
        url = row.get("url", "#")
        category = row.get("category", "Eco Product")
        in_stock_text = row.get("inStockText", "")
        description = row.get("description", "No description available.")
        if len(description) > 150:
            description = description[:147] + "..."

        # Impact message
        impact_msg = ""
        for key, msg in impacts.items():
            if key in str(title).lower():
                impact_msg = f"<div class='impact'>{msg}</div>"

        img_html = f"<img src='{row['img_url']}' style='width:120px; height:120px; object-fit:cover; border-radius:10px;'/>" if row.get("img_url") else ""

        html += f"""
        <div class="card" title="Rating: {rating}" data-desc="{description}">
            {img_html}
            <h3>{title}</h3>
            <p class="price">{price}</p>
            <p class="category">Category: {category}</p>
            <p>{in_stock_text}</p>
            {impact_msg}
            <a href="{url}" target="_blank">View Product</a>
        </div>
        """
    return f"<div class='grid-container'>{html}</div>"

# --- Filters, search, sort ---
def get_filtered_products(category="All", sort_by="Rating", min_price=0, max_price=1000, in_stock=False, query=""):
    products = df.copy()

    if category != "All":
        products = products[products["category"].str.contains(category, case=False, na=False)]

    if query:
        products = products[
            products["title"].str.contains(query, case=False, na=False) |
            products["brand"].str.contains(query, case=False, na=False) |
            products["category"].str.contains(query, case=False, na=False)
        ]

    products = products[(products["price"] >= min_price) & (products["price"] <= max_price)]

    if in_stock:
        products = products[products["inStock"] == True]

    if sort_by == "Price: Low to High":
        products = products.sort_values("price", ascending=True)
    elif sort_by == "Price: High to Low":
        products = products.sort_values("price", ascending=False)
    elif sort_by == "Rating":
        products = products.sort_values("rating", ascending=False)

    return products

def show_products(category, sort_by, min_price, max_price, in_stock, query):
    global shown_products
    products = get_filtered_products(category, sort_by, min_price, max_price, in_stock, query)
    shown_products = products.head(batch_size)
    return render_products(shown_products)

def load_more(category, sort_by, min_price, max_price, in_stock, query):
    global shown_products
    products = get_filtered_products(category, sort_by, min_price, max_price, in_stock, query)
    already_shown_ids = set(shown_products["id"]) if not pd.DataFrame(shown_products).empty else set()
    remaining = products[~products["id"].isin(already_shown_ids)]
    if remaining.empty:
        return render_products(shown_products)
    next_batch = remaining.head(batch_size)
    shown_products = pd.concat([pd.DataFrame(shown_products), next_batch])
    return render_products(shown_products)

# --- Random products on start ---
def show_random_products():
    global shown_products
    shown_products = df.sample(n=batch_size)
    return render_products(shown_products)

# --- Quote Slideshow ---
current_quote = [random.choice(quotes)]

def get_quote():
    return f"<div class='quote-box'>{current_quote[0]}</div>"

def cycle_quotes():
    while True:
        current_quote[0] = random.choice(quotes)
        time.sleep(5)

threading.Thread(target=cycle_quotes, daemon=True).start()

# --- Gradio UI ---
with gr.Blocks(css="""
body {background: #0d1117; color: #e6edf3; font-family: 'Segoe UI', sans-serif; margin:0; padding:0;}
.grid-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 15px;
    justify-items: center;
}
.card {
    backdrop-filter: blur(12px); 
    background: rgba(255,255,255,0.05); 
    border-radius: 16px; 
    padding: 20px; 
    box-shadow: 0 0 15px rgba(0,255,150,0.2); 
    transition: transform 0.2s ease; 
    width: 220px; 
    min-height: 320px;
    text-align:center; 
    position: relative;
    overflow: hidden;
}
.card:hover {transform: scale(1.05); box-shadow: 0 0 25px rgba(0,255,150,0.5);}
.card::after {
    content: attr(data-desc);
    position: absolute;
    background: rgba(0,0,0,0.9);
    color: #fff;
    padding: 10px;
    border-radius: 8px;
    font-size: 0.85em;
    white-space: normal;
    width: 250px;
    display: none;
    z-index: 1000;
}
.card:hover::after { display: block; }
.card:hover::after {
    top: 0;
    left: 100%;
    margin-left: 10px;
}
@media(max-width: 1024px) {
    .card:hover::after {
        left: auto;
        right: 100%;
        margin-left: 0;
        margin-right: 10px;
    }
}
@media(max-width: 767px) {
    .card:hover::after {
        position: static;
        display: block;
        width: auto;
        margin-top: 10px;
    }
}
h3 {font-size: 1.1em; margin: 5px 0; word-wrap: break-word;}
.price {color: #39ff14; font-weight: bold;}
a {color: #58a6ff; text-decoration: none;}
a:hover {text-decoration: underline;}
.quote-box {padding: 12px; margin: 10px 0; background: rgba(0,255,100,0.1); border-left: 4px solid #39ff14; font-style: italic; border-radius: 8px; text-align:center;}
.impact {color: #ffd700; margin-top: 6px; font-size: 0.9em;}
""") as demo:
    
    # Search & filters on top
    with gr.Row():
        query = gr.Textbox(label="Search")
        category = gr.Dropdown(["All"] + sorted(df["category"].dropna().unique().tolist()), label="Category")
        sort_by = gr.Dropdown(["Price: Low to High", "Price: High to Low", "Rating"], label="Sort By", value="Rating")
        min_price = gr.Number(label="Min Price", value=0)
        max_price = gr.Number(label="Max Price", value=1000)
        in_stock = gr.Checkbox(label="In Stock Only")
    
    show_btn = gr.Button("🔍 Show Products")
    load_more_btn = gr.Button("➕ Load More")
    output = gr.HTML()

    # Quote row
    with gr.Row():
        quote_output = gr.HTML()
    demo.load(get_quote, None, quote_output)

    # Show random products on page load
    demo.load(show_random_products, None, output)

    show_btn.click(show_products, [category, sort_by, min_price, max_price, in_stock, query], output)
    load_more_btn.click(load_more, [category, sort_by, min_price, max_price, in_stock, query], output)
def show_footer():
    return """
    <div style="text-align:center; font-size:0.8em; color:#888; margin-top:20px;">
        © Krishna Jha | <a href="https://www.instagram.com/kosmos.cpp/" target="_blank" style="color:#888;">@kosmos.cpp</a>
    </div>
    """
    
demo.launch()

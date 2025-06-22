import json

# Load the input JSON file
with open("comprehensive_sourcing_analysis_chocolate_manufacturing_USA_20250621_214030.json") as f:
    data = json.load(f)

# Output containers
neo4jNodes = []
neo4jRelationships = []

# ID and mapping setup
id_counter = 1
rel_counter = 1
id_map = {}

# ------------------------------
# Step 1: Add UseCase node
# ------------------------------

# Raw materials as comma string
raw_materials_list = data.get("identified_raw_materials", [])
raw_materials_str = ", ".join(raw_materials_list)

# Top supplier per material
top_suppliers = []
for material, details in data["material_analyses"].items():
    best_country = details["leader_analysis"]["ranking_analysis"]["best_country"]["country"]
    top_suppliers.append(f"{material}: {best_country}")
top_suppliers_str = ", ".join(top_suppliers)

# Add UseCase node
use_case_id = str(id_counter)
neo4jNodes.append({
    "id": use_case_id,
    "labels": ["UseCase"],
    "properties": {
        "name": "Chocolate Manufacturing",
        "location": data.get("destination_country", "Unknown"),
        "raw_materials": raw_materials_str,
        "top_suppliers": top_suppliers_str
    }
})
id_map["Chocolate Manufacturing"] = use_case_id
id_counter += 1

# ------------------------------
# Step 2: RawMaterial nodes & REQUIRES relationships
# ------------------------------
for material in raw_materials_list:
    raw_id = str(id_counter)
    material_data = data["material_analyses"].get(material, {})

    # Extract country names and scores
    countries_info = material_data.get("leader_analysis", {}).get("ranking_analysis", {}).get("all_rankings", [])
    identified_countries = [c["country"] for c in countries_info]
    country_scores = [f'{c["country"]}: {c["composite_score"]}' for c in countries_info]

    neo4jNodes.append({
        "id": raw_id,
        "labels": ["RawMaterial"],
        "properties": {
            "name": material,
            "identified_countries": ", ".join(identified_countries),
            "country_scores": ", ".join(country_scores)
        }
    })
    id_map[material] = raw_id

    neo4jRelationships.append({
        "id": f"r{rel_counter}",
        "startNodeId": use_case_id,
        "endNodeId": raw_id,
        "type": "REQUIRES",
        "properties": {}
    })
    id_counter += 1
    rel_counter += 1

# ------------------------------
# Step 3: Country nodes & SUPPLIES relationships
# ------------------------------
for material, details in data["material_analyses"].items():
    raw_id = id_map.get(material)
    countries = details["leader_analysis"]["ranking_analysis"]["all_rankings"]

    for country in countries:
        cname = country["country"]
        if cname not in id_map:
            country_id = str(id_counter)
            neo4jNodes.append({
                "id": country_id,
                "labels": ["Country"],
                "properties": {
                    "name": cname,
                    "cost_score": country["cost_score"],
                    "stability_score": country["stability_score"],
                    "eco_friendly_score": country["eco_friendly_score"],
                    "composite_score": country["composite_score"]
                }
            })
            id_map[cname] = country_id
            id_counter += 1

        neo4jRelationships.append({
            "id": f"r{rel_counter}",
            "startNodeId": id_map[cname],
            "endNodeId": raw_id,
            "type": "SUPPLIES",
            "properties": {}
        })
        rel_counter += 1

# ------------------------------
# Output the result
# ------------------------------
print("neo4jNodes = ")
print(json.dumps(neo4jNodes, indent=2))
print("\nneo4jRelationships = ")
print(json.dumps(neo4jRelationships, indent=2))

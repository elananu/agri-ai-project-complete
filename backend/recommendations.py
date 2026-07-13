"""
recommendations.py
Maps detected class labels to smart treatment recommendations, category,
risk level, disease type, and cause.

These keys match the 29 classes in the PlantDoc object-detection dataset
(https://github.com/pratikkayal/PlantDoc-Object-Detection-Dataset), which
is what backend/training/prepare_dataset.py + train.py are set up to use
by default, spanning multiple crops: apple, corn, tomato, potato, grape,
cherry, peach, bell pepper, blueberry, raspberry, soyabean, squash,
strawberry. If you train on a different dataset, update the keys below to
match your model's class names (see backend/models after training, or
check data.yaml's `names` list).
"""

RECOMMENDATIONS = {
    # --- Apple ---
    "apple_leaf": {"category": "healthy", "risk": "none", "disease_type": None, "cause": None,
                    "advice": "Healthy apple foliage. Maintain regular watering and pruning schedule."},
    "apple_scab_leaf": {"category": "disease", "risk": "high",
                          "disease_type": "Fungal disease",
                          "cause": "Caused by the fungus Venturia inaequalis, which thrives in cool, "
                                   "wet spring weather and spreads via spores from infected fallen leaves.",
                          "advice": "Apple scab detected. Remove and destroy fallen leaves, apply a "
                                    "labelled fungicide (e.g. captan or myclobutanil) at bud break, and "
                                    "improve air circulation by pruning."},
    "apple_rust_leaf": {"category": "disease", "risk": "medium",
                          "disease_type": "Fungal disease (rust)",
                          "cause": "Caused by Gymnosporangium juniperi-virginianae, a fungus that "
                                   "requires both an apple tree and a nearby juniper/cedar host to "
                                   "complete its life cycle.",
                          "advice": "Cedar-apple rust detected. Remove nearby juniper/cedar hosts if "
                                    "possible, apply a triazole fungicide in early spring."},

    # --- Corn / Maize ---
    "corn_gray_leaf_spot": {"category": "disease", "risk": "high",
                              "disease_type": "Fungal disease",
                              "cause": "Caused by the fungus Cercospora zeae-maydis, favored by warm, "
                                       "humid conditions and prolonged leaf wetness, and often worsened "
                                       "by continuous corn planting and reduced tillage.",
                              "advice": "Gray leaf spot detected. Rotate with a non-host crop, use "
                                        "resistant hybrids next season, and apply a strobilurin or "
                                        "triazole fungicide if disease pressure is high."},
    "corn_leaf_blight": {"category": "disease", "risk": "high",
                           "disease_type": "Fungal disease",
                           "cause": "Caused by the fungus Exserohilum turcicum, which survives in crop "
                                    "residue and spreads rapidly during periods of moderate temperatures "
                                    "and high humidity.",
                           "advice": "Northern corn leaf blight detected. Apply foliar fungicide at "
                                     "first sign of spread, rotate crops, and plant resistant hybrids."},
    "corn_rust_leaf": {"category": "disease", "risk": "medium",
                         "disease_type": "Fungal disease (rust)",
                         "cause": "Caused by the fungus Puccinia sorghi, whose airborne spores spread "
                                  "quickly in humid conditions with moderate temperatures.",
                         "advice": "Common rust detected. Usually minor — monitor spread; apply "
                                   "fungicide only if pustules cover a large leaf area on susceptible hybrids."},

    # --- Grape ---
    "grape_leaf": {"category": "healthy", "risk": "none", "disease_type": None, "cause": None,
                     "advice": "Healthy grape foliage. Continue routine canopy management."},
    "grape_leaf_black_rot": {"category": "disease", "risk": "high",
                               "disease_type": "Fungal disease",
                               "cause": "Caused by the fungus Guignardia bidwellii, which overwinters in "
                                        "mummified berries and infected canes, spreading during warm, "
                                        "wet spring weather.",
                               "advice": "Black rot detected. Remove mummified berries and infected "
                                         "leaves, apply mancozeb or myclobutanil starting at bud break."},

    # --- Tomato ---
    "tomato_leaf": {"category": "healthy", "risk": "none", "disease_type": None, "cause": None,
                      "advice": "Healthy tomato foliage. Maintain consistent watering to avoid stress."},
    "tomato_early_blight_leaf": {"category": "disease", "risk": "high",
                                   "disease_type": "Fungal disease",
                                   "cause": "Caused by the fungus Alternaria solani, which persists in "
                                            "soil and plant debris and spreads via wind, rain splash, "
                                            "and overhead irrigation.",
                                   "advice": "Early blight detected. Remove lower infected leaves, mulch "
                                             "to prevent soil splash, apply chlorothalonil or copper fungicide."},
    "tomato_leaf_late_blight": {"category": "disease", "risk": "high",
                                  "disease_type": "Oomycete (water mold) disease",
                                  "cause": "Caused by Phytophthora infestans, which spreads explosively "
                                           "in cool, wet, humid weather and can destroy a crop within days.",
                                  "advice": "Late blight detected — spreads fast in humid weather. Remove "
                                            "infected plants promptly, apply a copper-based fungicide, "
                                            "avoid overhead watering."},
    "tomato_leaf_bacterial_spot": {"category": "disease", "risk": "high",
                                     "disease_type": "Bacterial disease",
                                     "cause": "Caused by Xanthomonas bacteria species, which spread "
                                              "through splashing water, contaminated tools, and handling "
                                              "wet plants.",
                                     "advice": "Bacterial spot detected. Use copper bactericide sprays, "
                                               "avoid working in wet fields, rotate crops for 2+ seasons."},
    "tomato_septoria_leaf_spot": {"category": "disease", "risk": "medium",
                                    "disease_type": "Fungal disease",
                                    "cause": "Caused by the fungus Septoria lycopersici, which survives "
                                             "on plant debris and spreads via rain splash and prolonged "
                                             "leaf wetness.",
                                    "advice": "Septoria leaf spot detected. Remove affected lower leaves, "
                                              "stake plants for airflow, apply chlorothalonil-based fungicide."},
    "tomato_leaf_mosaic_virus": {"category": "disease", "risk": "high",
                                   "disease_type": "Viral disease",
                                   "cause": "Caused by Tobacco Mosaic Virus (TMV) or related mosaic "
                                            "viruses, spread mechanically through handling, tools, and "
                                            "sometimes seed.",
                                   "advice": "Mosaic virus symptoms detected. No cure — remove and destroy "
                                             "infected plants, control aphids (a common vector), disinfect tools."},
    "tomato_leaf_yellow_virus": {"category": "disease", "risk": "high",
                                   "disease_type": "Viral disease",
                                   "cause": "Caused by Tomato Yellow Leaf Curl Virus (TYLCV), transmitted "
                                            "primarily by the silverleaf whitefly (Bemisia tabaci).",
                                   "advice": "Yellow leaf curl virus symptoms detected. Remove infected "
                                             "plants, control whitefly populations (the primary vector) "
                                             "with insecticidal soap or yellow sticky traps."},
    "tomato_mold_leaf": {"category": "disease", "risk": "medium",
                           "disease_type": "Fungal disease",
                           "cause": "Caused by the fungus Passalora fulva (formerly Fulvia fulva), "
                                    "which thrives in high humidity and poor air circulation, especially "
                                    "in greenhouses.",
                           "advice": "Leaf mold detected. Improve greenhouse/field ventilation, reduce "
                                     "humidity, apply a labelled fungicide."},
    "tomato_two_spotted_spider_mites_leaf": {"category": "pest", "risk": "medium",
                                               "disease_type": "Pest infestation (mite)",
                                               "cause": "Caused by Tetranychus urticae (two-spotted spider "
                                                        "mite), which thrives in hot, dry conditions and "
                                                        "reproduces rapidly on leaf undersides.",
                                               "advice": "Spider mite damage detected. Spray undersides of "
                                                         "leaves with water to dislodge mites, apply "
                                                         "insecticidal soap or miticide, introduce predatory mites."},

    # --- Potato ---
    "potato_leaf": {"category": "healthy", "risk": "none", "disease_type": None, "cause": None,
                      "advice": "Healthy potato foliage."},
    "potato_leaf_early_blight": {"category": "disease", "risk": "high",
                                   "disease_type": "Fungal disease",
                                   "cause": "Caused by the fungus Alternaria solani, favored by warm "
                                            "temperatures, alternating wet/dry periods, and plant stress "
                                            "or nutrient deficiency.",
                                   "advice": "Early blight detected. Apply chlorothalonil or mancozeb, "
                                             "remove infected foliage, ensure adequate plant spacing."},
    "potato_leaf_late_blight": {"category": "disease", "risk": "high",
                                  "disease_type": "Oomycete (water mold) disease",
                                  "cause": "Caused by Phytophthora infestans, the same pathogen behind "
                                           "the historic Irish potato famine, spreading rapidly in cool, "
                                           "wet conditions.",
                                  "advice": "Late blight detected — highly contagious in wet conditions. "
                                            "Apply copper-based fungicide immediately, remove infected "
                                            "plants, avoid overhead irrigation."},

    # --- Squash ---
    "squash_powdery_mildew_leaf": {"category": "disease", "risk": "medium",
                                     "disease_type": "Fungal disease",
                                     "cause": "Caused by fungi such as Podosphaera xanthii or Erysiphe "
                                              "cichoracearum, which spread readily in warm, dry conditions "
                                              "with high humidity and poor air circulation.",
                                     "advice": "Powdery mildew (white powdery coating) detected. Apply "
                                               "sulfur or potassium bicarbonate spray, increase spacing "
                                               "for airflow, avoid overhead watering."},

    # --- Bell pepper ---
    "bell_pepper_leaf": {"category": "healthy", "risk": "none", "disease_type": None, "cause": None,
                           "advice": "Healthy bell pepper foliage."},
    "bell_pepper_leaf_spot": {"category": "disease", "risk": "medium",
                                "disease_type": "Bacterial disease",
                                "cause": "Caused by Xanthomonas campestris pv. vesicatoria, spread by "
                                         "rain splash, contaminated seed, and handling wet foliage.",
                                "advice": "Bacterial leaf spot detected. Apply copper-based bactericide, "
                                          "avoid overhead irrigation, rotate crops."},

    # --- Other healthy leaf classes (no disease/pest signature) ---
    "cherry_leaf": {"category": "healthy", "risk": "none", "disease_type": None, "cause": None,
                     "advice": "Healthy cherry foliage."},
    "peach_leaf": {"category": "healthy", "risk": "none", "disease_type": None, "cause": None,
                    "advice": "Healthy peach foliage."},
    "blueberry_leaf": {"category": "healthy", "risk": "none", "disease_type": None, "cause": None,
                        "advice": "Healthy blueberry foliage."},
    "raspberry_leaf": {"category": "healthy", "risk": "none", "disease_type": None, "cause": None,
                        "advice": "Healthy raspberry foliage."},
    "soyabean_leaf": {"category": "healthy", "risk": "none", "disease_type": None, "cause": None,
                       "advice": "Healthy soyabean foliage."},
    "strawberry_leaf": {"category": "healthy", "risk": "none", "disease_type": None, "cause": None,
                         "advice": "Healthy strawberry foliage."},

    # --- Generic CV-heuristic fallback labels (used only when no trained
    #     model is loaded — see backend/detection.py) ---
    "leaf_blight": {"category": "disease", "risk": "high",
                      "disease_type": "Fungal disease (general blight)",
                      "cause": "Consistent with a fungal or bacterial blight pathogen that thrives in "
                               "wet, humid conditions and spreads via water splash and plant debris.",
                      "advice": "Dark lesion pattern detected. Remove and destroy affected leaves, "
                                "apply a copper-based fungicide, improve field drainage and airflow."},
    "rust": {"category": "disease", "risk": "medium",
              "disease_type": "Fungal disease (rust)",
              "cause": "Consistent with a rust fungus (Puccinia or related genera), which produces "
                       "airborne spores that spread rapidly in humid, moderate-temperature conditions.",
              "advice": "Small round dark spots detected, consistent with rust. Apply a triazole "
                        "fungicide and remove crop debris that may harbor spores."},
    "powdery_mildew": {"category": "disease", "risk": "medium",
                         "disease_type": "Fungal disease",
                         "cause": "Consistent with a powdery mildew fungus, which thrives in warm, dry "
                                  "air combined with high humidity and poor air circulation.",
                         "advice": "Large pale/yellow patch detected. If a white powdery coating is "
                                   "visible, apply sulfur-based fungicide and increase plant spacing."},
    "pest_damage_yellowing": {"category": "pest", "risk": "medium",
                                "disease_type": "Pest infestation or nutrient stress",
                                "cause": "Often caused by sap-sucking pests such as aphids or whiteflies, "
                                         "or by nutrient deficiency (commonly nitrogen).",
                                "advice": "Yellow/chlorotic patch detected — often caused by sap-sucking "
                                          "pests (aphids, whiteflies) or nutrient stress. Inspect leaf "
                                          "undersides for insects; apply neem oil if pests are confirmed, "
                                          "or a balanced foliar feed if it looks nutrient-related."},
    "weed": {"category": "weed", "risk": "medium",
              "disease_type": None, "cause": None,
              "advice": "Manual or mechanical weed removal recommended. Consider a targeted "
                        "bio-herbicide for dense patches."},
    "healthy": {"category": "healthy", "risk": "none", "disease_type": None, "cause": None,
                 "advice": "Crop looks healthy. Maintain current watering and fertilization schedule."},
}

DEFAULT_RECOMMENDATION = {
    "category": "unknown",
    "risk": "low",
    "disease_type": None,
    "cause": None,
    "advice": "No specific recommendation available for this class yet. "
              "Add an entry to RECOMMENDATIONS in recommendations.py, or "
              "consult a local agronomist for confirmation.",
}


def get_recommendation(label: str) -> dict:
    key = label.strip().lower().replace(" ", "_")
    return RECOMMENDATIONS.get(key, DEFAULT_RECOMMENDATION)
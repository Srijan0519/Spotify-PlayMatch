# gemini_service.py (refactored)

import json
import logging
import random
import re
import time
import streamlit as st
import google.generativeai as genai


def setup_gemini():
    try:
        api_key = st.secrets["gemini"]["api_key"]
        genai.configure(api_key=api_key)

        preferred_models = [
            "models/gemini-1.5-pro",
            "models/gemini-1.5-flash",
            "models/gemini-2.0-pro",
        ]

        for model_name in preferred_models:
            try:
                model = genai.GenerativeModel(model_name)
                _ = model.generate_content("Hello")
                st.success(f"✅ Using Gemini model: {model_name}")
                return model
            except Exception as e:
                logging.warning(f"Model {model_name} failed: {e}")

        raise RuntimeError("No Gemini models responded.")

    except Exception as e:
        st.warning("⚠️ Gemini API failed. Falling back to basic recommendations.")
        logging.error(f"Fallback activated: {e}")

        class FallbackModel:
            def generate_content(self, prompt, **kwargs):
                class Response:
                    @property
                    def text(self):
                        return json.dumps({"error": "Gemini unavailable. Using fallback response."})
                return Response()

        return FallbackModel()


def extract_json_from_response(response_text):
    try:
        if response_text.startswith("```json"):
            response_text = response_text.split("```json")[-1].split("```")[-2].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[-2].strip()
        response_text = response_text.replace("'", '"')
        if response_text.startswith("[") or response_text.startswith("{"):
            return json.loads(response_text)
    except Exception as e:
        logging.warning(f"Error parsing JSON from response: {e}")
    return None


def analyze_playlist(tracks):
    model = setup_gemini()
    track_lines = [f"{i+1}. {t['name']} by {t['artist']} ({t.get('release_date', 'Unknown')})" for i, t in enumerate(tracks[:20])]
    prompt = f"""
    Analyze the following playlist and return musical attributes in JSON:

    SONGS:
    {'\n'.join(track_lines)}

    Return JSON with:
    - general_description
    - bpm_range (min, max, most_common)
    - instruments (e.g., Guitar: high)
    - key_distribution (e.g., A Minor: 3)
    - mood_description
    - genre_analysis
    """

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        parsed = extract_json_from_response(response_text)
        return parsed if parsed else {"error": "Failed to parse analysis."}
    except Exception as e:
        logging.error(f"Analysis failed: {e}")
        return {"error": "Gemini failed to generate analysis."}


def get_song_recommendations(analysis):
    model = setup_gemini()

    simplified = {
        "description": analysis.get("general_description", ""),
        "genres": analysis.get("genre_analysis", ""),
        "mood": analysis.get("mood_description", ""),
        "instruments": list(analysis.get("instruments", {}).keys()),
        "keys": list(analysis.get("key_distribution", {}).keys()),
    }

    prompt = f"""
    Recommend 3 songs based on this profile:

    PROFILE:
    {json.dumps(simplified, indent=2)}

    Return ONLY a JSON array of songs with:
    - title
    - artist
    - reasoning
    - attributes (tempo, key, mood, production style, instruments)
    - spotify_url
    """

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        parsed = extract_json_from_response(response_text)
        return parsed if parsed else [{"error": "Failed to parse recommendations."}]
    except Exception as e:
        logging.error(f"Recommendation failed: {e}")
        return [{"error": "Gemini failed to generate recommendations."}]

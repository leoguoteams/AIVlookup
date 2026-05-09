import numpy as np
import json
import os
from typing import List, Tuple, Optional, Dict, Any
from api_manager import APIManager

class MatcherLogic:
    """
    Core matching engine implementing the 'Coarse-to-Fine' strategy:
    Cosine Similarity (Top-K) -> LLM Refinement -> Confidence Grading.
    """
    
    def __init__(self, api_manager: APIManager, score_threshold: int = 30):
        self.api_manager = api_manager
        self.score_threshold = score_threshold
        self.global_cache_path = "global_match_cache.json"
        self.match_cache = self._load_global_cache()

    def _load_global_cache(self) -> Dict[str, Any]:
        if os.path.exists(self.global_cache_path):
            try:
                with open(self.global_cache_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_global_cache(self):
        try:
            with open(self.global_cache_path, "w", encoding="utf-8") as f:
                json.dump(self.match_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Cache] Failed to save global cache: {e}")

    def clean_text(self, text: Any) -> str:
        if not text:
            return ""
        cleaned = str(text).strip().replace("　", "").replace(" ", "")
        return cleaned[:512]

    def get_confidence_grade(self, score: int) -> str:
        if score >= 90:
            return "High"
        elif score >= 60:
            return "Medium"
        else:
            return "Low"

    def calculate_cosine_similarity(self, a_vector: np.ndarray, b_vectors: np.ndarray) -> np.ndarray:
        norm_a = np.linalg.norm(a_vector)
        norm_b = np.linalg.norm(b_vectors, axis=1)
        dot_product = np.dot(a_vector, b_vectors.T)
        return dot_product / np.where((norm_a * norm_b) == 0, 1e-10, norm_a * norm_b)

    def match_single_item(self, a_text: str, b_data: List[Tuple], b_embeddings: np.ndarray) -> Tuple:
        """
        Matches a single item from A against the B table.
        Returns: (B_code, B_name, B_spec, B_size, Final_Score, Source, Grade, Status)
        """
        cleaned_a = self.clean_text(a_text)
        if not cleaned_a:
            return (None, None, None, None, 0, "None", "Low", "Empty Text")

        # 1. Check Global Cache
        if cleaned_a in self.match_cache:
            cached = self.match_cache[cleaned_a]
            return (cached['code'], cached['name'], cached['spec'], cached['size'], 
                    cached['score'], cached['source'], cached['grade'], "Cached")

        # 2. Vectorization & Coarse Match
        a_emb = self.api_manager.get_embeddings([cleaned_a])
        if a_emb is None or len(a_emb) == 0:
            return (None, None, None, None, 0, "None", "Low", "Vector Failed")
        
        sims = self.calculate_cosine_similarity(a_emb[0], b_embeddings)
        top_indices = np.argsort(sims)[::-1][:3]
        
        # Prepare candidates for LLM
        candidates = []
        for idx in top_indices:
            item = b_data[idx]
            candidates.append({
                "index": idx,
                "code": item[0],
                "name": item[1],
                "spec": item[2],
                "size": item[3],
                "cosine_score": float(sims[idx])
            })

        # 3. LLM Refinement
        # Construct prompt for the LLM
        b_list_str = "\n".join([f"[{i}] 名称:{c['name']}, 规格:{c['spec']}, 尺寸:{c['size']}" for i, c in enumerate(candidates)])
        prompt = (
            f"##Role: Material Matching Expert\n"
            f"##Task: Find the most similar item from Candidates to the target material. Provide a score (0-100).\n"
            f"##Target Material: {cleaned_a}\n"
            f"##Candidates:\n{b_list_str}\n"
            f"##Constraint: Return ONLY a JSON object: {{\"index\": int, \"score\": int}}\n"
        )

        llm_raw = self.api_manager.get_llm_response(prompt)
        if not llm_raw:
            return (None, None, None, None, 0, "LLM", "Low", "LLM Failed")

        try:
            # Basic JSON extraction
            import re
            match = re.search(r'\{.*\}', llm_raw)
            if match:
                res_json = json.loads(match.group())
                best_idx_rel = res_json.get("index")
                llm_score = res_json.get("score", 0)
                
                if best_idx_rel is not None and 0 <= best_idx_rel < len(candidates):
                    best_cand = candidates[best_idx_rel]
                    final_score = llm_score
                    
                    # Final Validation against threshold
                    if final_score >= self.score_threshold:
                        status = "Matched"
                    else:
                        status = "Below Threshold"
                    
                    grade = self.get_confidence_grade(final_score)
                    
                    result = (
                        best_cand['code'], best_cand['name'], 
                        best_cand['spec'], best_cand['size'], 
                        final_score, "LLM", grade, status
                    )
                    
                    # Update Global Cache
                    self.match_cache[cleaned_a] = {
                        "code": result[0], "name": result[1], "spec": result[2], 
                        "size": result[3], "score": result[4], "source": result[5], "grade": result[6]
                    }
                    self._save_global_cache()
                    
                    return result
        except Exception as e:
            print(f"[Matcher] Parsing error: {e}")

        return (None, None, None, None, 0, "LLM", "Low", "Matching Failed")

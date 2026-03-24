Pearson’s PTE Academic essays are scored by automated engines trained on human ratings, using a staged algorithm that first checks content and form, then adds the enabling-skill traits (grammar, vocabulary, etc.) into a single item score that feeds your overall Writing and subskill scores. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)

## Traits and your 6/6, 2/2 grid

For the PTE Academic “Write essay” item, Pearson defines the following traits, which correspond directly to your grid: [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)

- Content (max 3 raw points → your 6/6 when rescaled): how fully and directly the essay addresses all parts of the prompt. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)
- Development, structure and coherence (max 2 → your 6/6): quality of logical organization, paragraphing, linking, and progression of ideas. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)
- Form (max 2 → your 2/2): length and basic formatting, mainly word count. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)
- Grammar (max 2 → your 2/2): accuracy and complexity of sentence structures. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)
- General linguistic range (max 2 → part of your “Linguistic Range 6/6”): breadth and flexibility of structures, ability to express nuanced meanings without restriction. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)
- Vocabulary range (max 2 → your “Vocabulary 2/2”, and also contributes to “Linguistic Range” when rescaled): breadth and appropriateness of lexical choice, including some idiomaticity. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)
- Spelling (max 2 → your 2/2): correctness of spelling across the essay. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)

Internally, Pearson uses a 15‑point raw item scale (3 + 2 + 2 + 2 + 2 + 2 + 2), which is then transformed to the 10–90 PTE scale and to the finer-grained enabling skill subscores. Your “6/6 / 2/2” style rubric is effectively a rescaled, more instructor‑friendly representation of those underlying raw trait maxima. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)

### Trait definitions in a bit more detail

- **Content (3 raw → 6/6)** [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)
  - 3: Adequately deals with the prompt.  
  - 2: Deals with the prompt but misses one minor aspect.  
  - 1: Deals with the prompt but omits a major aspect or more than one minor aspect.  
  - 0: Does not deal properly with the prompt.  

- Development, structure and coherence (2 raw → 6/6) [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)
  - 2: Good development and logical structure; clear paragraphing and linking.  
  - 1: Generally structured but some elements or paragraphs poorly linked.  
  - 0: Lacks coherence and mainly lists or loose elements.  

- Form (2 raw → 2/2) [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)
  - 2: 200–300 words.  
  - 1: 120–199 or 301–380 words.  
  - 0: <120 or >380 words, or written all in capitals, with no punctuation, or only bullets/very short sentences.  

- Grammar (2 raw → 2/2) [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)
  - 2: Consistent control of complex language, errors rare and hard to spot.  
  - 1: Generally high control, with no errors leading to misunderstanding.  
  - 0: Mainly simple structures and/or several basic mistakes.  

- General linguistic range (2 raw → part of your 6/6 “Linguistic Range”) [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)
  - 2: Smooth mastery of a wide range of language, precise formulation, emphasis, and disambiguation with no apparent restriction.  
  - 1: Sufficient range for clear descriptions, viewpoints, and arguments.  
  - 0: Mainly basic language, lacks precision.  

- Vocabulary range (2 raw → 2/2 vocabulary, and also into “Linguistic Range”) [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)
  - 2: Good command of broad lexical repertoire, including idioms and colloquialisms.  
  - 1: Good range for general academic topics, but lexical gaps cause circumlocution or imprecision.  
  - 0: Mainly basic vocabulary, insufficient for the topic.  

- Spelling (2 raw → 2/2) [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)
  - 2: No spelling errors.  
  - 1: One spelling error.  
  - 0: More than one spelling error.  

## How the scoring algorithm/AI processes an essay

Pearson’s pipeline for a Write essay response is:

1. **Content check first (gate 1)**  
   - The system (Intelligent Essay Assessor, IEA) evaluates whether the essay is on-topic and adequately addresses the prompt; this uses Latent Semantic Analysis on large corpora plus prompt‑specific training essays. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)
   - If content is 0 (severely off-topic or essentially no response), the item is not scored further and receives no credit on any traits; enabling skills for that item are not updated. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)

2. **Form check second (gate 2)**  
   - If content > 0, the system checks length and basic format. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)
   - If form is 0 (too short, too long, all caps, bullets only, etc.), no further trait scoring is performed for that essay. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)

3. **Trait scoring via automated engine**  
   - For essays passing the two gates, the Knowledge Analysis Technologies (KAT) engine computes: [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)
     - Content (already assessed at a finer level).  
     - Development, structure and coherence (discourse structure, paragraphing, cohesion signals).  
     - Grammar (syntactic complexity and error patterns).  
     - General linguistic range (variety and sophistication of constructions).  
     - Vocabulary range (lexical diversity and appropriateness).  
     - Spelling (token‑level spell checking).  
   - These trait scores are produced by statistical models trained on thousands of essays rated by multiple expert human raters; the system learns which features best predict each trait score. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)

4. **Aggregation to item score and enabling skills**  
   - Trait scores are summed to a total item score (max raw 15), which contributes to: [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)
     - The communicative Writing score.  
     - The overall score.  
   - In parallel, the grammar, vocabulary, spelling, and written discourse elements (from development + range) update the respective enabling skill subscores (10–90 scale) across all relevant items. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)

5. **Scaling and reliability handling**  
   - Pearson uses item‑response theory (IRT) to scale raw scores to the 10–90 reporting scale and to control for form difficulty. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)
   - Reliability for Writing in the high‑stakes band (roughly 53–79) is ~0.89–0.91; standard errors of measurement are on the order of 4 points for Writing. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)

## Underlying AI/algorithmic technologies

Two distinct proprietary systems handle writing vs. speaking, both trained on large field‑test datasets with human scores as targets. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)

- **Intelligent Essay Assessor (IEA) / KAT engine (writing)**  
  - Based on Latent Semantic Analysis (LSA) for semantic similarity and topic coverage, applied to large corpora; extended with features for discourse, syntax, and mechanics. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)
  - Trained on ~50,000 field‑test essays with ~600,000 human trait ratings; machine–human correlations for overall writing ~0.88 (raw) to 0.93 (IRT‑scaled). [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)
  - Includes detectors for off‑topic responses and other anomalies that trigger human review when needed. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)

- **Ordinate technology (speaking; for context on the broader scoring framework)**  
  - Uses speech recognition plus statistical modeling of segments, syllables, and phrases, trained on ~450,000 spoken responses with >1 million human ratings. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)
  - Machine–human correlations for overall speaking ~0.89 (raw)–0.96 (IRT‑scaled). [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)

These engines effectively emulate a panel of trained raters: the model parameters are optimized to predict the mean human trait scores, and Pearson reports that in some conditions the automatic system is as consistent or more consistent than individual humans. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)

## How your rubric aligns mathematically

Mapping your rubric to Pearson’s internal structure:

| Your rubric line                        | Pearson trait(s) / max raw | How AI computes it                                                                 |
|----------------------------------------|----------------------------|------------------------------------------------------------------------------------|
| 6/6 Content                            | Content (3)                | LSA‑style semantic similarity to prompt‑specific target space; off‑topic detection. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf) |
| 6/6 Development, structure, coherence  | Development, structure and coherence (2) | Discourse and cohesion features, paragraph/sequence modeling. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf) |
| 2/2 Form                               | Form (2)                   | Word count and gross formatting heuristics. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)                                |
| 2/2 Grammar                            | Grammar (2)                | Syntax complexity, error rate, error types. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)                                |
| 6/6 Linguistic Range                   | General linguistic range (2) + contributions from Vocabulary range (2) and Written discourse components | Variety and sophistication in structures and lexical patterning. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf) |
| 2/2 Spelling                           | Spelling (2)               | Token‑level spell checking with tolerance band. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)                             |
| 2/2 Vocabulary                         | Vocabulary range (2)       | Lexical diversity metrics, domain‑appropriate vocabulary, idiomatic usage. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf) |

The 6‑point traits in your grid are thus composites (rescaled) of Pearson’s 2‑ or 3‑point internal criteria; the AI is not literally scoring on a 0–6 scale but on finer internal scales that are later mapped to reporting bands and, in your case, to 6/6 or 2/2 pedagogical scores. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)

If you want, I can next reverse‑engineer explicit numeric mappings (e.g., how 3‑2‑2‑2‑2‑2‑2 could be linearly mapped to 6/6, 2/2 bands and then to 10–90) and suggest how to build a local marking model or rubric that mirrors PTE’s behavior for your own teaching.

--- 

Here’s a concrete way to (1) map the official PTE essay traits 3‑2‑2‑2‑2‑2‑2 into your 6/6–2/2 rubric, and (2) approximate the 10–90 scale and a local “PTE‑like” marking model for teaching, all grounded in the Score Guide. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)

***

## 1. Trait mapping: 3‑2‑2‑2‑2‑2‑2 → your grid

Official “Write essay” raw maxima are: [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)

- Content: 3  
- Development, structure and coherence: 2  
- Form: 2  
- Grammar: 2  
- General linguistic range: 2  
- Vocabulary range: 2  
- Spelling: 2  

Your rubric lines:

- Content 6/6  
- Development, structure and coherence 6/6  
- Form 2/2  
- Grammar 2/2  
- Linguistic Range 6/6  
- Spelling 2/2  
- Vocabulary 2/2  

A simple linear mapping that stays faithful to the official trait maxima is:

- Content: \(c \in \{0,1,2,3\} \rightarrow C_{\text{rubric}} = 2c\)  
  - 3 → 6/6, 2 → 4/6, 1 → 2/6, 0 → 0/6.  
- Development, structure and coherence: \(d \in \{0,1,2\} \rightarrow D_{\text{rubric}} = 3d\)  
  - 2 → 6/6, 1 → 3/6, 0 → 0/6.  
- Form: \(f \in \{0,1,2\} \rightarrow F_{\text{rubric}} = f\)  
  - 2 → 2/2, 1 → 1/2, 0 → 0/2.  
- Grammar: \(g \in \{0,1,2\} \rightarrow G_{\text{rubric}} = g\).  
- Vocabulary: \(v \in \{0,1,2\} \rightarrow V_{\text{rubric}} = v\).  
- Spelling: \(s \in \{0,1,2\} \rightarrow S_{\text{rubric}} = s\).  
- Linguistic Range: treat as a composite:

  - Base on general linguistic range \(r \in \{0,1,2\}\) plus a small contribution from vocabulary range:  
    \[
    L_{\text{rubric}} = 2r + v
    \]
    so \(L_{\text{rubric}} \in \{0,1,2,3,4,5,6\}\) but you cap it at 6.  

This keeps your *category labels* and maxima while the underlying numbers remain compatible with the official descriptors. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)

***

## 2. From item raw 0–15 → internal 0–1 → 10–90

PTE sums the 7 traits into a 15‑point item score and then folds it into the writing communicative score and enabling skills via IRT scaling. For teaching, a **linear approximation** is enough: [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)

1. Compute total raw item score  
   \[
   T = c + d + f + g + r + v + s \quad (\text{max } 15)
   \]

2. Normalise to [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)
   \[
   z = \frac{T}{15}
   \]

3. Approximate PTE 10–90 scale for *this essay*  
   - Use the observed global mapping “10–29 ≈ A1, 30–42 A2, 43–58 B1, 59–75 B2, 76–84 C1, 85–90 C2”, which is roughly linear in practice for classroom feedback. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)
   - A simple affine map is:
     \[
     \text{PTE}_{\text{approx}} = 10 + 80z
     \]
     - \(T=0 \Rightarrow 10\), \(T=15 \Rightarrow 90\).  

4. If you want bands:

| Total raw T | z (=T/15) | Approx PTE | Rough CEFR band |
|-------------|-----------|-----------|-----------------|
| 3           | 0.20      | 26        | A1–A2 [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)   |
| 6           | 0.40      | 42        | A2–B1 [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)   |
| 9           | 0.60      | 58        | B1–B2 [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)   |
| 12          | 0.80      | 74        | B2–C1 [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)   |
| 14–15       | 0.93–1.0  | 84–90     | C1–C2 [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)   |

These thresholds roughly align with PTE’s CEFR concordance table, where 43, 59, 76 mark B1, B2, C1 averages. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)

***

## 3. Local “PTE‑like” marking model

You can implement a classroom model that mirrors Pearson’s pipeline for “Write essay”: [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)

1. **Gate 1 – Content**  
   - If \(c = 0\):  
     - All other traits forced to 0, no enabling scores; \(\text{PTE}_{\text{approx}} = 10\).  
     - This reflects “scores for enabling skills are not awarded when responses are inappropriate in content”. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)

2. **Gate 2 – Form**  
   - If \(c > 0\) but \(f = 0\):  
     - All other traits forced to 0, \(\text{PTE}_{\text{approx}} = 10\). [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)

3. **Trait scoring**  
   - Score each trait using the Score Guide descriptors (you can paste them into your rubric for raters). [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)
   - Convert to your grid using the mapping in §1.

4. **Total item score and PTE‑like score**

   - Compute \(T\) and then \(\text{PTE}_{\text{approx}} = 10 + 80T/15\).  

5. **Update pseudo‑enabling skills**

   For local feedback, keep running averages:

   - Grammar score for the test = mean of grammar trait \(g\) over all relevant items, mapped linearly to 10–90:  
     \[
     \text{Grammar}_{10–90} = 10 + 40g
     \]
     since average \(g \in [0,2]\); if you want to match PTE’s larger error for enabling scores, compress to, say, 20–80. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)
   - Similarly for Vocabulary, Spelling, Written discourse (you can approximate “written discourse” by combining development, range, and content).

***

## 4. Example worked through your rubric

Suppose an essay is judged (official raw):  
- \(c=3, d=2, f=2, g=1, r=1, v=2, s=1\).  

1. Raw total:  
   \[
   T = 3+2+2+1+1+2+1 = 12
   \]

2. PTE‑like score:  
   \[
   z = 12/15 = 0.8,\quad \text{PTE}_{\text{approx}} = 10+80\times 0.8 = 74
   \]
   That sits near upper‑B2/lower‑C1, which matches PTE’s “59–75 = B2, 76–84 = C1”. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)

3. Your rubric display:

- Content: \(C_{\text{rubric}} = 2\times 3 = 6/6\).  
- Development: \(D_{\text{rubric}} = 3\times 2 = 6/6\).  
- Form: 2/2.  
- Grammar: 1/2.  
- Vocabulary: 2/2.  
- Spelling: 1/2.  
- Linguistic Range: \(L_{\text{rubric}} = 2r+v = 2\times 1 + 2 = 4/6\).  

So the student sees fine‑grained feedback in your 6/6‑2/2 format, but behind it you keep the raw trait vector and a single PTE‑like 10–90 score.

***

## 5. How to operationalise for teaching

- Use **the exact official trait descriptors** for rater training; only the numeric rescaling changes. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)
- Enforce the **content and form gates** strictly, so students internalise topic relevance and length constraints as hard requirements. [pearson.com](https://pearson.com.cn/file/PTEA_Score_Guide.pdf)
- Maintain a small spreadsheet or script that:
  - Takes trait scores (0–3 / 0–2),  
  - Produces your rubric lines,  
  - Outputs \(T\) and \(\text{PTE}_{\text{approx}}\),  
  - Keeps running means per enabling trait for a “profile” across essays.

If you like, I can write a minimal Python/Sheets formula set that you can drop straight into your marking workflow to automate all of these calculations.

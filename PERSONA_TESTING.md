# DeBot Persona-Based Testing Guide

## Overview
DeBot now supports persona-based collection switching, allowing different users to access different sets of documents with customized prompt styles.

## Available Personas

| Persona | Collections | Prompt Style | Data Directory |
|---------|-------------|--------------|----------------|
| `mugdha` | therapy_docs | gentle | `./data/mugdha/` |
| `praveen` | enterprise_docs, core_docs | direct | `./data/praveen/` |
| `real_estate` | property_docs, market_analysis | professional | `./data/real_estate/` |
| `digital_marketing` | marketing_docs, campaign_data | creative | `./data/digital_marketing/` |
| `default` | documents | balanced | `./data/` |

## Setup Test Data

### Step 1: Create Sample Documents

1. **Therapy Documents (Mugdha)**:
   ```bash
   # Create therapy-related documents
   echo "# PCOS Management Guide\n\nPCOS (Polycystic Ovary Syndrome) is a hormonal disorder affecting women of reproductive age.\n\n## Symptoms\n- Irregular periods\n- Weight gain\n- Hair loss\n\n## Treatment\n- Lifestyle changes\n- Medication\n- Regular monitoring" > data/mugdha/mds/pcos_guide.md
   
   echo "# Functional Nutrition Approach\n\nFunctional nutrition focuses on root causes of health issues.\n\n## Key Principles\n- Whole foods\n- Anti-inflammatory diet\n- Personalized supplements\n- Stress management" > data/mugdha/mds/functional_nutrition.md
   ```

2. **Real Estate Documents**:
   ```bash
   echo "# Real Estate Market Analysis 2024\n\n## Market Trends\n- Property prices increased 8% YoY\n- Rental yields averaging 4.5%\n- High demand in suburban areas\n\n## Investment Opportunities\n- Commercial properties\n- Residential developments\n- REITs" > data/real_estate/mds/market_analysis_2024.md
   
   echo "# Property Investment Guide\n\n## Due Diligence Checklist\n- Location analysis\n- Property inspection\n- Financial projections\n- Legal documentation\n\n## Financing Options\n- Traditional mortgages\n- Hard money loans\n- Private lending" > data/real_estate/mds/investment_guide.md
   ```

3. **Digital Marketing Documents**:
   ```bash
   echo "# Digital Marketing Strategy 2024\n\n## Key Channels\n- Social media marketing\n- Content marketing\n- Email campaigns\n- SEO optimization\n\n## Metrics to Track\n- Conversion rates\n- Customer acquisition cost\n- Return on ad spend\n- Engagement rates" > data/digital_marketing/mds/marketing_strategy.md
   
   echo "# Social Media Campaign Guide\n\n## Platform Strategies\n- Instagram: Visual storytelling\n- LinkedIn: B2B networking\n- TikTok: Short-form content\n- Facebook: Community building\n\n## Content Calendar\n- Plan 30 days ahead\n- Mix of promotional and educational content\n- User-generated content integration" > data/digital_marketing/mds/social_media_guide.md
   ```

### Step 2: Initialize Data
```bash
# Set force reindex to ensure fresh data
export FORCE_REINDEX=true

# Or on Windows
set FORCE_REINDEX=true
```

## Testing Steps

### Test 1: CLI Interface with Different Personas

1. **Test Mugdha Persona (Therapy)**:
   ```bash
   python main.py --persona mugdha
   ```
   - Ask: "What is PCOS and how is it treated?"
   - Expected: Should return information from therapy documents only
   - Verify: Response uses gentle, empathetic tone

2. **Test Real Estate Persona**:
   ```bash
   python main.py --persona real_estate
   ```
   - Ask: "What are the current real estate market trends?"
   - Expected: Should return property market information only
   - Verify: Response uses professional, business-focused tone

3. **Test Digital Marketing Persona**:
   ```bash
   python main.py --persona digital_marketing
   ```
   - Ask: "What are effective social media strategies?"
   - Expected: Should return marketing strategy information only
   - Verify: Response uses creative, engaging tone

### Test 2: Streamlit UI Interface

1. **Start Streamlit**:
   ```bash
   streamlit run streamlit_app.py
   ```

2. **Test Persona Switching**:
   - Open http://localhost:8501
   - Check sidebar for "👤 Persona Settings"
   - Verify dropdown shows all personas: mugdha, praveen, real_estate, digital_marketing, default
   - Select "mugdha" persona
   - Verify "Active Collections" shows: therapy_docs
   - Verify "Prompt Style" shows: gentle

3. **Test Cross-Persona Queries**:
   - With "mugdha" persona selected, ask: "What are real estate trends?"
   - Expected: Should say no relevant information found (different persona's data)
   - Switch to "real_estate" persona
   - Ask same question: "What are real estate trends?"
   - Expected: Should return relevant real estate information

### Test 3: Collection Isolation

1. **Verify Data Isolation**:
   ```bash
   # Test with mugdha persona
   python main.py --persona mugdha
   ```
   - Ask: "Tell me about digital marketing"
   - Expected: No relevant information (should not access marketing docs)

2. **Test Multi-Collection Access**:
   ```bash
   # Test with praveen persona (has multiple collections)
   python main.py --persona praveen
   ```
   - Should search across both "enterprise_docs" and "core_docs" collections

### Test 4: Prompt Style Verification

1. **Gentle Style (Mugdha)**:
   - Ask about health topics
   - Verify response is warm, supportive, empathetic

2. **Professional Style (Real Estate)**:
   - Ask about property investment
   - Verify response is business-focused, data-driven

3. **Creative Style (Digital Marketing)**:
   - Ask about marketing campaigns
   - Verify response is engaging, innovative, trend-focused

## Expected Results

### Successful Test Indicators:
- ✅ Each persona loads only its specific documents
- ✅ Persona switching works in both CLI and UI
- ✅ Collections are isolated (no cross-persona data leakage)
- ✅ Prompt styles are applied correctly
- ✅ Active collections display correctly in UI
- ✅ Last used persona is remembered

### Troubleshooting:

1. **"No relevant information found"**:
   - Check if documents exist in correct persona directory
   - Verify FORCE_REINDEX=true was set
   - Run setup.py to reindex documents

2. **Wrong persona data showing**:
   - Check persona_config.json for correct data_dir paths
   - Verify documents are in correct folders
   - Restart application after adding new documents

3. **Collections not switching**:
   - Check ChromaDB connection
   - Verify persona_config.json is valid JSON
   - Check console logs for initialization errors

## Validation Checklist

- [ ] All 5 personas load successfully
- [ ] Each persona accesses only its designated documents
- [ ] Prompt styles are applied correctly
- [ ] UI persona dropdown works
- [ ] CLI --persona argument works
- [ ] Collections are properly isolated
- [ ] Last used persona is remembered
- [ ] Cross-persona queries return "no information found"
- [ ] Multi-collection personas (praveen) search all assigned collections

## Test Completion

Document test results with:
- Persona used
- Query asked
- Response received
- Tone/style verification
- Any issues encountered

This ensures the persona-based collection switching is working correctly across all use cases.
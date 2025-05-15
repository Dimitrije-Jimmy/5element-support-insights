# Support Analytics System with LLM-powered Chatbot

A support message analytics system with natural language querying capabilities, built as part of the 5Element technical assessment. The system analyzes customer support messages from LiveChat and Telegram, providing insights through a modern web interface.

## Current State & Limitations

### Data Classification

- Currently using DistilBERT for message classification into 7 categories:
  - bonus
  - deposit
  - withdraw
  - game_issue
  - login_account
  - anger_feedback
  - other
- **Known Issues:**
  - Categories are too broad and need refinement
  - Single-label classification misses multi-issue messages
  - "other" category catches too many specific issues
  - Model needs retraining with more diverse data

### LLM Chatbot

- Uses OpenAI/Gemini for natural language understanding
- **Current Problems:**
  - Occasional hallucination of statistics
  - Sometimes ignores date range constraints
  - Responses can be inconsistent in length/detail
  - Context retention needs improvement
  - Tool schema could be more robust

### Frontend

- Built with React + TypeScript
- Features:
  - Real-time chat interface
  - Message statistics dashboard
  - Category filtering
  - Date range selection
- **Areas for Improvement:**
  - Better error handling
  - Loading states
  - Mobile responsiveness
  - Data visualization
  - Real-time updates

## Setup Instructions

### Prerequisites

```bash
# Python 3.10+ required
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt
npm install  # in frontend directory
```

### Environment Variables

Create `.env` file in backend directory:

```env
OPENAI_API_KEY=your_key_here  # or
GEMINI_API_KEY=your_key_here
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### Database Setup

1. Create Supabase project
2. Run migration:

```bash
cd backend/scripts
python setup_supabase.sql
```

### Training the Classifier

```bash
cd backend/training
python train_distilbert.py --data_path ../data/messages.csv --epochs 5 --batch_size 32
```

The trained model will be saved to `backend/models/distilbert_classifier/`

### Running Locally

```bash
# Backend
cd backend
uvicorn app.main:app --reload

# Frontend
cd frontend
npm run dev
```

### Deployment

#### Backend (fly.io)

```bash
flyctl launch
flyctl deploy
```

#### Frontend (Cloudflare Pages)

1. Connect your GitHub repository
2. Configure build settings:
   - Build command: `npm run build`
   - Output directory: `dist`
3. Add environment variables from `.env`

## Architecture

### Backend

- FastAPI for API endpoints
- Supabase for data storage
- DistilBERT for message classification
- OpenAI/Gemini for natural language understanding

### Frontend Architecture

- React + TypeScript
- TailwindCSS for styling
- shadcn/ui components

## Needed Improvements

### Short Term

1. **Data Quality**
   - Refine classification categories
   - Add multi-label classification
   - Improve training data diversity

2. **LLM Integration**
   - Better prompt engineering
   - Stricter validation of responses
   - Improved context management
   - Add streaming responses

3. **Frontend**
   - Add proper error boundaries
   - Improve loading states
   - Add data export
   - Better mobile support

### Long Term

1. **Architecture**
   - Add message queue for async processing
   - Implement caching layer
   - Add rate limiting
   - Improve error logging

2. **Features**
   - Sentiment analysis
   - User feedback collection
   - Custom category creation
   - Advanced analytics
   - Automated alerts

3. **Integration**
   - Direct LiveChat/Telegram integration
   - Real-time processing
   - Automated responses
   - Ticket creation

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Model Files Handling

### For Contributors

The DistilBERT model files are large and shouldn't be committed to Git. Instead:

1. After training, upload the model files to cloud storage (e.g., S3, GCS)
2. Update the URLs in `backend/scripts/download_model.py`
3. Commit the updated script

### For Users

To get the model files:

```bash
# Option 1: Download pre-trained model
python backend/scripts/download_model.py

# Option 2: Train your own
python backend/training/train_distilbert.py --data_path ../data/messages.csv
```

### Git Setup for Large Files

If you need to work with the model files locally:

1. Add to `.gitignore`:

```bash
backend/models/distilbert_classifier/model.safetensors
backend/models/distilbert_classifier/*.bin
backend/models/distilbert_classifier/tokenizer.json
```

2. Initial repository setup:

```bash
# Initialize repository
git init

# Add and commit files (model files will be ignored)
git add .
git commit -m "Initial commit"

# Add remote and push
git remote add origin your-repo-url
git push -u origin main
```

3. Working with the repository:

```bash
# Clone repository
git clone your-repo-url

# Download model files
python backend/scripts/download_model.py

# Continue development...
```

Note: If you need to track large files in Git, consider using Git LFS (Large File Storage).

## Evaluation & Technical Details

### Message Classification Methodology

We use a hybrid approach combining DistilBERT with rule-based post-processing:

- **Base Model**: Fine-tuned DistilBERT for initial classification
- **Advantages**:
  - Fast inference time compared to larger models
  - Good performance on known categories
  - Relatively small model size
- **Drawbacks**:
  - Single-label classification misses multi-issue messages
  - Limited to training categories
- **Handling New Issues**:
  - Currently falls back to "other" category
  - Could be improved by:
    - Implementing zero-shot classification
    - Adding regular retraining pipeline
    - Using embeddings similarity for new category detection

### Conversational Context Management

Current implementation uses a simple memory dict with limitations:

```python
_memory: Dict[str, Dict[str, Any]] = {}  # keyed by user-id
```

- Stores last used filters (category, source, timeframe)
- **Limitations**:
  - No persistence across restarts
  - Basic key-value storage
  - No complex context understanding
- **Improvement Opportunities**:
  - Implement proper session management
  - Add Redis/PostgreSQL for persistence
  - Use vector embeddings for semantic memory

### System Limitations

1. **Classification Issues**:
   - Broad categories miss nuanced issues
   - No multi-label support
   - Limited handling of edge cases

2. **LLM Integration**:
   - Occasional hallucination in responses
   - Inconsistent adherence to date constraints
   - Basic prompt engineering

3. **Technical Debt**:
   - No proper test coverage
   - Limited error handling
   - Basic monitoring

4. **Data Processing**:
   - No real-time processing
   - Limited data validation
   - Basic analytics only

### Proposed Improvements

1. **Short-term**:
   - Implement multi-label classification
   - Add proper validation layer for LLM responses
   - Improve prompt engineering
   - Add basic monitoring

2. **Long-term**:
   - Move to streaming architecture
   - Implement proper observability
   - Add automated retraining pipeline
   - Develop custom fine-tuning approach

### Query Refinement Process

Current implementation:

1. Extracts filters from query using LLM
2. Merges with previous context
3. Fetches filtered data
4. Generates response

Could be improved by:

- Adding query vector embeddings
- Implementing semantic search
- Adding conversation summarization
- Proper context window management

### Full Conversation Approach

With full conversation context, we would:

1. Use conversation flow for better classification
2. Extract resolution patterns
3. Implement solution recommendation
4. Add automated quality scoring
5. Build conversation flow analytics

### Classification Validation

Current metrics:

- Basic accuracy/precision/recall
- Manual spot checks
- Error logging

Needed improvements:

1. **Automated Testing**:
   - Golden dataset creation
   - Regular evaluation pipeline
   - Regression testing

2. **Quality Metrics**:
   - Inter-annotator agreement
   - Confidence scoring
   - Edge case detection

3. **Monitoring**:
   - Classification drift detection
   - Error pattern analysis
   - Performance degradation alerts

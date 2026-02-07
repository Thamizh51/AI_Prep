# Setting up Environment Variables

## Groq API Key Setup

The AI_Prep project uses the Groq API for generating interview questions and feedback. You need to set up your API key to use the interview features.

### Step 1: Get Your API Key

1. Visit [Groq Console](https://console.groq.com/keys)
2. Sign up or log in to your account
3. Create a new API key
4. Copy the API key (keep it secure!)

### Step 2: Set Up Locally

#### Option 1: Using .env file (Recommended for Development)

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```

2. Open `.env` and add your API key:
   ```
   GROQ_API_KEY=your_actual_api_key_here
   ```

#### Option 2: Using Environment Variables (Windows)

Set the environment variable in your terminal session:
```powershell
$env:GROQ_API_KEY="your_actual_api_key_here"
```

Or set it permanently in Windows:
1. Search for "Environment Variables" in Windows
2. Click "Environment Variables" button
3. Under "User variables", click "New"
4. Variable name: `GROQ_API_KEY`
5. Variable value: your actual API key
6. Click OK

### Step 3: For Production (Render)

When deploying to Render:

1. Go to your Render dashboard
2. Select your web service
3. Go to "Environment" tab
4. Add a new environment variable:
   - Key: `GROQ_API_KEY`
   - Value: your actual API key
5. Save changes

The app will automatically use the environment variable in production.

## Verification

After setting up the API key, restart your Django development server:

```bash
python manage.py runserver
```

The interview features should now work without the "GROQ_API_KEY" error!

## Security Notes

⚠️ **NEVER** commit your `.env` file or expose your API key in your code!
- `.env` is already in `.gitignore`
- Always use environment variables for sensitive data
- Rotate your API key if it's accidentally exposed

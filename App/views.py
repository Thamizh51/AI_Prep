from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from .models import Interview
from django.db.models import Avg, Count
from datetime import datetime, timedelta
import json
import re
import requests
# Create your views here.

def index(request):
    if request.user.is_authenticated:
        # Get interview statistics
        interviews = Interview.objects.filter(user=request.user)
        total_interviews = interviews.count()
        
        # Calculate average score
        avg_score = interviews.aggregate(Avg('score'))['score__avg']
        avg_score = round(avg_score, 1) if avg_score else 0
        
        # Get recent interviews (last 5)
        recent_interviews = interviews[:5]
        
        # Calculate streak (consecutive days with interviews)
        streak = 0
        if total_interviews > 0:
            today = datetime.now().date()
            current_date = today
            while True:
                day_interviews = interviews.filter(created_at__date=current_date)
                if day_interviews.exists():
                    streak += 1
                    current_date -= timedelta(days=1)
                else:
                    break
        
        context = {
            'total_interviews': total_interviews,
            'avg_score': avg_score,
            'streak': streak,
            'recent_interviews': recent_interviews,
        }
        return render(request, 'home.html', context)
    return render(request, 'home.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        values = {'email': email}
        
        # Try to find user by email first to support email-based login
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            errors = {'password': 'Invalid email or password'}
            return render(request, 'login.html', {'values': values, 'errors': errors})
            
    return render(request, 'login.html')

def signup(request):

    if request.method == 'POST':
        name = request.POST.get('fullname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        
        values = {
            'fullname': name,
            'email': email
        }

        if User.objects.filter(email=email).exists():
            errors = {'email': 'Email already exists'}
            return render(request, 'signup.html', {'values': values, 'errors': errors})
            
        if password != confirm_password:
            errors = {'password': 'Passwords do not match'}
            return render(request, 'signup.html', {'values': values, 'errors': errors})
        
        try:
            user = User.objects.create_user(username=name, email=email, password=password)
            user.save()
            messages.success(request, 'Account created successfully')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Error creating account: {e}')
            return render(request, 'signup.html', {'values': values})
            
    return render(request, 'signup.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def start_interview(request):
    role = request.GET.get('role', '')
    return render(request, 'start_interview.html', {'role': role})

def about(request):
    return render(request, 'about.html')

def mock_interviews(request):
    return render(request, 'mock_interviews.html')

@login_required
def interview_chat(request):
    return render(request, 'interview_chat.html')

@login_required
def interview_review(request, interview_id):
    """Display interview review page"""
    try:
        interview = Interview.objects.get(id=interview_id, user=request.user)
        
        # Parse strengths and improvements from JSON
        strengths_list = []
        improvements_list = []
        
        if interview.strengths:
            try:
                strengths_list = json.loads(interview.strengths)
            except:
                strengths_list = [interview.strengths] if interview.strengths else []
        
        if interview.improvements:
            try:
                improvements_list = json.loads(interview.improvements)
            except:
                improvements_list = [interview.improvements] if interview.improvements else []
        
        context = {
            'interview': interview,
            'strengths_list': strengths_list,
            'improvements_list': improvements_list,
        }
        return render(request, 'interview_review.html', context)
    except Interview.DoesNotExist:
        messages.error(request, 'Interview not found.')
        return redirect('home')

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def interview_chat_api(request):
    try:
        data = json.loads(request.body)
        messages = data.get('messages', [])
        
        if not messages:
            return JsonResponse({'error': 'Messages are required'}, status=400)
        
        headers = {
            'Authorization': f'Bearer {settings.GROQ_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'llama-3.1-8b-instant',  # Powerful Groq model (updated from deprecated llama-3.1-70b-versatile)
            'messages': messages,
            'temperature': 0.7,
            'max_tokens': 2000
        }
        
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            return JsonResponse({'response': ai_response})
        else:
            error_data = response.json() if response.content else {}
            error_message = error_data.get('error', {}).get('message', 'Unknown error occurred')
            return JsonResponse({'error': f'API Error: {error_message}'}, status=response.status_code)
            
    except requests.exceptions.Timeout:
        return JsonResponse({'error': 'Request timeout. Please try again.'}, status=504)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': f'Network error: {str(e)}'}, status=500)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def interview_review_api(request):
    """Generate AI review and save interview data"""
    try:
        data = json.loads(request.body)
        conversation_history = data.get('conversation', [])
        role = data.get('role', '')
        technology = data.get('technology', '')
        difficulty = data.get('difficulty', 'mid')
        focus = data.get('focus', 'balanced')
        persona = data.get('persona', 'neutral')
        
        if not conversation_history:
            return JsonResponse({'error': 'Conversation history is required'}, status=400)
        
        # Prepare review prompt for AI
        review_prompt = f"""You are an expert interview evaluator. Review the following interview conversation and provide:

1. A comprehensive review (2-3 paragraphs)
2. A score out of 100 (consider: technical knowledge, communication, problem-solving, clarity)
3. Top 3 strengths
4. Top 3 areas for improvement

Interview Details:
- Role: {role}
- Technology: {technology or 'General'}
- Difficulty Level: {difficulty}
- Focus: {focus}

Format your response as JSON:
{{
    "review": "Your comprehensive review here...",
    "score": 85,
    "strengths": ["Strength 1", "Strength 2", "Strength 3"],
    "improvements": ["Improvement 1", "Improvement 2", "Improvement 3"]
}}

Conversation:
{json.dumps(conversation_history, indent=2)}

Provide only the JSON response, no additional text."""

        # Call Groq API for review
        headers = {
            'Authorization': f'Bearer {settings.GROQ_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'llama-3.1-8b-instant',
            'messages': [
                {'role': 'system', 'content': 'You are an expert interview evaluator. Always respond with valid JSON only.'},
                {'role': 'user', 'content': review_prompt}
            ],
            'temperature': 0.3,
            'max_tokens': 2000
        }
        
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            
            # Parse AI response (try to extract JSON)
            try:
                # Try to find JSON in the response
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    review_data = json.loads(json_match.group())
                else:
                    # Fallback if no JSON found
                    review_data = {
                        'review': ai_response,
                        'score': 75,
                        'strengths': ['Good communication', 'Clear thinking', 'Technical knowledge'],
                        'improvements': ['Could improve depth', 'More examples needed', 'Better structure']
                    }
            except:
                # Fallback if parsing fails
                review_data = {
                    'review': ai_response,
                    'score': 75,
                    'strengths': ['Good communication', 'Clear thinking', 'Technical knowledge'],
                    'improvements': ['Could improve depth', 'More examples needed', 'Better structure']
                }
            
            # Save interview to database
            interview = Interview.objects.create(
                user=request.user,
                role=role,
                technology=technology,
                difficulty=difficulty,
                focus=focus,
                persona=persona,
                conversation=json.dumps(conversation_history),
                ai_review=review_data.get('review', ''),
                score=review_data.get('score', 75),
                strengths=json.dumps(review_data.get('strengths', [])),
                improvements=json.dumps(review_data.get('improvements', []))
            )
            
            return JsonResponse({
                'success': True,
                'review': review_data.get('review', ''),
                'score': review_data.get('score', 75),
                'strengths': review_data.get('strengths', []),
                'improvements': review_data.get('improvements', []),
                'interview_id': interview.id
            })
        else:
            error_data = response.json() if response.content else {}
            error_message = error_data.get('error', {}).get('message', 'Unknown error occurred')
            return JsonResponse({'error': f'API Error: {error_message}'}, status=response.status_code)
            
    except requests.exceptions.Timeout:
        return JsonResponse({'error': 'Request timeout. Please try again.'}, status=504)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': f'Network error: {str(e)}'}, status=500)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)

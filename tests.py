from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from gameplay.models import Department, Question, QuizResult

class DepartmentTests(TestCase):
    def setUp(self):
        # 1. Create a test user
        self.user = User.objects.create_user(username='testuser', password='password123')
        
        # 2. Create a test department
        self.department = Department.objects.create(
            name="IT Department",
            description="Tech support",
            video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )
        
        # 3. Create a test question
        self.question = Question.objects.create(
            department=self.department,
            text="What is Python?",
            option_1="Snake",
            option_2="Language",
            option_3="Car",
            correct_option="2"
        )

    def test_department_model(self):
        """Test if department is created correctly"""
        self.assertEqual(self.department.name, "IT Department")
        self.assertEqual(str(self.department), "IT Department")

    def test_department_page_loads(self):
        """Test if the department page loads (requires login)"""
        self.client.login(username='testuser', password='password123')
        
        # Get the page
        response = self.client.get(reverse('department_detail', args=[self.department.id]))
        
        # Check if status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        
        # Check if department name is on the page
        self.assertContains(response, "IT Department")

    def test_quiz_submission(self):
        """Test submitting a quiz answer"""
        self.client.login(username='testuser', password='password123')
        
        # Simulate posting a correct answer
        response = self.client.post(reverse('take_department_quiz', args=[self.department.id]), {
            f'question_{self.question.id}': '2'  # Correct option
        })
        
        # Check if result was saved
        result = QuizResult.objects.filter(user=self.user, department=self.department).first()
        self.assertIsNotNone(result)
        self.assertEqual(result.score, 1)  # 1 correct answer
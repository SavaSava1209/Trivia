import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)

  @app.after_request
  def after_request(response): 
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
      return response
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    categories = Category.query.order_by(Category.type).all()
    formatted_categories = {category.id: category.type for category in categories}

    if len(formatted_categories) == 0:
      abort(404)
    
    return jsonify({
      "success": True,
      'categories': formatted_categories
    })
    


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  def pagination(req, selections):
    showing_pages = 10
    page = req.args.get('page', 1, type=int)
    start = (page - 1) * showing_pages
    end = start + showing_pages
    return selections[start: end]

  @app.route('/questions')
  def get_questions():
    
      selections = Question.query.order_by(Question.id).all()
      questions = pagination(request, selections)
      formatted_questions = [question.format() for question in questions]

      categories = Category.query.order_by(Category.id).all()
      formatted_categories = {category.id: category.type for category in categories}

      if len(questions) == 0:
        abort(404)

      return jsonify({
        "success": True,
        "questions": formatted_questions,
        "totalQuestions": len(formatted_questions),
        "categories": formatted_categories,
        "currentCategory": None
      })
    

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()     

      question.delete()

      return jsonify({
        "success": True,
      })

    except:
      abort(404)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  
  @app.route("/questions", methods=['POST'])
  def create_question():
    body = request.get_json()

    question = body.get('question', None)
    answer = body.get('answer', None)
    difficulty = body.get('difficulty', None)
    category = body.get('category', None)

    if question is None or answer is None or difficulty is None or category is None:
      abort(422)

    try:
      question = Question(question=question, answer=answer, difficulty=difficulty, category=category)
      question.insert()

      return jsonify({
          'success': True,
          'created': question.id,
      })

    except:
      abort(422)


  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    body = request.get_json()
    search_term = body.get('searchTerm')

    if search_term:   
      questions = Question.query.filter(Question.question.ilike(f"%{search_term}%")).all()

      formatted_questions = [question.format() for question in questions]

      return jsonify({
        "success": True,
        'questions': formatted_questions,
        'totalQuestions': len(formatted_questions),
        'currentCategory': None
      })
    else:
      abort(404)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def get_questions_by_category(category_id):

    try:
      questions = Question.query.filter(Question.category == category_id).all()
      category = Category.query.filter(Category.id == category_id).one_or_none()
      formatted_questions = [question.format() for question in questions]
      if len(questions) == 0:
        abort(404)

      return jsonify({
        "success": True,
        "questions": formatted_questions,
        "totalQuestions": len(questions),
        "currentCategory": category_id
      })
    except:
      abort(422)


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=["POST"])
  def get_quiz_by_category():
    try:
      body = request.get_json()
      # a list
      previous_questions = body.get('previous_questions', None)
      # an object
      quiz_category = body.get('quiz_category', None)

      if previous_questions is None or quiz_category is None:
        abort(422)

     
      # {'previous_questions': [], 'quiz_category': {'type': 'click', 'id': 0}}
      # {'type': 'click', 'id': 0}
      print(previous_questions)
      # when category is all
      if quiz_category['type'] == 'click':
        # notin_ mean not in 
        questions = Question.query.all()
      else:
        questions = Question.query.filter(Question.category == quiz_category['id']).all()
      
      random_num = random.randrange(len(questions))
      next_question = questions[random_num].format()
      question_id = next_question['id']

      while question_id in previous_questions:
        random_num = random.randrange(len(questions))
        next_question = questions[random_num].format()
        question_id = next_question['id']

      return jsonify({
          'success': True,
          'question': next_question
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404, 
      "message": "not found"
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      'error': 422,
      "message": 'unprocessable'
    }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400, 
      "message": "bad request"
    }), 400

  @app.errorhandler(500)
  def internet_server_error(error):
    return jsonify({
      "success": False, 
      "error": 500, 
      "message": "internet server error"
    }), 500


  return app

    
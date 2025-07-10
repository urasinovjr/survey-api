from fastapi import HTTPException
from sqlalchemy.orm import Session
from repositories.response import ResponseRepository
from repositories.question import QuestionRepository
from schemas.response import ResponseCreate, ResponseUpdate
from models.question import Question
import json
import logging
from copy import deepcopy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResponseService:
    def __init__(self, db: Session):
        self.repo = ResponseRepository(db)
        self.question_repo = QuestionRepository(db)

    def create_response(self, response: ResponseCreate):
        question = self.question_repo.get_question(response.question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")

        constraints = json.loads(question.constraints) if question.constraints else {}
        options = json.loads(question.options) if question.options else {"values": []}

        self.validate_response(response.response_value, question.type, constraints, options, response.user_id, response.version_id, question.number)

        if question.number in ["2.1.1", "2.2.1", "2.3.1"]:
            self.validate_corpus_selection(response, question, constraints)
        elif question.number.startswith("6."):
            self.validate_apartment_area(response, question, constraints)
        elif question.number == "2.1.22":
            self.validate_lifts(response, question, constraints)
        elif question.number.startswith("4.") and "depends_on" in constraints:
            self.validate_dependency(response, question, constraints)
        elif question.number in ["5.1", "5.4"]:
            self.validate_totals(response, question, constraints)
        elif question.number == "2.1.9":
            self.validate_parking(response, question, constraints)
        elif question.number in ["3.6.рд.св.кор", "3.8.рд.св.кор"]:
            self.calculate_fire_params(response, question, constraints)

        db_response = self.repo.create_response(response)
        logger.info(f"Created response for user {response.user_id}, question {response.question_id}")
        return db_response

    def validate_response(self, value, q_type: str, constraints: dict, options: dict, user_id: int, version_id: int, question_number: str):
        if q_type == "integer":
            if not isinstance(value, int):
                raise HTTPException(status_code=400, detail="Response must be an integer")
            min_val = constraints.get("min")
            max_val = constraints.get("max")
            if min_val is not None and value < min_val:
                raise HTTPException(status_code=400, detail=f"Value must be >= {min_val}")
            if max_val is not None and value > max_val:
                raise HTTPException(status_code=400, detail=f"Value must be <= {max_val}")
            max_ref = constraints.get("max_ref")
            if max_ref:
                ref_question = self.question_repo.get_question_by_number(version_id, max_ref)
                if ref_question:
                    ref_response = self.repo.get_response_by_user_and_question(user_id, version_id, ref_question.id)
                    if ref_response and value > ref_response.response_value:
                        raise HTTPException(status_code=400, detail=f"Value must be <= {max_ref} ({ref_response.response_value})")
            max_ref_percent = constraints.get("max_ref_percent")
            if max_ref_percent:
                ref_question = self.question_repo.get_question_by_number(version_id, max_ref_percent["ref"])
                if ref_question:
                    ref_response = self.repo.get_response_by_user_and_question(user_id, version_id, ref_question.id)
                    if ref_response:
                        max_allowed = ref_response.response_value * (max_ref_percent["percent"] / 100)
                        if value > max_allowed:
                            raise HTTPException(status_code=400, detail=f"Value must be <= {max_ref_percent['percent']}% of {max_ref_percent['ref']} ({max_allowed})")
        elif q_type == "dropdown":
            if value not in options["values"]:
                raise HTTPException(status_code=400, detail=f"Value must be one of {options['values']}")
        elif q_type == "boolean":
            if not isinstance(value, bool):
                raise HTTPException(status_code=400, detail="Response must be a boolean")
        elif q_type == "text":
            if not isinstance(value, str):
                raise HTTPException(status_code=400, detail="Response must be a string")
        if constraints.get("read_only") and question_number in ["3.6.рд.св.кор", "3.7.рд.св.кор", "3.8.рд.св.кор"]:
            raise HTTPException(status_code=400, detail="This parameter is read-only")

    def validate_corpus_selection(self, response: ResponseCreate, question: Question, constraints: dict):
        question_2_1 = self.question_repo.get_question_by_number(response.version_id, "2.1")
        if not question_2_1:
            raise HTTPException(status_code=400, detail="Question 2.1 not found")
        response_2_1 = self.repo.get_response_by_user_and_question(response.user_id, response.version_id, question_2_1.id)
        if not response_2_1:
            raise HTTPException(status_code=400, detail="Response for 2.1 required")

        num_corps = response_2_1.response_value
        valid_options = [f"К.{i}" for i in range(1, num_corps + 1)]
        if response.response_value not in valid_options:
            raise HTTPException(status_code=400, detail=f"Value must be one of {valid_options}")

        if question.number == "2.1.1" and response_2_1.response_value <= 1:
            raise HTTPException(status_code=400, detail="Question 2.1.1 requires 2.1 > 1")
        if question.number == "2.2.1":
            question_2_2 = self.question_repo.get_question_by_number(response.version_id, "2.2")
            if question_2_2:
                response_2_2 = self.repo.get_response_by_user_and_question(response.user_id, response.version_id, question_2_2.id)
                if not response_2_2 or response_2_2.response_value == 0:
                    raise HTTPException(status_code=400, detail="Question 2.2.1 requires 2.2 > 0")
        if question.number == "2.3.1":
            question_2_3 = self.question_repo.get_question_by_number(response.version_id, "2.3")
            if question_2_3:
                response_2_3 = self.repo.get_response_by_user_and_question(response.user_id, response.version_id, question_2_3.id)
                if not response_2_3 or response_2_3.response_value == 0:
                    raise HTTPException(status_code=400, detail="Question 2.3.1 requires 2.3 > 0")

        other_questions = [q for q in ["2.1.1", "2.2.1", "2.3.1"] if q != question.number]
        for other_q in other_questions:
            other_question = self.question_repo.get_question_by_number(response.version_id, other_q)
            if other_question:
                other_response = self.repo.get_response_by_user_and_question(response.user_id, response.version_id, other_question.id)
                if other_response and other_response.response_value == response.response_value:
                    raise HTTPException(status_code=400, detail=f"Corpus already selected in {other_q}")

    def validate_apartment_area(self, response: ResponseCreate, question: Question, constraints: dict):
        area_check = constraints.get("area_check")
        if area_check:
            min_area = area_check["min_area"]
            max_area = area_check["max_area"]
            if response.response_value < 0:
                raise HTTPException(status_code=400, detail="Number of apartments must be >= 0")
            question_2_1_4 = self.question_repo.get_question_by_number(response.version_id, "2.1.4")
            if question_2_1_4:
                response_2_1_4 = self.repo.get_response_by_user_and_question(response.user_id, response.version_id, question_2_1_4.id)
                if response_2_1_4:
                    total_area = response_2_1_4.response_value
                    estimated_area = response.response_value * max_area
                    if estimated_area > total_area:
                        raise HTTPException(status_code=400, detail=f"Total area for {question.number} exceeds 2.1.4 ({total_area} m²)")

    def validate_lifts(self, response: ResponseCreate, question: Question, constraints: dict):
        question_2_1_2 = self.question_repo.get_question_by_number(response.version_id, "2.1.2")
        question_2_1_4 = self.question_repo.get_question_by_number(response.version_id, "2.1.4")
        if question_2_1_2 and question_2_1_4:
            response_2_1_2 = self.repo.get_response_by_user_and_question(response.user_id, response.version_id, question_2_1_2.id)
            response_2_1_4 = self.repo.get_response_by_user_and_question(response.user_id, response.version_id, question_2_1_4.id)
            if response_2_1_2 and response_2_1_4:
                floors = response_2_1_2.response_value
                area = response_2_1_4.response_value
                lifts = response.response_value
                if floors <= 9 and area > 600 and lifts != 1:
                    raise HTTPException(status_code=400, detail="For up to 9 floors, area must be <= 600 m² for 1 lift")
                elif 10 <= floors <= 12 and area > 600 and lifts != 2:
                    raise HTTPException(status_code=400, detail="For 10-12 floors, area must be <= 600 m² for 2 lifts")
                elif 13 <= floors <= 17 and area > 450 and lifts != 2:
                    raise HTTPException(status_code=400, detail="For 13-17 floors, area must be <= 450 m² for 2 lifts")
                elif 20 <= floors <= 25 and area > 350 and lifts == 3:
                    raise HTTPException(status_code=400, detail="For 20-25 floors, area must be <= 350 m² for 3 lifts")
                elif 20 <= floors <= 25 and area > 450 and lifts == 4:
                    raise HTTPException(status_code=400, detail="For 20-25 floors, area must be <= 450 m² for 4 lifts")

    def validate_dependency(self, response: ResponseCreate, question: Question, constraints: dict):
        depends_on = constraints.get("depends_on")
        condition = constraints.get("condition")
        if depends_on:
            dep_question = self.question_repo.get_question_by_number(response.version_id, depends_on)
            if dep_question:
                dep_response = self.repo.get_response_by_user_and_question(response.user_id, response.version_id, dep_question.id)
                if not dep_response:
                    raise HTTPException(status_code=400, detail=f"Response for {depends_on} required")
                if condition == "True" and not dep_response.response_value:
                    raise HTTPException(status_code=400, detail=f"Question {question.number} requires {depends_on} to be True")
                elif condition == ">0" and dep_response.response_value == 0:
                    raise HTTPException(status_code=400, detail=f"Question {question.number} requires {depends_on} > 0")

    def validate_totals(self, response: ResponseCreate, question: Question, constraints: dict):
        if question.number == "5.1":
            area_questions = ["2.1.4", "2.1.5", "2.1.7", "2.1.8"]
            total_area = 0
            for q_num in area_questions:
                q = self.question_repo.get_question_by_number(response.version_id, q_num)
                if q:
                    resp = self.repo.get_response_by_user_and_question(response.user_id, response.version_id, q.id)
                    if resp:
                        total_area += resp.response_value
            if response.response_value < total_area:
                raise HTTPException(status_code=400, detail=f"Total area (5.1) must be >= sum of {area_questions} ({total_area} m²)")
        
        elif question.number == "5.4":
            apartment_questions = [f"6.{i}" for i in range(1, 6)]
            total_apartments = 0
            for q_num in apartment_questions:
                q = self.question_repo.get_question_by_number(response.version_id, q_num)
                if q:
                    resp = self.repo.get_response_by_user_and_question(response.user_id, response.version_id, q.id)
                    if resp:
                        total_apartments += resp.response_value
            if response.response_value != total_apartments:
                raise HTTPException(status_code=400, detail=f"Total apartments (5.4) must equal sum of {apartment_questions} ({total_apartments})")

    def validate_parking(self, response: ResponseCreate, question: Question, constraints: dict):
        question_2_1_10 = self.question_repo.get_question_by_number(response.version_id, "2.1.10")
        if question_2_1_10:
            response_2_1_10 = self.repo.get_response_by_user_and_question(response.user_id, response.version_id, question_2_1_10.id)
            if response.response_value > 0 and (not response_2_1_10 or response_2_1_10.response_value == 0):
                raise HTTPException(status_code=400, detail="Parking spaces (2.1.9) > 0 requires underground area (2.1.10) > 0")

    def calculate_fire_params(self, response: ResponseCreate, question: Question, constraints: dict):
        question_2_1_13 = self.question_repo.get_question_by_number(response.version_id, "2.1.13")
        if question_2_1_13:
            response_2_1_13 = self.repo.get_response_by_user_and_question(response.user_id, response.version_id, question_2_1_13.id)
            if response_2_1_13:
                height = response_2_1_13.response_value
                if question.number == "3.6.рд.св.кор":
                    calculated_value = "II" if height < 50 else "I"
                    if response.response_value != calculated_value:
                        raise HTTPException(status_code=400, detail=f"Fire rating (3.6) must be {calculated_value} for height {height} m")
                elif question.number == "3.8.рд.св.кор":
                    calculated_value = (
                        "R90" if height < 50 else
                        "R120" if 50 <= height <= 75 else
                        "R150" if 75 < height <= 100 else
                        "R180" if 100 < height <= 150 else
                        "R240"
                    )
                    if response.response_value != calculated_value:
                        raise HTTPException(status_code=400, detail=f"Fire resistance (3.8) must be {calculated_value} for height {height} m")

    def get_responses(self, user_id: int, version_id: int):
        responses = self.repo.get_responses_by_user_and_version(user_id, version_id)
        for response in responses:
            question = self.question_repo.get_question(response.question_id)
            if question and question.type == "integer":
                constraints = json.loads(question.constraints) if question.constraints else {}
                if constraints.get("format") == "thousands":
                    response.response_value = f"{response.response_value:,}"
        return responses

    def get_response(self, response_id: int):
        response = self.repo.get_response(response_id)
        if not response:
            raise HTTPException(status_code=404, detail="Response not found")
        question = self.question_repo.get_question(response.question_id)
        if question and question.type == "integer":
            constraints = json.loads(question.constraints) if question.constraints else {}
            if constraints.get("format") == "thousands":
                response.response_value = f"{response.response_value:,}"
        return response

    def update_response(self, response_id: int, response_update: ResponseUpdate):
        response = self.repo.get_response(response_id)
        if not response:
            raise HTTPException(status_code=404, detail="Response not found")
        question = self.question_repo.get_question(response.question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")

        constraints = json.loads(question.constraints) if question.constraints else {}
        options = json.loads(question.options) if question.options else {"values": []}
        self.validate_response(response_update.response_value, question.type, constraints, options, response.user_id, response.version_id, question.number)

        if question.number in ["2.1.1", "2.2.1", "2.3.1"]:
            self.validate_corpus_selection(response, question, constraints)
        elif question.number.startswith("6."):
            self.validate_apartment_area(response, question, constraints)
        elif question.number == "2.1.22":
            self.validate_lifts(response, question, constraints)
        elif question.number.startswith("4.") and "depends_on" in constraints:
            self.validate_dependency(response, question, constraints)
        elif question.number in ["5.1", "5.4"]:
            self.validate_totals(response, question, constraints)
        elif question.number == "2.1.9":
            self.validate_parking(response, question, constraints)
        elif question.number in ["3.6.рд.св.кор", "3.8.рд.св.кор"]:
            self.calculate_fire_params(response, question, constraints)

        updated_response = self.repo.update_response(response_id, response_update)
        logger.info(f"Updated response {response_id}")
        return updated_response

    def delete_response(self, response_id: int):
        response = self.repo.get_response(response_id)
        if not response:
            raise HTTPException(status_code=404, detail="Response not found")
        self.repo.delete_response(response_id)
        logger.info(f"Deleted response {response_id}")